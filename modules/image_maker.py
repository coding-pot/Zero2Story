from typing import Literal
from pathlib import Path

import uuid
import json
import re
import asyncio
import toml

import torch
from compel import Compel

from diffusers import (
    DiffusionPipeline,
    StableDiffusionPipeline,
    AutoencoderKL,
    DPMSolverMultistepScheduler,
    DDPMScheduler,
    DPMSolverSinglestepScheduler,
    DPMSolverSDEScheduler,
    DEISMultistepScheduler,
)

from .utils import (
    set_all_seeds,
)
from .palmchat import (
    palm_prompts,
    gen_text,
)

_gpus = 0

class ImageMaker:
    # TODO: DocString...
    """Class for generating images from prompts."""

    __ratio = {'3:2':  [768, 512],
               '4:3':  [680, 512],
               '16:9': [912, 512],
               '1:1':  [512, 512],
               '9:16': [512, 912],
               '3:4':  [512, 680],
               '2:3':  [512, 768]}
    __allocated = False

    def __init__(self, model_base: str,
                       clip_skip: int = 2,
                       sampling: Literal['sde-dpmsolver++'] = 'sde-dpmsolver++',
                       vae: str = None,
                       safety: bool = True,
                       variant: str = None,
                       from_hf: bool = False,
                       device: str = None) -> None:
        """Initialize the ImageMaker class.

        Args:
            model_base (str): Filename of the model base.
            clip_skip (int, optional): Number of layers to skip in the clip model. Defaults to 2.
            sampling (Literal['sde-dpmsolver++'], optional): Sampling method. Defaults to 'sde-dpmsolver++'.
            vae (str, optional): Filename of the VAE model. Defaults to None.
            safety (bool, optional): Whether to use the safety checker. Defaults to True.
            variant (str, optional): Variant of the model. Defaults to None.
            from_hf (bool, optional): Whether to load the model from HuggingFace. Defaults to False.
            device (str, optional): Device to use for the model. Defaults to None.
        """

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if not device else device
        self.__model_base = model_base
        self.__clip_skip = clip_skip
        self.__sampling = sampling
        self.__vae = vae
        self.__safety = safety
        self.__variant = variant
        self.__from_hf = from_hf

        print("Loading the Stable Diffusion model into memory...")
        if not self.__from_hf:
            # from file
            self.__sd_model = StableDiffusionPipeline.from_single_file(self.model_base,
                                                                torch_dtype=torch.float16,
                                                                use_safetensors=True,
                                                                )

            # Clip Skip
            self.__sd_model.text_encoder.text_model.encoder.layers = self.__sd_model.text_encoder.text_model.encoder.layers[:12 - (self.clip_skip - 1)]

            # Sampling method
            if True: # TODO: Sampling method :: self.sampling == 'sde-dpmsolver++'
                scheduler = DPMSolverMultistepScheduler.from_config(self.__sd_model.scheduler.config)
                scheduler.config.algorithm_type = 'sde-dpmsolver++'
                self.__sd_model.scheduler = scheduler
            
            # VAE
            if self.vae:
                vae_model = AutoencoderKL.from_single_file(self.vae, use_safetensors=True)
                self.__sd_model.vae = vae_model.to(dtype=torch.float16)
            
            # Safety checker
            if not self.safety:
                self.__sd_model.safety_checker = None
                self.__sd_model.requires_safety_checker = False

        else:
            # from huggingface
            self.__sd_model = StableDiffusionPipeline.from_pretrained(self.model_base,
                                                                      variant=self.__variant,
                                                                      use_safetensors=True)
        print(f"Loaded model to {self.device}")
        self.__sd_model = self.__sd_model.to(self.device)

        # Text Encoder using Compel
        self.__compel_proc = Compel(tokenizer=self.__sd_model.tokenizer, text_encoder=self.__sd_model.text_encoder, truncate_long_prompts=False)
        
        output_dir = Path('.') / 'outputs'
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif output_dir.is_file():
            assert False, f"A file with the same name as the desired directory ('{str(output_dir)}') already exists."

    
    def text2image(self,
                   prompt: str, neg_prompt: str = None,
                   ratio: Literal['3:2', '4:3', '16:9', '1:1', '9:16', '3:4', '2:3'] = '1:1',
                   step: int = 28,
                   cfg: float = 4.5,
                   seed: int = None) -> str:
        """Generate an image from the prompt.

        Args:
            prompt (str): Prompt for the image generation.
            neg_prompt (str, optional): Negative prompt for the image generation. Defaults to None.
            ratio (Literal['3:2', '4:3', '16:9', '1:1', '9:16', '3:4', '2:3'], optional): Ratio of the generated image. Defaults to '1:1'.
            step (int, optional): Number of iterations for the diffusion. Defaults to 20.
            cfg (float, optional): Configuration for the diffusion. Defaults to 7.5.
            seed (int, optional): Seed for the random number generator. Defaults to None.

        Returns:
            str: Path to the generated image.
        """

        output_filename = Path('.') / 'outputs' / str(uuid.uuid4())

        if not seed or seed == -1:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()
        set_all_seeds(seed)

        width, height = self.__ratio[ratio]

        prompt_embeds, negative_prompt_embeds = self.__get_pipeline_embeds(prompt, neg_prompt or self.neg_prompt)
        
        # Generate the image
        result = self.__sd_model(prompt_embeds=prompt_embeds,
                              negative_prompt_embeds=negative_prompt_embeds,
                              guidance_scale=cfg,
                              num_inference_steps=step,
                              width=width,
                              height=height,
                            )
        if self.__safety and result.nsfw_content_detected[0]:
            print("=== NSFW Content Detected ===")
            raise ValueError("Potential NSFW content was detected in one or more images.")

        img = result.images[0]
        img.save(str(output_filename.with_suffix('.png')))

        return str(output_filename.with_suffix('.png'))
    

    def generate_character_prompts(self, character_name: str, age: str, job: str,
                                         keywords: list[str] = None, 
                                         creative_mode: Literal['sd character', 'cartoon', 'realistic'] = 'cartoon') -> tuple[str, str]:
        """Generate positive and negative prompts for a character based on given attributes.

        Args:
            character_name (str): Character's name.
            age (str): Age of the character.
            job (str): The profession or job of the character.
            keywords (list[str]): List of descriptive words for the character.

        Returns:
            tuple[str, str]: A tuple of positive and negative prompts.
        """

        positive = "" # add static prompt for character if needed (e.g. "chibi, cute, anime")
        negative = palm_prompts['image_gen']['neg_prompt']

        # Generate prompts with PaLM
        t = palm_prompts['image_gen']['character']['gen_prompt']
        q = palm_prompts['image_gen']['character']['query']
        query_string = t.format(input=q.format(character_name=character_name,
                                               job=job,
                                               age=age,
                                               keywords=', '.join(keywords) if keywords else 'Nothing'))
        try:
            response, response_txt = asyncio.run(asyncio.wait_for(
                                                    gen_text(query_string, mode="text", use_filter=False),
                                                    timeout=10)
                                                )
        except asyncio.TimeoutError:
            raise TimeoutError("The response time for PaLM API exceeded the limit.")
        
        try: 
            res_json = json.loads(response_txt)
            positive = (res_json['primary_sentence'] if not positive else f"{positive}, {res_json['primary_sentence']}") + ", "
            gender_keywords = ['1man', '1woman', '1boy', '1girl', '1male', '1female', '1gentleman', '1lady']
            positive += ', '.join([w if w not in gender_keywords else w + '+++' for w in res_json['descriptors']])
            positive = f'{job.lower()}+'.join(positive.split(job.lower()))
        except:
            print("=== PaLM Response ===")
            print(response.filters)
            print(response_txt)
            print("=== PaLM Response ===")            
            raise ValueError("The response from PaLM API is not in the expected format.")
            
        return (positive.lower(), negative.lower())


    def generate_background_prompts(self, genre:str, place:str, mood:str,
                                          title:str, chapter_title:str, chapter_plot:str) -> tuple[str, str]:
        """Generate positive and negative prompts for a background image based on given attributes.

        Args:
            genre (str): Genre of the story.
            place (str): Place of the story.
            mood (str): Mood of the story.
            title (str): Title of the story.
            chapter_title (str): Title of the chapter.
            chapter_plot (str): Plot of the chapter.

        Returns:
            tuple[str, str]: A tuple of positive and negative prompts.
        """

        positive = "painting+++, anime+, catoon, watercolor, wallpaper, text---" # add static prompt for background if needed (e.g. "chibi, cute, anime")
        negative = "realistic, human, character, people, photograph, 3d render, blurry, grayscale, oversaturated, " + palm_prompts['image_gen']['neg_prompt']

        # Generate prompts with PaLM
        t = palm_prompts['image_gen']['background']['gen_prompt']
        q = palm_prompts['image_gen']['background']['query']
        query_string = t.format(input=q.format(genre=genre,
                                               place=place,
                                               mood=mood,
                                               title=title,
                                               chapter_title=chapter_title,
                                               chapter_plot=chapter_plot))
        try:
            response, response_txt = asyncio.run(asyncio.wait_for(
                                                    gen_text(query_string, mode="text", use_filter=False),
                                                    timeout=10)
                                                )
        except asyncio.TimeoutError:
            raise TimeoutError("The response time for PaLM API exceeded the limit.")
        
        try: 
            res_json = json.loads(response_txt)
            positive = (res_json['primary_sentence'] if not positive else f"{positive}, {res_json['primary_sentence']}") + ", "
            positive += ', '.join(res_json['descriptors'])
        except:
            print("=== PaLM Response ===")
            print(response.filters)
            print(response_txt)
            print("=== PaLM Response ===")            
            raise ValueError("The response from PaLM API is not in the expected format.")
            
        return (positive.lower(), negative.lower())


    def __get_pipeline_embeds(self, prompt:str, negative_prompt:str) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Get pipeline embeds for prompts bigger than the maxlength of the pipeline

        Args:
            prompt (str): Prompt for the image generation.
            neg_prompt (str): Negative prompt for the image generation.

        Returns:
            tuple[torch.Tensor, torch.Tensor]: A tuple of positive and negative prompt embeds.
        """
        conditioning = self.__compel_proc.build_conditioning_tensor(prompt)
        negative_conditioning = self.__compel_proc.build_conditioning_tensor(negative_prompt)
        return self.__compel_proc.pad_conditioning_tensors_to_same_length([conditioning, negative_conditioning])


    def push_to_hub(self, repo_id:str, commit_message:str=None, token:str=None, variant:str=None):
        self.__sd_model.push_to_hub(repo_id, commit_message=commit_message, token=token, variant=variant)


    @property
    def model_base(self):
        """Model base

        Returns:
            str: The model base (read-only)
        """
        return self.__model_base

    @property
    def clip_skip(self):
        """Clip Skip

        Returns:
            int: The number of layers to skip in the clip model (read-only)
        """
        return self.__clip_skip

    @property
    def sampling(self):
        """Sampling method

        Returns:
            Literal['sde-dpmsolver++']: The sampling method (read-only)
        """
        return self.__sampling

    @property
    def vae(self):
        """VAE

        Returns:
            str: The VAE (read-only)
        """
        return self.__vae

    @property
    def safety(self):
        """Safety checker

        Returns:
            bool: Whether to use the safety checker (read-only)
        """
        return self.__safety
    
    @property
    def device(self):
        """Device

        Returns:
            str: The device (read-only)
        """
        return self.__device

    @device.setter
    def device(self, value):
        if self.__allocated:
            raise RuntimeError("Cannot change device after the model is loaded.")

        if value == 'cpu':
            self.__device = value
        else:
            global _gpus
            self.__device = f'{value}:{_gpus}'
            max_gpu = torch.cuda.device_count()
            _gpus = (_gpus + 1) if (_gpus + 1) < max_gpu else 0
        self.__allocated = True

    @property
    def neg_prompt(self):
        """Negative prompt

        Returns:
            str: The negative prompt
        """
        return self.__neg_prompt

    @neg_prompt.setter
    def neg_prompt(self, value):
        if not value:
            self.__neg_prompt = ""
        else:
            self.__neg_prompt = value

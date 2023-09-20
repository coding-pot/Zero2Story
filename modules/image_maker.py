from typing import Literal
from tempfile import NamedTemporaryFile
from pathlib import Path

import uuid
import json
import re

import torch

from diffusers import (
    StableDiffusionPipeline,
    AutoencoderKL,
    DPMSolverMultistepScheduler,
    DDPMScheduler,
    DPMSolverSinglestepScheduler,
    DPMSolverSDEScheduler,
)

import google.generativeai as palm

from .utils import (
    set_all_seeds,
    get_palm_api_key
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

    def __init__(self, model_base: str,
                       clip_skip: int = 2,
                       sampling: Literal['sde-dpmsolver++'] = 'sde-dpmsolver++',
                       vae: str = None,
                       safety: bool = True,
                       device: str = None) -> None:
        """Initialize the ImageMaker class.

        Args:
            model_base (str): Filename of the model base.
            clip_skip (int, optional): Number of layers to skip in the clip model. Defaults to 2.
            sampling (Literal['sde-dpmsolver++'], optional): Sampling method. Defaults to 'sde-dpmsolver++'.
            vae (str, optional): Filename of the VAE model. Defaults to None.
            safety (bool, optional): Whether to use the safety checker. Defaults to True.
            device (str, optional): Device to use for the model. Defaults to None.
        """

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if not device else device
        self.__model_base = model_base
        self.__clip_skip = clip_skip
        self.__sampling = sampling
        self.__vae = vae
        self.__safety = safety

        print("Loading the Stable Diffusion model into memory...")
        self.__sd_model = StableDiffusionPipeline.from_single_file(self.model_base,
                                                                   torch_dtype=torch.float16,
                                                                   custom_pipeline="lpw_stable_diffusion",
                                                                   use_safetensors=True)

        # Clip Skip
        self.__sd_model.text_encoder.text_model.encoder.layers = self.__sd_model.text_encoder.text_model.encoder.layers[:12 - (self.clip_skip - 1)]

        # Sampling method
        if True: # TODO: Sampling method :: self.sampling == 'sde-dpmsolver++'
            scheduler = DPMSolverMultistepScheduler.from_config(self.__sd_model.scheduler.config)
            scheduler.config.algorithm_type = 'sde-dpmsolver++'
            self.__sd_model.scheduler = scheduler
        
        # TODO: Use LoRA

        # VAE
        if self.vae:
            vae_model = AutoencoderKL.from_single_file(self.vae)
            self.__sd_model.vae = vae_model

        if not self.safety:
            self.__sd_model.safety_checker = None
            self.__sd_model.requires_safety_checker = False

        print(f"Loaded model to {self.device}")
        self.__sd_model = self.__sd_model.to(self.device)
        
        output_dir = Path('.') / 'outputs'
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif output_dir.is_file():
            assert False, f"A file with the same name as the desired directory ('{str(output_dir)}') already exists."

    
    def text2image(self,
                   prompt: str, neg_prompt: str = None,
                   ratio: Literal['3:2', '4:3', '16:9', '1:1', '9:16', '3:4', '2:3'] = '1:1',
                   step: int = 28,
                   cfg: float = 7,
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

        # Generate the image
        img = self.__sd_model(prompt,
                              negative_prompt=neg_prompt,
                              guidance_scale=cfg,
                              num_inference_steps=step,
                              width=width,
                              height=height,
                            ).images[0]
        img.save(str(output_filename.with_suffix('.png')))

        return str(output_filename.with_suffix('.png'))
    

    def generate_prompts_from_keywords(self, keywords: list[str], job, age, character_name) -> tuple[str, str]:
        """Generate prompts from keywords.

        Args:
            keywords (list[str]): List of keywords.
            character_name (str): Character's name.

        Returns:
            tuple[str, str]: A tuple of positive and negative prompts.
        """
        palm.configure(api_key=get_palm_api_key())
        positive = "masterpiece, best quality, dramatic, solo, "  # Add chibi, cute : Cute 3D Chracter style
        quality_prompt = ", extremely detailed, highly detailed, high budget, cinemascope, film grain, grainy, finely detailed eyes and face"
        negative = ("nsfw, worst quality, low quality, lowres, bad anatomy,bad hands, text, watermark, signature, error, missing fingers, "
                    "extra digit, fewer digits, cropped, worst quality, normal quality, blurry, username, extra limbs, "
                    "twins, boring, jpeg artifacts ")
        
        defaults = {
            'model': 'models/chat-bison-001',
            'temperature': 0.5,
            'candidate_count': 1,
            'top_k': 40,
            'top_p': 0.95,
        }
        context = ("Based on a few short sentences describing the character, recommend 'short words' that can visualize their image. "
                   "Output only the 'words' section in JSON format. Output template is as follows: {\"words\":[\"word1\",\"word2\",\"word3\"]}. "
                   "Do not output anything other than JSON values. Not exceeding 30 words.")
        examples = [
            [
                "The character's name is Catherine, their job is as a Traveler, and they are in their 10s. "
                "And the keywords that help in associating with the character are "
                "\"Romance, Starlit Bridge, Dreamy, ENTJ, Ambitious\". "
                "Print out the words in JSON format.",
                "{\"words\":[\"1girl\",\"teenage\",\"Ethereal beauty\",\"Starry-eyed\",\"Wanderlust\",\"scarf\",\"floating hair\",\"whimsical\",\"graceful poise\",\"celestial allure\",\"delicate\",\"close-up\",\"warm soft lighting\",\"luminescent glow\",\"gentle aura\",\"mystic charm\",\"smug\",\"smirk\",\"enigmatic presence\",\"serene\",\"Dreamy Landscape\",\"fantastical essence\",\"poetic demeanor\"]}"
            ],
            [
                "The character's name is Claire, their job is as a Technological Advancement, and they are in their 20s. "
                "And the keywords that help in associating with the character are "
                "\"Science Fiction, Space Station, INFP, Ambitious, Generous\". "
                "Print out the words in JSON format.",
                "{\"words\":[\"1girl\",\"twenty\",\"editorial close-up portrait\",\"cyborg\",\"sci-fi\",\"techno-savvy\",\"visionary engineer\",\"sharp focus\",\"bokeh\",\"extremely detailed\",\"intricate circuitry\",\"robotic grace\",\"rich colors\",\"vivid contrasts\",\"dramatic lighting\",\"Futuristic flair\",\"avant-garde\",\"high-tech allure\",\"Engineer with ingenuity\",\"innovative mind\",\"mechanical sophistication\",\"futuristic femme fatale\"]}"
            ],
            [
                "The character's name is Liam, their job is as a Secret Agent, and they are in their 40s. "
                "And the keywords that help in associating with the character are "
                "\"Thriller, Underground Warehouse, Darkness, ESTP, Ambitious, Generous\". "
                "Print out the words in JSON format.",
                "{\"words\":[\"1man\",\"middle-aged\",\"absurdres\",\"dramatic lighting\",\"muscular adult male\",\"chiseled physique\",\"intense brown eyes\",\"raven-black hair\",\"stylish layer cut\",\"determined gaze\",\"looking at viewer\",\"enigmatic presence\",\"secret agent with a stealthy demeanor\",\"cunning strategist\",\"advanced techwear equipped with high-tech gadgets\",\"sleek\",\"night operative\",\"shadowy figure\",\"night cinematic atmosphere\",\"under the moonlight operation\",\"mysterious and captivating aura\"]}"
            ]
        ]

        messages = [f"The character's name is {character_name}, their job is as a {job}, and they are in their {age}. " +
                    "And the keywords that help in associating with the character are " +
                    f"\"{', '.join(keywords)}\". " +
                    "Print out the words in JSON format."]
        response = palm.chat(
            **defaults,
            context=context,
            examples=examples,
            messages=messages
        )

        print('PaLM Response:', response.last)
        response.last = response.last.replace(',\n  ]\n}', '\n  ]\n}')
        try:
            positive += ', '.join(json.loads(response.last)['words'][:32])
        except:
            start, end = response.last.find('{'), response.last.rfind('}') + 1
            if end - start >= 12:
                json_str = response.last[start:end]
                positive += ', '.join(json.loads(json_str)['words'][:32])
            else:
                positive += ', '.join(re.findall(r'\*\s(\w+)', response.last.replace('**', ''))[:32])
        positive += quality_prompt

        return (positive, negative)
    
    
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
        if value == 'cpu':
            self.__device = value
        else:
            global _gpus
            self.__device = f'{value}:{_gpus}'
            max_gpu = torch.cuda.device_count()
            _gpus = (_gpus + 1) if (_gpus + 1) < max_gpu else 0

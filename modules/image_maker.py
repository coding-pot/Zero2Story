from typing import Literal
from tempfile import NamedTemporaryFile
from pathlib import Path

import uuid
import json
import re

import torch

from diffusers import StableDiffusionPipeline
from diffusers import (
    DPMSolverMultistepScheduler,
    DDPMScheduler,
    DPMSolverSinglestepScheduler,
    DPMSolverSDEScheduler
)

import google.generativeai as palm

from .utils import (
    set_all_seeds,
    get_palm_api_key
)

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
                       safety: bool = True,
                       device: str = None) -> None:
        """Initialize the ImageMaker class.

        Args:
            model_base (str): Filename of the model base.
            clip_skip (int, optional): Number of layers to skip in the clip model. Defaults to 2.
            sampling (Literal['sde-dpmsolver++'], optional): Sampling method. Defaults to 'sde-dpmsolver++'.
            safety (bool, optional): Whether to use the safety checker. Defaults to True.
            device (str, optional): Device to use for the model. Defaults to None.
        """

        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if not device else device
        self.__model_base = model_base
        self.__clip_skip = clip_skip
        self.__sampling = sampling
        self.__safety = safety

        print("Loading the Stable Diffusion model into memory...")
        self.__sd_model = StableDiffusionPipeline.from_single_file(self.model_base, torch_dtype=torch.float16, use_safetensors=True)

        # Clip Skip
        self.__sd_model.text_encoder.text_model.encoder.layers = self.__sd_model.text_encoder.text_model.encoder.layers[:12 - (self.clip_skip - 1)]

        # Sampling method
        if True: # TODO: Sampling method :: self.sampling == 'sde-dpmsolver++'
            scheduler = DPMSolverMultistepScheduler.from_config(self.__sd_model.scheduler.config)
            scheduler.config.algorithm_type = 'sde-dpmsolver++'
            self.__sd_model.scheduler = scheduler
        
        # TODO: Use LoRA

        if not self.safety:
            self.__sd_model.safety_checker = None
            self.__sd_model.requires_safety_checker = False

        if self.device != 'cpu':
            self.__sd_model = self.__sd_model.to(self.device)
        
        output_dir = Path('.') / 'outputs'
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif output_dir.is_file():
            assert False, f"A file with the same name as the desired directory ('{str(output_dir)}') already exists."

    
    def text2image(self,
                   prompt: str, neg_prompt: str = None,
                   ratio: Literal['3:2', '4:3', '16:9', '1:1', '9:16', '3:4', '2:3'] = '1:1',
                   step: int = 20,
                   cfg: float = 7.5,
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

        img = self.__sd_model(prompt,
                              negative_prompt=neg_prompt,
                              guidance_scale=cfg,
                              num_inference_steps=step,
                              width=width,
                              height=height,
                            ).images[0]
        img.save(str(output_filename.with_suffix('.png')))

        return str(output_filename.with_suffix('.png'))
    

    def generate_prompts_from_keywords(self, keywords: list[str], character_name) -> tuple[str, str]:
        """Generate prompts from keywords.

        Args:
            keywords (list[str]): List of keywords.
            character_name (str): Character's name.

        Returns:
            tuple[str, str]: A tuple of positive and negative prompts.
        """
        palm.configure(api_key=get_palm_api_key())
        positive = ''
        negative = ''

        defaults = {
            'model': 'models/chat-bison-001',
            'temperature': 0.5,
            'candidate_count': 1,
            'top_k': 40,
            'top_p': 0.95,
        }
        context = "Create a list of inspirational 'short words' based on the following 'keywords', output only the 'words' section in JSON format. Output template is as follows: {\"words\":[\"word1\",\"word2\",\"word3\"]}. Do not output anything other than JSON values."
        examples = [
            [
                "The keywords are, \"Romance, Starlit Bridge, Dreamy, teen, ENTJ, Ambitious, Traveler, Character's name is Catherine\". Print out the words in JSON format.",
                "{\"words\":[\"Ethereal beauty\",\"1girl\",\"Starry-eyed\",\"Wanderlust\",\"scarf\",\"floating hair\",\"whimsical\",\"graceful poise\",\"celestial allure\",\"delicate\",\"close-up\",\"warm soft lighting\",\"luminescent glow\",\"gentle aura\",\"mystic charm\",\"smug\",\"smirk\",\"enigmatic presence\",\"serene\",\"Dreamy Landscape\",\"fantastical essence\",\"poetic demeanor\"]}"
            ],
            [
                "The keywords are, \"Science Fiction, Space Station, Technological Advancement, 20s, INFP, Ambitious, Generous, Character's name is Claire\". Print out the words in JSON format.",
                "{\"words\":[\"1girl\",\"editorial close-up portrait\",\"cyborg\",\"sci-fi\",\"techno-savvy\",\"visionary engineer\",\"sharp focus\",\"bokeh\",\"extremely detailed\",\"intricate circuitry\",\"robotic grace\",\"rich colors\",\"vivid contrasts\",\"dramatic lighting\",\"Futuristic flair\",\"avant-garde\",\"high-tech allure\",\"Engineer with ingenuity\",\"innovative mind\",\"mechanical sophistication\",\"futuristic femme fatale\"]}"
            ],
            [
                "The keywords are, \"Thriller, Underground Warehouse, Darkness, Secret Agent, 40s, ESTP, Ambitious, Generous, Character's name is Liam\". Print out the words in JSON format.",
                "{\"words\":[\"1man\",\"absurdres\",\"dramatic lighting\",\"muscular adult male\",\"chiseled physique\",\"intense brown eyes\",\"raven-black hair\",\"stylish layer cut\",\"determined gaze\",\"looking at viewer\",\"enigmatic presence\",\"secret agent with a stealthy demeanor\",\"cunning strategist\",\"advanced techwear equipped with high-tech gadgets\",\"sleek\",\"night operative\",\"shadowy figure\",\"night cinematic atmosphere\",\"under the moonlight operation\",\"mysterious and captivating aura\"]}"
            ]
        ]

        messages = [f"The keywords are, \"{', '.join(keywords)}, Character's name is {character_name}\". Print out the words in JSON format."]
        response = palm.chat(
            **defaults,
            context=context,
            examples=examples,
            messages=messages
        )

        try:
            print(positive := ', '.join(json.loads(response.last)['words']))
        except:
            print(positive := ', '.join(re.findall(r'\*\s(\w+)', response.last)))

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

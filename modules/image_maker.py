from typing import Literal
from tempfile import NamedTemporaryFile
from pathlib import Path

import uuid

import torch

from diffusers import StableDiffusionPipeline
from diffusers import DPMSolverMultistepScheduler, DDPMScheduler, DPMSolverSinglestepScheduler, DPMSolverSDEScheduler

from utils import set_all_seeds


class ImageMaker:
    # TODO: DocString...

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

    
    def text2image(prompt: str, neg_prompt: str = None,
                   ratio: Literal['3:2', '4:3', '16:9', '1:1', '9:16', '3:4', '2:3'] = '1:1',
                   step: int = 20,
                   cfg: float = 7.5,
                   seed: int = None) -> str:
        output_filename = Path('.') / 'outputs' / str(uuid.uuid4())

        if not seed or seed == -1:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()
        set_all_seeds(seed)

        width, height = __ratio[ratio]

        img = self.__sd_model(prompt,
                              negative_prompt=neg_prompt,
                              guidance_scale=cfg,
                              num_inference_steps=step,
                              width=width,
                              height=height,
                            ).images[0]
        img.save(str(output_filename.with_suffix('.png')))

        return str(output_filename.with_suffix('.png'))
    
    
    @property
    def model_base(self):
        return self.__model_base

    @property
    def clip_skip(self):
        return self.__clip_skip

    @property
    def sampling(self):
        return self.__sampling

    @property
    def safety(self):
        return self.__safety

    @property
    def device(self):
        return self.__device

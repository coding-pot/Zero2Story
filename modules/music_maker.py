from typing import Literal
from tempfile import NamedTemporaryFile
from pathlib import Path

import uuid
import shutil

import torch

from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from pydub import AudioSegment

from .utils import set_all_seeds


class MusicMaker:
    # TODO: DocString...

    def __init__(self, model_size: Literal['small', 'medium', 'melody', 'large'] = 'large',
                       format: Literal['wav', 'mp3'] = 'mp3',
                       device: str = None) -> None:
        self.__model_size = model_size
        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if not device else device
        self.format = format

        print("Loading the MusicGen model into memory...")
        self.__mg_model = MusicGen.get_pretrained(self.model_size, device=self.device)
        self.__mg_model.set_generation_params(use_sampling=True,
                                            top_k=250,
                                            top_p=0.0,
                                            temperature=1.0,
                                            cfg_coef=3.0
                                            )
        
        output_dir = Path('.') / 'outputs'
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif output_dir.is_file():
            assert False, f"A file with the same name as the desired directory ('{str(output_dir)}') already exists."
    

    def text2music(self, prompt: str, length: int = 60, seed: int = None) -> str:
        def wavToMp3(src_file: str, dest_file: str) -> None:
            sound = AudioSegment.from_wav(src_file)  
            sound.export(dest_file, format="mp3")
        
        output_filename = Path('.') / 'outputs' / str(uuid.uuid4())

        if not seed or seed == -1:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()
        set_all_seeds(seed)

        self.__mg_model.set_generation_params(duration=length)
        output = self.__mg_model.generate(descriptions=[prompt], progress=True)[0]

        with NamedTemporaryFile("wb", delete=True) as temp_file:
            audio_write(temp_file.name, output.cpu(), self.__mg_model.sample_rate, strategy="loudness", loudness_compressor=True)
            if self.format == 'mp3':
                wavToMp3(f'{temp_file.name}.wav', str(output_filename.with_suffix('.mp3')))
            else:
                shutil.copy(f'{temp_file.name}.wav', str(output_filename.with_suffix('.wav')))

        return str(output_filename.with_suffix('.mp3' if self.format == 'mp3' else '.wav'))


    @property
    def model_size(self):
        return self.__model_size

    @property
    def device(self):
        return self.__device

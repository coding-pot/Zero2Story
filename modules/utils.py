import os
import numpy as np
import random

import torch

import google.generativeai as palm_api

def set_all_seeds(random_seed: int) -> None:
    # TODO: DocString...
    torch.manual_seed(random_seed)
    torch.cuda.manual_seed(random_seed)
    torch.cuda.manual_seed_all(random_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(random_seed)
    random.seed(random_seed)
    print(f"Using seed {random_seed}")


def get_palm_api_key() -> str:
    palm_api_key = os.getenv("PALM_API_KEY")

    if palm_api_key is None:
        with open('.palm_api_key.txt', 'r') as file:
            palm_api_key = file.read().strip()

    if not palm_api_key:
        raise ValueError("PaLM API Key is missing.")
    return palm_api_key


def set_palm_api_key(palm_api_key:str = None) -> None:
    palm_api.configure(api_key=(palm_api_key or get_palm_api_key()))

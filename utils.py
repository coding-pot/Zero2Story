import numpy as np
import random

import torch


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

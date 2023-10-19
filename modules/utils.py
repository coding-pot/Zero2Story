import os
import numpy as np
import random
import uuid

from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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


def merge_video(image_path: str, audio_path: str, story_title:str = None) -> str:
    output_filename = Path('.') / 'outputs' / str(uuid.uuid4())
    output_filename = str(output_filename.with_suffix('.mp4'))

    try:
        temp_image_path = image_path
        if story_title:
            img = Image.open(image_path)
            img_drawable = ImageDraw.Draw(img)
            title_font_path = str(Path('.') / 'assets' / 'Lugrasimo-Regular.ttf')
            title_font = ImageFont.truetype(title_font_path, 24)
            img_drawable.text((65, 468), story_title, font=title_font, fill=(16, 16, 16))
            img_drawable.text((63, 466), story_title, font=title_font, fill=(255, 255, 255))
            
            with NamedTemporaryFile("wb", delete=True) as temp_file:
                temp_image_path = f'{temp_file.name}.png'
                img.save(temp_image_path)

        cmd = [
            'ffmpeg', '-loop', '1', '-i', temp_image_path, '-i', audio_path,
            '-filter_complex',
            '"[1:a]asplit=29[ASPLIT01][ASPLIT02][ASPLIT03][ASPLIT04][ASPLIT05][ASPLIT06][ASPLIT07][ASPLIT08][ASPLIT09][ASPLIT10][ASPLIT11][ASPLIT12][ASPLIT13][ASPLIT14][ASPLIT15][ASPLIT16][ASPLIT17][ASPLIT18][ASPLIT19][ASPLIT20][ASPLIT21][ASPLIT22][ASPLIT23][ASPLIT24][ASPLIT25][ASPLIT26][ASPLIT27][ASPLIT28][ASPLIT29];\
[ASPLIT01]bandpass=frequency=20:width=4:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ01];\
[ASPLIT02]bandpass=frequency=25:width=4:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ02];\
[ASPLIT03]bandpass=frequency=31.5:width=8:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ03];\
[ASPLIT04]bandpass=frequency=40:width=8:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ04];\
[ASPLIT05]bandpass=frequency=50:width=8:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ05];\
[ASPLIT06]bandpass=frequency=63:width=8:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ06];\
[ASPLIT07]bandpass=frequency=80:width=16:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ07];\
[ASPLIT08]bandpass=frequency=100:width=16:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ08];\
[ASPLIT09]bandpass=frequency=125:width=32:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ09];\
[ASPLIT10]bandpass=frequency=160:width=32:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ10];\
[ASPLIT11]bandpass=frequency=200:width=64:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ11];\
[ASPLIT12]bandpass=frequency=250:width=64:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ12];\
[ASPLIT13]bandpass=frequency=315:width=64:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ13];\
[ASPLIT14]bandpass=frequency=400:width=64:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ14];\
[ASPLIT15]bandpass=frequency=500:width=128:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ15];\
[ASPLIT16]bandpass=frequency=630:width=128:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ16];\
[ASPLIT17]bandpass=frequency=800:width=128:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ17];\
[ASPLIT18]bandpass=frequency=1000:width=128:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ18];\
[ASPLIT19]bandpass=frequency=1250:width=256:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ19];\
[ASPLIT20]bandpass=frequency=1500:width=256:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ20];\
[ASPLIT21]bandpass=frequency=2000:width=512:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ21];\
[ASPLIT22]bandpass=frequency=2500:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ22];\
[ASPLIT23]bandpass=frequency=3150:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ23];\
[ASPLIT24]bandpass=frequency=4000:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ24];\
[ASPLIT25]bandpass=frequency=5000:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ25];\
[ASPLIT26]bandpass=frequency=6300:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ26];\
[ASPLIT27]bandpass=frequency=8000:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ27];\
[ASPLIT28]bandpass=frequency=12000:width=1024:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ28];\
[ASPLIT29]bandpass=frequency=16000:width=2048:width_type=h,showvolume=rate=30.000:c=0xAFFFFFFF:b=5:w=176:h=11:o=v:t=0:v=0:m=p:s=0:ds=lin:dm=1:dmc=0xFFFFFFFF[EQ29];\
[EQ01][EQ02][EQ03][EQ04][EQ05][EQ06][EQ07][EQ08][EQ09][EQ10][EQ11][EQ12][EQ13][EQ14][EQ15][EQ16][EQ17][EQ18][EQ19][EQ20][EQ21][EQ22][EQ23][EQ24][EQ25][EQ26][EQ27][EQ28][EQ29]hstack=inputs=29[BARS];[0][BARS]overlay=(W-w)/2:H-h-50:shortest=1,format=yuv420p[out]"',
            '-map', '"[out]"', '-map', '1:a', '-movflags', '+faststart',
            output_filename
        ]

        result = os.system(' '.join([c.strip() for c in cmd]))

        if result == 0:
            return output_filename
        else:
            return None
    except Exception as e:
        print(e)
        return None

import copy
import random
import gradio as gr

import numpy
import PIL

from constants.init_values import (
	places, moods, jobs, random_names, default_character_images
)

from modules import (
	ImageMaker, MusicMaker
)

# TODO: Replace checkpoint filename to Huggingface URL
bg_img_maker = ImageMaker('landscapeAnimePro_v20Inspiration.safetensors')
ch_img_maker = ImageMaker('hellonijicute25d_V10b.safetensors')


def get_random_name(cur_char_name, char_name1, char_name2, char_name3):
	tmp_random_names = copy.deepcopy(random_names)
	tmp_random_names.remove(cur_char_name)
	tmp_random_names.remove(char_name1)
	tmp_random_names.remove(char_name2)
	tmp_random_names.remove(char_name3)
	return random.choice(tmp_random_names)

def gen_character_image(gallery_images, name, age, mbti, personality, job):
	prompt = ("cute cat, rust, epic, viking knotwork, wearing armor and shield, highly detailed, "
			  "high budget, highly detailed, high budget, cinemascope, moody, gorgeous, film grain, grainy")
	
	neg_prompt = ("nsfw, twins, blurry, boring, lowres, bad anatomy, bad hands, text, error, missing fingers, "
				  "extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark")

	prompt, _ = ch_img_maker.generate_prompts_from_keywords([age, mbti, personality, job], name)

	img_filename = ch_img_maker.text2image(prompt, neg_prompt=neg_prompt)
	gen_image = numpy.asarray(PIL.Image.open(img_filename))
	gallery_images.insert(0, gen_image)

	return gr.update(value=gallery_images), gallery_images

def update_on_age(evt: gr.SelectData): 
	job_list = jobs[evt.value]

	return (
    gr.update(value=places[evt.value][0], choices=places[evt.value]),
    gr.update(value=moods[evt.value][0], choices=moods[evt.value]),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list)
	)
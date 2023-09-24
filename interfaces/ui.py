import copy
import random
import gradio as gr

import numpy
import PIL

from constants.init_values import (
	places, moods, jobs, random_names, default_character_images
)

from modules import (
	ImageMaker, palmchat
)

from interfaces import utils

# TODO: Replace checkpoint filename to Huggingface URL
#img_maker = ImageMaker('hellonijicute25d_V10b.safetensors', vae="kl-f8-anime2.vae.safetensors", safety=False)
img_maker = None # ImageMaker('hellonijicute25d_V10b.safetensors', safety=False) # without_VAE

############
# for plotting

def get_random_name(cur_char_name, char_name1, char_name2, char_name3):
	tmp_random_names = copy.deepcopy(random_names)
	tmp_random_names.remove(cur_char_name)
	tmp_random_names.remove(char_name1)
	tmp_random_names.remove(char_name2)
	tmp_random_names.remove(char_name3)
	return random.choice(tmp_random_names)


def gen_character_image(
  gallery_images, 
  name, age, mbti, personality, job, 
  time, place, mood, creative_mode
):
	# generate prompts for character image with PaLM
	for _ in range(3):
		try:
			prompt, neg_prompt = img_maker.generate_character_prompts(name, age, job, keywords=[mbti, personality, time, place, mood], creative_mode=creative_mode)
			print(f"Image Prompt: {prompt}")
			print(f"Negative Prompt: {neg_prompt}")
		except Exception as e:
			print(e)

	if not prompt:
		raise ValueError("Failed to generate prompts for character image.")

	# generate image
	img_filename = img_maker.text2image(prompt, neg_prompt=neg_prompt, ratio='3:4', cfg=4.5)

	# update gallery
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

############
# for tabbing

def update_on_main_tabs(chat_state, evt: gr.SelectData):
    chat_mode = "plot_chat"

    if evt.value.lower() == "background setup":
        chat_mode = "plot_chat"
    elif evt.value.lower() == "story generation":
        chat_mode = "story_chat"
    else: # export
        chat_mode = "export_chat"

    ppm = chat_state[chat_mode]
    return chat_mode, ppm.build_uis()

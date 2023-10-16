import copy
import random
import gradio as gr

import numpy
import PIL
from pathlib import Path

from constants.init_values import (
	genres, places, moods, jobs, random_names, default_character_images
)

from modules import (
	ImageMaker, palmchat
)

from interfaces import utils

### e.g.
#img_maker = ImageMaker('hellonijicute25d_V10b.safetensors') # without_VAE

#img_maker = ImageMaker('hellonijicute25d_V10b.safetensors', vae="klF8Anime2Fp16.safetensors")
#img_maker.push_to_hub('jphan32/Zero2Story', commit_message="test fp16", token="YOUR_HF_TOKEN", variant="character")
#img_maker = ImageMaker('jphan32/Zero2Story', variant="character", from_hf=True)
img_maker = ImageMaker('https://huggingface.co/jphan32/Zero2Story/hellonijicute25d_V10b.safetensors',
						vae="https://huggingface.co/jphan32/Zero2Story/klF8Anime2Fp16.safetensors")

############
# for plotting

get_random_name = f"""
function get_random_name(cur_char_name, char_name1, char_name2, char_name3) {{
	const names = {random_names};
	const names_copy = JSON.parse(JSON.stringify(names));

	const cur_name = 'a';
	const char_name1 = 'b';
	const char_name2 = 'c';
	const char_name3 = 'd';

	let index = names_copy.indexOf(cur_char_name);
	names_copy.splice(index, 1);

	index = names_copy.indexOf(char_name1);
	names_copy.splice(index, 1)

	index = names_copy.indexOf(char_name2);
	names_copy.splice(index, 1);

	index = names_copy.indexOf(char_name3);
	names_copy.splice(index, 1);

	return names_copy[(Math.floor(Math.random() * names_copy.length))];
}}
"""

def update_selected_char_image(evt: gr.EventData):
    return evt.value

# def get_random_name(cur_char_name, char_name1, char_name2, char_name3):
# 	tmp_random_names = copy.deepcopy(random_names)
# 	tmp_random_names.remove(cur_char_name)
# 	tmp_random_names.remove(char_name1)
# 	tmp_random_names.remove(char_name2)
# 	tmp_random_names.remove(char_name3)
# 	return random.choice(tmp_random_names)


def gen_character_image(
  gallery_images, 
  name, age, mbti, personality, job, 
  genre, place, mood, creative_mode
):
	# generate prompts for character image with PaLM
	for _ in range(3):
		try:
			prompt, neg_prompt = img_maker.generate_character_prompts(name, age, job, keywords=[mbti, personality, genre, place, mood], creative_mode=creative_mode)
			print(f"Image Prompt: {prompt}")
			print(f"Negative Prompt: {neg_prompt}")
			break
		except Exception as e:
			print(e)
			raise gr.Error(e)

	if not prompt:
		raise ValueError("Failed to generate prompts for character image.")

	# generate image
	try:
		img_filename = img_maker.text2image(prompt, neg_prompt=neg_prompt, ratio='3:4', cfg=4.5)
	except ValueError as e:
		print(e)
		img_filename = str(Path('.') / 'assets' / 'nsfw_warning.png')

	# update gallery
	# gen_image = numpy.asarray(PIL.Image.open(img_filename))
	gallery_images.insert(0, img_filename)

	return gr.update(value=gallery_images), gallery_images, img_filename


def update_on_age(evt: gr.SelectData): 
	job_list = jobs[evt.value]

	return (
        gr.update(value=places[evt.value][0], choices=places[evt.value]),
        gr.update(value=moods[evt.value][0], choices=moods[evt.value]),
        gr.update(value=job_list[0], choices=job_list),
        gr.update(value=job_list[1], choices=job_list),
        gr.update(value=job_list[2], choices=job_list),
        gr.update(value=job_list[3], choices=job_list)
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

def reset():
	from modules.palmchat import GradioPaLMChatPPManager
    
	return (
		[], # cursors
		0, # cur_cursor
  
		{
				"setting_chat": GradioPaLMChatPPManager(),
				"story_chat": GradioPaLMChatPPManager(),
				"export_chat": GradioPaLMChatPPManager(),
		}, # chat_state
		"setting_chat", # chat_mode
  
		default_character_images, # gallery_images1
		default_character_images, # gallery_images2
		default_character_images, # gallery_images3
		default_character_images, # gallery_images4
		default_character_images[0], # selected_main_char_image1 
		default_character_images[0], # selected_side_char_image1 
		default_character_images[0], # selected_side_char_image2 
		default_character_images[0], # selected_side_char_image3 

		genres[0], # genre_dd
		places[genres[0]][0], # place_dd
		moods[genres[0]][0], # mood_dd

		default_character_images, # char_gallery1
		jobs[genres[0]][0], # job_dd1

		False, # side_char_enable_ckb1
		default_character_images, # char_gallery2
		jobs[genres[0]][1], # job_dd2

		False, # side_char_enable_ckb2
		default_character_images, # char_gallery3
		jobs[genres[0]][2], # job_dd3

		False, # side_char_enable_ckb3
		default_character_images, # char_gallery4
		jobs[genres[0]][3], # job_dd4

		None, # story_image
		None, # story_audio
		None, # story_video

		'', # story_content
		gr.Slider(
			1, 2, 1, step=1, interactive=True, 
			label="1/2", visible=False
		), # story_progress

		'', # custom_prompt_txt

		'Action 1', # action_btn1
		'Action 2', # action_btn2
		'Action 3', # action_btn3
		'', # custom_action_txt

		'Your Own Story', # title_txt

		"", # export_html
	)
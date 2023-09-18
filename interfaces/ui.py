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

from pingpong import PingPong
from pingpong.context import CtxLastWindowStrategy

# TODO: Replace checkpoint filename to Huggingface URL
bg_img_maker = ImageMaker('landscapeAnimePro_v20Inspiration.safetensors', safety=False)
ch_img_maker = ImageMaker('hellonijicute25d_V10b.safetensors', vae="kl-f8-anime2.vae.safetensors", safety=False)


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
	prompt, neg_prompt = ch_img_maker.generate_prompts_from_keywords([
            mbti, personality, time, place, mood], job, age, name
        )
	print(f"Image Prompt: {prompt}")
	print(f"Negative Prompt: {neg_prompt}")
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

def _build_prompts(ppmanager, win_size=3):
    dummy_ppm = copy.deepcopy(ppmanager)
    lws = CtxLastWindowStrategy(win_size)
    return lws(dummy_ppm)

async def chat(user_input, chat_state):
    chat_state.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = _build_prompts(ppm)

    parameters = {
        'model': 'models/chat-bison-001',
        'candidate_count': 1,
        'context': global_context,
        'temperature': res_temp,
        'top_k': res_topk,
        'top_p': res_topp,
    }
    
    palm_if, response_txt = await gen_text(
        prompt, 
        parameters=parameters
    )
	chat_state.replace_last_pong(response_txt)

	return chat_state, chat_state.build_uis()
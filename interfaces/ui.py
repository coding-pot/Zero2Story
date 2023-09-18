import copy
import random
import gradio as gr

import numpy
import PIL

from constants.init_values import (
	places, moods, jobs, random_names, default_character_images
)

from modules import (
	ImageMaker, MusicMaker, palmchat
)

from pingpong import PingPong
from pingpong.context import CtxLastWindowStrategy

# TODO: Replace checkpoint filename to Huggingface URL
bg_img_maker = ImageMaker('landscapeAnimePro_v20Inspiration.safetensors', safety=False)
ch_img_maker = ImageMaker('hellonijicute25d_V10b.safetensors', vae="kl-f8-anime2.vae.safetensors", safety=False)

############
# helpers

def _build_prompts(ppm, win_size=3):
    dummy_ppm = copy.deepcopy(ppm)
    lws = CtxLastWindowStrategy(win_size)
    return lws(dummy_ppm)

async def _get_chat_response(prompt):
    parameters = {
		'model': 'models/chat-bison-001',
		'candidate_count': 1,
		'context': "",
		'temperature': 1.0,
		'top_k': 50,
		'top_p': 0.9,
    }
    
    _, response_txt = await palmchat.gen_text(
        prompt, 
        parameters=parameters
    )

    return response_txt

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

##############
# for chatting

def rollback_last_ui(history):
    return history[:-1]

async def chat(user_input, chat_mode, chat_state):
    ppm = chat_state[chat_mode]
    ppm.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = _build_prompts(ppm)

    response_txt = await _get_chat_response(prompt)
    ppm.replace_last_pong(response_txt)
    
    chat_state[chat_mode] = ppm

    return (
        "", 
        chat_state, 
        ppm.build_uis(), 
        gr.update(interactive=True)
    )

async def chat_regen(chat_mode, chat_state):
    ppm = chat_state[chat_mode]
    
    user_input = ppm.pingpongs[-1].ping
    ppm.pingpongs = ppm.pingpongs[:-1]
    ppm.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = _build_prompts(ppm)

    response_txt = await _get_chat_response(prompt)
    ppm.replace_last_pong(response_txt)
    
    chat_state[chat_mode] = ppm

    return (
        chat_state,
        ppm.build_uis()
    )

def chat_reset(chat_mode, chat_state):
    chat_state[chat_mode] = palmchat.GradioPaLMChatPPManager()

    return (
        "", 
        chat_state, 
        [], 
        gr.update(interactive=False)
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
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

from interfaces import utils

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

async def _get_chat_response(prompt, ctx=None):
    parameters = {
		'model': 'models/chat-bison-001',
		'candidate_count': 1,
		'context': "" if ctx is None else ctx,
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

async def chat(
    user_input, chat_mode, chat_state,
    time, place, mood,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
):
    ctx = f"""You are a professional writing advisor, especially specialized in developing ideas on plotting stories and creating characters. I provide when, where, and mood along with the rough description of one main character and three side characters. 

Give creative responses based on the following information.

when: {time}
where: {place}
mood: {mood}

main character: {{
name: {name1},
job: {job1},
age: {age1},
mbti: {mbti1},
personality: {personality1} 
}}

side character1: {{
name: {name2},
job: {job2},
age: {age2},
mbti: {mbti2},
personality: {personality2} 
}}

side character2: {{
name: {name3},
job: {job3},
age: {age3},
mbti: {mbti3},
personality: {personality3} 
}}

side character3: {{
name: {name4},
job: {job4},
age: {age4},
mbti: {mbti4},
personality: {personality4} 
}}
"""

    ppm = chat_state[chat_mode]
    ppm.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = _build_prompts(ppm)

    response_txt = await _get_chat_response(prompt, ctx)
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

#############
# for plot generation

async def plot_gen(
    time, place, mood,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
):
    ctx = """Based on the given information about the story to be developed, give me one possible titles of the four chapters in JSON format. 

Output template is as follows: ```{"introduction": "title", "development": "title", "turn": "title", "conclusion": "title"}```. 

DO NOT output anything other than JSON values. ONLY JSON is allowed. DO NOT give any further explanations about the titles.
"""

    user_input = f"""
when: {time}
where: {place}
mood: {mood}

main character: {{
name: {name1},
job: {job1},
age: {age1},
mbti: {mbti1},
personality: {personality1} 
}}

side character1: {{
name: {name2},
job: {job2},
age: {age2},
mbti: {mbti2},
personality: {personality2} 
}}

side character2: {{
name: {name3},
job: {job3},
age: {age3},
mbti: {mbti3},
personality: {personality3} 
}}

side character3: {{
name: {name4},
job: {job4},
age: {age4},
mbti: {mbti4},
personality: {personality4} 
}}    
"""

    ppm = palmchat.GradioPaLMChatPPManager()
    ppm.add_pingpong(
        PingPong(user_input, '')
    )
    prompt = _build_prompts(ppm)
    response_txt = await _get_chat_response(prompt)
    response_json = utils.parse_first_json_code_snippet(response_txt)

    return (
        response_txt["introduction"],
        response_txt["development"],
        response_txt["turn"],
        response_txt["conclusion"],
    )
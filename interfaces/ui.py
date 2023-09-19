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

# TODO: Replace checkpoint filename to Huggingface URL
bg_img_maker = ImageMaker('landscapeAnimePro_v20Inspiration.safetensors', safety=False)
ch_img_maker = ImageMaker('hellonijicute25d_V10b.safetensors', vae="kl-f8-anime2.vae.safetensors", safety=False)

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

async def first_paragrph_gen(
    time, place, mood,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
    chapter1_title, chapter2_title, chapter3_title, chapter4_title
):
    ctx = f"""Based on the background information below, suggest me a possible first paragraph of the introduction part in JSON format. Also suggest three specific actions that the characters to choose to continue the story after the next paragraph.

Output template is as follows: ```json{{"paragraph": "gen_paragraph", "actions":["action1", "action2", "action3"]}}```. fill in the gen_paragraph section ONLY.
DO NOT output anything other than JSON values. ONLY JSON is allowed.    
    
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

    user_input = f"""
plot: {{
    "introduction": "{chapter1_title}",
    "development": "{chapter2_title}",
    "turn": "{chapter3_title}",
    "conclusion": "{chapter4_title}"
}}
"""

    ppm = palmchat.GradioPaLMChatPPManager()
    ppm.add_pingpong(
        PingPong(user_input, '')
    )
    prompt = _build_prompts(ppm)

    response_json = None
    while response_json is None:
        response_txt = await _get_chat_response(prompt, ctx=ctx)
        print(response_txt)

        try:
            response_json = utils.parse_first_json_code_snippet(response_txt)
        except:
            pass

    return (
        response_json["paragraph"], 
        response_json["paragraph"],
        response_json["actions"][0],
        response_json["actions"][1],
        response_json["actions"][2]
    )
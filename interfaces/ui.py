import copy
import random
import gradio as gr

from constants.init_values import (
	places, moods, jobs, random_names, default_character_images
)

def get_random_name(cur_char_name, char_name1, char_name2, char_name3):
	tmp_random_names = copy.deepcopy(random_names)
	tmp_random_names.remove(cur_char_name)
	tmp_random_names.remove(char_name1)
	tmp_random_names.remove(char_name2)
	tmp_random_names.remove(char_name3)
	return random.choice(tmp_random_names)

def gen_character_image(name, age, mbti, personality, job):
	print(name, age, mbti, personality, job)
	images = copy.deepcopy(default_character_images)
	images.insert(0, "assets/image.png")

	return gr.update(value=images)

def update_on_age(evt: gr.SelectData):  # SelectData is a subclass of EventData
	job_list = jobs[evt.value]

	return (
    gr.update(value=places[evt.value][0], choices=places[evt.value]),
    gr.update(value=moods[evt.value][0], choices=moods[evt.value]),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list),
    gr.update(value=job_list[0], choices=job_list)
	)
import re
import copy
import random
import gradio as gr
from gradio_client import Client
from pathlib import Path

from modules import (
	ImageMaker, MusicMaker, palmchat, palm_prompts, merge_video
)
from interfaces import utils

from pingpong import PingPong
from pingpong.context import CtxLastWindowStrategy

img_maker = ImageMaker('https://huggingface.co/jphan32/Zero2Story/landscapeAnimePro_v20Inspiration.safetensors',
						vae="https://huggingface.co/jphan32/Zero2Story/cute20vae.safetensors")

bgm_maker = MusicMaker(model_size='small', output_format='mp3')

video_gen_client_url = None # e.g. "https://0447df3cf5f7c49c46.gradio.live"

# default safety settings
safety_settings = [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},
					{"category":"HARM_CATEGORY_TOXICITY","threshold":1},
					{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},
					{"category":"HARM_CATEGORY_SEXUAL","threshold":2},
					{"category":"HARM_CATEGORY_MEDICAL","threshold":2},
					{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}]

async def update_story_gen(
	cursors, cur_cursor_idx,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
):
    if len(cursors) == 1:
        return await first_story_gen(
			cursors,
			genre, place, mood,
			main_char_name, main_char_age, main_char_personality, main_char_job,
			side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
			side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
			side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
			cur_cursor_idx=cur_cursor_idx
		)
    else:
        return await next_story_gen(
			cursors,
			None,
			genre, place, mood,
			main_char_name, main_char_age, main_char_personality, main_char_job,
			side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
			side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
			side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
			cur_cursor_idx=cur_cursor_idx
		)

async def next_story_gen(
	cursors,
	action,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,	
	cur_cursor_idx=None
):
	stories = ""
	cur_side_chars = 1

	action = cursors[cur_cursor_idx]["action"] if cur_cursor_idx is not None else action
	end_idx = len(cursors) if cur_cursor_idx is None else len(cursors)-1

	for cursor in cursors[:end_idx]:
		stories = stories + cursor["story"]

	side_char_prompt = utils.add_side_character(
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)

	prompt = palm_prompts['story_gen']['next_story_gen'].format(
		genre=genre, place=place, mood=mood,
		main_char_name=main_char_name,
		main_char_job=main_char_job,
		main_char_age=main_char_age,
		main_char_personality=main_char_personality,
		side_char_placeholder=side_char_prompt,
		stories=stories, action=action,
	)

	print(f"generated prompt:\n{prompt}")
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': 1.0,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
		'safety_settings': safety_settings,
	}
	try:
		response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)
	except Exception as e:
		print(e)
		raise gr.Error(e)

	story = response_json["paragraphs"]
	if isinstance(story, list):
		story = "\n\n".join(story)
  
	if cur_cursor_idx is None:
		cursors.append({
			"title": "",
			"story": story,
			"action": action
		})
	else:
		cursors[cur_cursor_idx]["story"] = story
		cursors[cur_cursor_idx]["action"] = action

	return (
		cursors, len(cursors)-1,
		story,
		gr.update(
			maximum=len(cursors), value=len(cursors),
			label=f"{len(cursors)} out of {len(cursors)} stories",
			visible=True, interactive=True
		),
		gr.update(interactive=True),
		gr.update(interactive=True),
		gr.update(value=None, visible=False, interactive=True),
		gr.update(value=None, visible=False, interactive=True),
		gr.update(value=None, visible=False, interactive=True),	
	)

async def actions_gen(
	cursors,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	cur_cursor_idx=None
):
	stories = ""
	cur_side_chars = 1
	end_idx = len(cursors) if cur_cursor_idx is None else len(cursors)-1

	for cursor in cursors[:end_idx]:
		stories = stories + cursor["story"]

	summary_prompt = palm_prompts['story_gen']['summarize'].format(stories=stories)

	print(f"generated prompt:\n{summary_prompt}")
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': 1.0,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
		'safety_settings': safety_settings,
	}

	try:
		_, summary = await palmchat.gen_text(summary_prompt, mode="text", parameters=parameters)
	except Exception as e:
		print(e)
		raise gr.Error(e)

	side_char_prompt = utils.add_side_character(
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
	prompt = palm_prompts['story_gen']['actions_gen'].format(
		genre=genre, place=place, mood=mood,
		main_char_name=main_char_name,
		main_char_job=main_char_job,
		main_char_age=main_char_age,
		main_char_personality=main_char_personality,
		side_char_placeholder=side_char_prompt,
		summary=summary,
	)

	print(f"generated prompt:\n{prompt}")
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': 1.0,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
		'safety_settings': safety_settings,
	}
	try:
		response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)
	except Exception as e:
		print(e)
		raise gr.Error(e)
	actions = response_json["options"]

	random_actions = random.sample(actions, 3)

	return (
		gr.update(value=random_actions[0], interactive=True),
		gr.update(value=random_actions[1], interactive=True),
		gr.update(value=random_actions[2], interactive=True),
		"   "
	)

async def first_story_gen(
	cursors,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	cur_cursor_idx=None
):
	cur_side_chars = 1

	side_char_prompt = utils.add_side_character(
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
	prompt = palm_prompts['story_gen']['first_story_gen'].format(
		genre=genre, place=place, mood=mood,
		main_char_name=main_char_name,
		main_char_job=main_char_job,
		main_char_age=main_char_age,
		main_char_personality=main_char_personality,
		side_char_placeholder=side_char_prompt,
	)

	print(f"generated prompt:\n{prompt}")
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': 1.0,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
		'safety_settings': safety_settings,
	}
	try:
		response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)
	except Exception as e:
		print(e)
		raise gr.Error(e)

	story = response_json["paragraphs"]
	if isinstance(story, list):
		story = "\n\n".join(story)
  
	if cur_cursor_idx is None:
		cursors.append({
			"title": "",
			"story": story
		})
	else:
		cursors[cur_cursor_idx]["story"] = story

	return (
		cursors, len(cursors)-1,
		story,
		gr.update(
			maximum=len(cursors), value=len(cursors),
			label=f"{len(cursors)} out of {len(cursors)} stories",
			visible=False if len(cursors) == 1 else True, interactive=True
		),
		gr.update(interactive=True),
		gr.update(interactive=True),
		gr.update(value=None, visible=False, interactive=True),
		gr.update(value=None, visible=False, interactive=True),	
  		gr.update(value=None, visible=False, interactive=True),
	)

def video_gen(
	image, audio, title, cursors, cur_cursor, use_ffmpeg=True
):
	if use_ffmpeg:
		output_filename = merge_video(image, audio, story_title="")
	
	if not use_ffmpeg or not output_filename:
		client = Client(video_gen_client_url)
		result = client.predict(
			"",
			audio,
			image,
			f"{utils.id_generator()}.mp4",
			api_name="/predict"
		)
		output_filename = result[0]

	cursors[cur_cursor]["video"] = output_filename

	return (
		gr.update(visible=False),
		gr.update(visible=False),
		gr.update(visible=True, value=output_filename),
		cursors,
		"   "
	)


def image_gen(
	genre, place, mood, title, story_content, cursors, cur_cursor
):
	# generate prompts for background image with PaLM
	for _ in range(3):
		try:
			prompt, neg_prompt = img_maker.generate_background_prompts(genre, place, mood, title, "", story_content)
			print(f"Image Prompt: {prompt}")
			print(f"Negative Prompt: {neg_prompt}")
			break
		except Exception as e:
			print(e)
			raise gr.Error(e)
			
	if not prompt:
		raise ValueError("Failed to generate prompts for background image.")

	# generate image
	try:
		img_filename = img_maker.text2image(prompt, neg_prompt=neg_prompt, ratio='16:9', cfg=6.5)
	except ValueError as e:
		print(e)
		img_filename = str(Path('.') / 'assets' / 'nsfw_warning_wide.png')
	
	cursors[cur_cursor]["img"] = img_filename

	return  (
		gr.update(visible=True, value=img_filename),
		cursors,
		"  "
	)


def audio_gen(
	genre, place, mood, title, story_content, cursors, cur_cursor
):
	# generate prompt for background music with PaLM
	for _ in range(3):
		try:
			prompt = bgm_maker.generate_prompt(genre, place, mood, title, "", story_content)
			print(f"Music Prompt: {prompt}")
			break
		except Exception as e:
			print(e)
			raise gr.Error(e)

	if not prompt:
		raise ValueError("Failed to generate prompt for background music.")

	# generate music
	bgm_filename = bgm_maker.text2music(prompt, length=60)
	cursors[cur_cursor]["audio"] = bgm_filename

	return (
		gr.update(visible=True, value=bgm_filename),
		cursors,
		" "
	)

def move_story_cursor(moved_cursor, cursors):
	cursor_content = cursors[moved_cursor-1]
	max_cursor = len(cursors)

	action_btn = (
			gr.update(interactive=False),
			gr.update(interactive=False),
			gr.update(interactive=False)
	)

	if moved_cursor == max_cursor:
		action_btn = (
			gr.update(interactive=True),
			gr.update(interactive=True),
			gr.update(interactive=True)
		)

	if "video" in cursor_content:
		outputs = (
			moved_cursor-1,
			gr.update(label=f"{moved_cursor} out of {len(cursors)} chapters"),
			cursor_content["story"],
			gr.update(value=None, visible=False),
			gr.update(value=None, visible=False),
			gr.update(value=cursor_content["video"], visible=True),
		)

	else:
		image_container = gr.update(value=None, visible=False)
		audio_container = gr.update(value=None, visible=False)

		if "img" in cursor_content:
			image_container = gr.update(value=cursor_content["img"], visible=True)

		if "audio" in cursor_content:
			audio_container = gr.update(value=cursor_content["audio"], visible=True)

		outputs = (
			moved_cursor-1,
			gr.update(label=f"{moved_cursor} out of {len(cursors)} stories"),
			cursor_content["story"],
			image_container,
			audio_container,
			gr.update(value=None, visible=False),
		)        

	return outputs + action_btn

def update_story_content(story_content, cursors, cur_cursor):
	cursors[cur_cursor]["story"] = story_content
	return cursors

def disable_btns():
	return (
		gr.update(interactive=False), # image_gen_btn
		gr.update(interactive=False), # audio_gen_btn
		gr.update(interactive=False), # img_audio_combine_btn

		gr.update(interactive=False), # regen_actions_btn
		gr.update(interactive=False), # regen_story_btn
		gr.update(interactive=False), # custom_prompt_txt

		gr.update(interactive=False), # action_btn1
		gr.update(interactive=False), # action_btn2
		gr.update(interactive=False), # action_btn3

		gr.update(interactive=False), # custom_action_txt

		gr.update(interactive=False), # restart_from_story_generation_btn
		gr.update(interactive=False), # story_writing_done_btn
	)
 
def enable_btns(story_image, story_audio):
	video_gen_btn_state = gr.update(interactive=False)
    
	if story_image is not None and \
		story_audio is not None:
		video_gen_btn_state = gr.update(interactive=True)
    
	return (
		gr.update(interactive=True), # image_gen_btn
		gr.update(interactive=True), # audio_gen_btn
		video_gen_btn_state, # img_audio_combine_btn

		gr.update(interactive=True), # regen_actions_btn
		gr.update(interactive=True), # regen_story_btn
		gr.update(interactive=True), # custom_prompt_txt

		gr.update(interactive=True), # action_btn1
		gr.update(interactive=True), # action_btn2
		gr.update(interactive=True), # action_btn3

		gr.update(interactive=True), # custom_action_txt

		gr.update(interactive=True), # restart_from_story_generation_btn
		gr.update(interactive=True), # story_writing_done_btn
	)
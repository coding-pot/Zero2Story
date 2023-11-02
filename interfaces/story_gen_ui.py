import re
import copy
import json
import random
import gradio as gr
from gradio_client import Client
from pathlib import Path

from modules import (
	ImageMaker, MusicMaker, merge_video
)
from modules.llms import get_llm_factory
from interfaces import utils

from pingpong import PingPong
from pingpong.context import CtxLastWindowStrategy

img_maker = ImageMaker('https://huggingface.co/jphan32/Zero2Story/landscapeAnimePro_v20Inspiration.safetensors',
						vae="https://huggingface.co/jphan32/Zero2Story/cute20vae.safetensors")

bgm_maker = MusicMaker(model_size='small', output_format='mp3')

video_gen_client_url = None # e.g. "https://0447df3cf5f7c49c46.gradio.live"


async def update_story_gen(
	llm_factory, llm_mode,
	cursors, cur_cursor_idx,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
):
    if len(cursors) == 1:
        return await first_story_gen(
			llm_factory,
			llm_mode,
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
			llm_factory,
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
	llm_factory,
	llm_mode,
	cursors,
	action,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,	
	cur_cursor_idx=None,
):
	stories = ""

	action = cursors[cur_cursor_idx]["action"] if cur_cursor_idx is not None else action
	end_idx = len(cursors) if cur_cursor_idx is None else len(cursors)-1

	for cursor in cursors[:end_idx]:
		stories = stories + cursor["story"]

	context, examples, prompt, ppm = utils.build_next_story_gen_prompts(
		llm_mode, llm_factory,
		stories, action, 
		genre, place, mood,
		main_char_name, main_char_age, main_char_personality, main_char_job,
		side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
		side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
		side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	)

	print(f"generated prompt:\n{prompt}")
	if llm_mode == "text":
		parsing_key = "paragraphs"
		try:
			res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, mode="text"
			)
		except Exception as e:
			raise gr.Error(e)

		story = res_json["paragraphs"]
	else:
		parsing_key = "text"
		try: 
			res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, context=context, examples=examples, mode="chat", candidate=8,
			)
		except Exception as e:
			raise gr.Error(e)

	story = res_json[parsing_key]
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

	if llm_mode != "text":
		ppm.replace_last_pong(story)

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
	llm_factory,
	llm_mode,
	cursors,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	cur_cursor_idx=None,
):
	prompts = llm_factory.create_prompt_manager().prompts
	llm_service = llm_factory.create_llm_service()
	summary = None

	stories = ""
	end_idx = len(cursors) if cur_cursor_idx is None else len(cursors)-1

	if llm_mode == "text":
		for cursor in cursors[:end_idx]:
			stories = stories + cursor["story"]
  
		summary_prompt = prompts['story_gen']['summarize'].format(stories=stories)
		print(f"generated prompt:\n{summary_prompt}")
  
		try:
			parameters = llm_service.make_params(mode="text", temperature=1.0, top_k=40, top_p=1.0, max_output_tokens=4096)
			_, summary = await llm_service.gen_text(summary_prompt, mode="text", parameters=parameters)
		except Exception as e:
			print(e)
			raise gr.Error(e)

	ppm, context, examples, prompt = utils.build_actions_gen_prompts(
		llm_mode, llm_factory, 
		summary, stories,
		genre, place, mood,
		main_char_name, main_char_age, main_char_personality, main_char_job,
		side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
		side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
		side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	)

	print(f"generated prompt:\n{prompt}")
	if llm_mode == "text":
		try:
			res_json = await utils.retry_until_valid_json(prompt, parameters=parameters)
		except Exception as e:
			print(e)
			raise gr.Error(e)
		actions = res_json["options"]
		actions = random.sample(actions, 3)
	else:
		try:
			res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, context=context, examples=examples, mode="chat", candidate=8,
			)
		except Exception as e:
			print(e)
			raise gr.Error(e)
		actions = res_json["actions"]
		ppm.replace_last_pong(json.dumps(res_json))

	return (
		[] if llm_mode == "text" else ppm.pingpongs,
		gr.update(value=actions[0], interactive=True),
		gr.update(value=actions[1], interactive=True),
		gr.update(value=actions[2], interactive=True),
		"   "
	)

async def first_story_gen(
	llm_factory, 
	llm_mode,
	cursors,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	cur_cursor_idx=None,
):  
    context, examples, prompt, ppm = utils.build_first_story_gen_prompts(
		llm_mode, llm_factory,
		genre, place, mood,
		main_char_name, main_char_age, main_char_personality, main_char_job,
		side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
		side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
		side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	)
    
    if llm_mode == "text":
        parsing_key = "paragraphs"
        try:
            res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, mode="text"
			)
        except Exception as e:
            raise gr.Error(e)

        story = res_json["paragraphs"]

    else:
        parsing_key = "text"
        try: 
            res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, context=context, examples=examples, mode="chat", candidate=8,
			)
        except Exception as e:
            raise gr.Error(e)
        
    # post processings
    print(res_json)
    story = res_json[parsing_key]
    if isinstance(story, list):
        story = "\n\n".join(story)

    if cur_cursor_idx is None:
        cursors.append({
			"title": "",
			"story": story
		})
    else:
        cursors[cur_cursor_idx]["story"] = story
        
    if llm_mode != "text":
        ppm.replace_last_pong(story)

    return (
		cursors, 
		len(cursors)-1,
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


async def image_gen(
	llm_factory, llm_mode,
	genre, place, mood, title, story_content, cursors, cur_cursor
):
	# generate prompts for background image with LLM
	for _ in range(3):
		try:
			prompt, neg_prompt = await img_maker.generate_background_prompts(
				llm_factory, llm_mode,
				genre, place, mood, title, "", story_content
			)
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


async def audio_gen(
	llm_factory, llm_mode,
	genre, place, mood, title, story_content, cursors, cur_cursor
):
	# generate prompt for background music with LLM
	for _ in range(3):
		try:
			prompt = await bgm_maker.generate_prompt(
				llm_factory, llm_mode,
				genre, place, mood, title, "", story_content
			)
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
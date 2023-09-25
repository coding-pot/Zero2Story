import copy
import random
import gradio as gr
from gradio_client import Client

from modules import (
	ImageMaker, MusicMaker, palmchat, merge_video
)
from interfaces import utils

from pingpong import PingPong
from pingpong.context import CtxLastWindowStrategy

# TODO: Replace checkpoint filename to Huggingface URL
img_maker = ImageMaker('landscapeAnimePro_v20Inspiration.safetensors', safety=False)
bgm_maker = MusicMaker(model_size='small', output_format='mp3')

video_gen_client_url = "https://0447df3cf5f7c49c46.gradio.live"

def _get_next_plot_types(cur_plot_type):
	if cur_plot_type == "rising action":
		return "crisis"
	elif cur_plot_type == "crisis":
		return "climax"
	elif cur_plot_type == "climax":
		return "falling action"
	elif cur_plot_type == "falling action":
		return "denouement"
	else:
		return "end"

def _add_side_character(
	enable, prompt, cur_side_chars,
	name, age, mbti, personality, job
):
	if enable:
		prompt = prompt + f"""
side character #{cur_side_chars}
- name: {name},
- job: {job},
- age: {age},
- mbti: {mbti},
- personality: {personality}

"""
		cur_side_chars = cur_side_chars + 1
		
	return prompt, cur_side_chars

def _add_contents_by_content_types(cursors, plot_type):
	plot_contents = {}
	sub_prompts = ""
	
	for cursor in cursors:
		if cursor["plot_type"] not in plot_contents:
			plot_contents[cursor["plot_type"]] = cursor["story"]
		else:
			plot_contents[cursor["plot_type"]] = plot_contents[cursor["plot_type"]] + cursor["story"]
 
	for t in ["rising action", "crisis", "climax", "falling action", "denouement"]:
		if t == plot_type:
			break
		else:
			sub_prompts = sub_prompts + f"""{t} contents
- paragraphs: {plot_contents[t]}
"""

	return sub_prompts

async def next_story_gen(
	action_type, action,
	title, subtitle, story_content,
 	rising_action, crisis, climax, falling_action, denouement,
	time, place, mood,
	side_char_enable1, side_char_enable2, side_char_enable3,
	name1, age1, mbti1, personality1, job1,
	name2, age2, mbti2, personality2, job2,
	name3, age3, mbti3, personality3, job3,
	name4, age4, mbti4, personality4, job4, 
	cursors, cur_cursor
):
	cur_side_chars = 1
	line_break = '\n'
	plot_type = cursors[cur_cursor]["plot_type"]

	if action_type != "move to the next phase":
		prompt = f"""Write the chapter title and the first few paragraphs of the "{_get_next_plot_types(plot_type)}" plot based on the background information below in Ronald Tobias's plot theory. Also, suggest three choosable actions to drive current story in different directions. The first few paragraphs should be filled with a VERY MUCH detailed and descriptive at least two paragraphs of string. REMEMBER the first few paragraphs should not end the whole story and allow leaway for the next paragraphs to come.

background information:
- genre: string
- where: string
- mood: string

main character
- name: string
- job: string
- age: string
- mbti: string
- personality: string

overall outline
- title: string
- rising action: string
- crisis: string
- climax: string
- falling action: string
- denouement: string

rising action contents
- paragraphs: string

crisis contents
- paragraphs: string

climax contents
- paragraphs: string

falling action contents
- paragraphs: string

denouement contents
- paragraphs: string

JSON output:
{{
	"chapter_title": "string",
	"paragraphs": ["string", "string", ...],
	"actions": ["string", "string", "string"]
}}

background information:
- genre: {time}
- where: {place}
- mood: {mood}

main character
- name: {name1}
- job: {job1},
- age: {age1},
- mbti: {mbti1},
- personality: {personality1}

"""

		prompt, cur_side_chars = _add_side_character(
			side_char_enable1, prompt, cur_side_chars,
			name2, job2, age2, mbti2, personality2
		)
		prompt, cur_side_chars = _add_side_character(
			side_char_enable2, prompt, cur_side_chars,
			name3, job3, age3, mbti3, personality3
		)
		prompt, cur_side_chars = _add_side_character(
			side_char_enable3, prompt, cur_side_chars,
			name4, job4, age4, mbti4, personality4
		)
	
		prompt = prompt + f"""
overall outline
- title: {title}
- rising action: {rising_action}
- crisis: {crisis}
- climax: {climax}
- falling action: {falling_action}
- denouement: {denouement}

"""
		prompt = prompt + _add_contents_by_content_types(cursors, plot_type)
		prompt = prompt + """
JSON output:
"""

		print(f"generated prompt:\n{prompt}")
		parameters = {
			'model': 'models/text-bison-001',
			'candidate_count': 1,
			'temperature': 0.9,
			'top_k': 40,
			'top_p': 1,
			'max_output_tokens': 4096,
		}
		response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

		cursors.append({
			"title": response_json["chapter_title"],
			"plot_type": _get_next_plot_types(plot_type),
			"story": "\n\n".join(response_json["paragraphs"])
		})
		cur_cursor = cur_cursor + 1

		return (
			f"## {response_json['chapter_title']}",
			"\n\n".join(response_json["paragraphs"]),
			cursors, cur_cursor,
			gr.update(
				maximum=len(cursors), value=cur_cursor+1,
				label=f"{cur_cursor} out of {len(cursors)} chapters", visible=True
			),
			gr.update(value=None, visible=False),
			gr.update(value=None, visible=False),
			gr.update(value=None, visible=False),
			gr.update(value=response_json["next actions"][0], interactive=True),
			gr.update(value=response_json["next actions"][1], interactive=True),
			gr.update(value=response_json["next actions"][2], interactive=True)
		)
	else:
		prompt = f"""Write the next few paragraphs of the "{plot_type}" plot based on the background information below in Ronald Tobias's plot theory. The next few paragraphs should be naturally connected to the current paragraphs, and they should be written based on the "action choice". Also, suggest three choosable actions to drive current story in different directions. The choosable actions should not have a duplicate action of the action choice. The next few paragraphs should be filled with a VERY MUCH detailed and descriptive at least two paragraphs of string. Each paragraph should consist of at least five sentences. REMEMBER the next few paragraphs should not end the whole story and allow leaway for the next paragraphs to come.

background information:
- genre: string
- where: string
- mood: string

main character
- name: string
- job: string
- age: string
- mbti: string
- personality: string

overall outline
- title: string
- rising action: string
- crisis: string
- climax: string
- falling action: string
- denouement: string

{plot_type} contents
- current paragraphs: string
- action choice: string

JSON output:
{{
	"next paragraphs": ["string", "string", ...],
	"next actions": ["string", "string", "string"]
}}

background information:
- genre: {time}
- where: {place}
- mood: {mood}

main character
- name: {name1}
- job: {job1},
- age: {age1},
- mbti: {mbti1},
- personality: {personality1}

"""

		prompt, cur_side_chars = _add_side_character(
			side_char_enable1, prompt, cur_side_chars,
			name2, job2, age2, mbti2, personality2
		)
		prompt, cur_side_chars = _add_side_character(
			side_char_enable2, prompt, cur_side_chars,
			name3, job3, age3, mbti3, personality3
		)
		prompt, cur_side_chars = _add_side_character(
			side_char_enable3, prompt, cur_side_chars,
			name4, job4, age4, mbti4, personality4
		)
	
		prompt = prompt + f"""
overall outline
- title: {title}
- rising action: {rising_action}
- crisis: {crisis}
- climax: {climax}
- falling action: {falling_action}
- denouement: {denouement}

rising action contents
- current paragraphs: {story_content.replace(line_break, "")}
- action choice: {action}

JSON output:
"""

		print(f"generated prompt:\n{prompt}")
		parameters = {
			'model': 'models/text-bison-001',
			'candidate_count': 1,
			'temperature': 0.9,
			'top_k': 40,
			'top_p': 1,
			'max_output_tokens': 4096,
		}
		response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

		cursors.append({
			"title": subtitle.replace("## ", ""),
			"plot_type": plot_type,
			"story": "\n\n".join(response_json["next paragraphs"])
		})
		cur_cursor = cur_cursor + 1

		return (
			subtitle,
			"\n\n".join(response_json["next paragraphs"]),
			cursors, cur_cursor,
			gr.update(
				maximum=len(cursors), value=cur_cursor+1,
				label=f"{cur_cursor} out of {len(cursors)} chapters", visible=True
			),
			gr.update(value=None, visible=False),
			gr.update(value=None, visible=False),
			gr.update(value=None, visible=False),
			gr.update(value=response_json["next actions"][0], interactive=True),
			gr.update(value=response_json["next actions"][1], interactive=True),
			gr.update(value=response_json["next actions"][2], interactive=True)
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
	time, place, mood, title, story_content, cursors, cur_cursor, story_audio
):
	# generate prompts for background image with PaLM
	for _ in range(3):
		try:
			prompt, neg_prompt = img_maker.generate_background_prompts(time, place, mood, title, "", story_content)
			print(f"Image Prompt: {prompt}")
			print(f"Negative Prompt: {neg_prompt}")
		except Exception as e:
			print(e)
			
	if not prompt:
		raise ValueError("Failed to generate prompts for background image.")

	# generate image
	img_filename = img_maker.text2image(prompt, neg_prompt=neg_prompt, ratio='16:9', cfg=4.5)
	cursors[cur_cursor]["img"] = img_filename

	video_gen_btn_state = gr.update(interactive=False)
	if story_audio is not None:
		video_gen_btn_state = gr.update(interactive=True)

	return  (
		gr.update(visible=True, value=img_filename),
		video_gen_btn_state,
		cursors,
		"  "
	)


def audio_gen(
	time, place, mood, title, story_content, cursors, cur_cursor, story_image
):
	# generate prompt for background music with PaLM
	for _ in range(3):
		try:
			prompt = bgm_maker.generate_prompt(time, place, mood, title, "", story_content)
			print(f"Music Prompt: {prompt}")
		except Exception as e:
			print(e)

	if not prompt:
		raise ValueError("Failed to generate prompt for background music.")

	# generate music
	bgm_filename = bgm_maker.text2music(prompt, length=60)
	cursors[cur_cursor]["audio"] = bgm_filename

	video_gen_btn_state = gr.update(interactive=False)
	if story_image is not None:
		video_gen_btn_state = gr.update(interactive=True)

	return (
		gr.update(visible=True, value=bgm_filename),
		video_gen_btn_state,
		cursors,
		" "
	)

def move_story_cursor(moved_cursor, cursors):
	print(moved_cursor)

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
			gr.update(label=f"{moved_cursor} out of {len(cursors)} chapters"),
			cursor_content["story"],
			image_container,
			audio_container,
			gr.update(value=None, visible=False),
		)        

	return outputs + action_btn
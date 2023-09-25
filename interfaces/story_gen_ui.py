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

async def next_story_gen(
	action_type, action,
	title, plot, story_content,
	cursors, cur_cursor
):
	story = ""
	for cursor in cursors:
		story = story + cursor["story"]

	prompt = ("You are a world-renowned novelist and TRPG creator. You specialize in long, "
	"descriptive sentences and enigmatic plots. When writing, you must follow Ronald Tobia"
	"s's plot theory and Gustav Freytag's pyramid theory. According to Gustav Freytag's py"
	"ramid theory, the plot type contains rising actions-crisis-climax-falling actions-den"
	"ouncement.\n"
	"Output template is as follows: ```json{\"chapter_title\": \"chapter_title\", \"plot_t"
	"ype based on Freytag's Theory\": \"type\", \"story\": {\"story\" : \"story\", \"acti"
	"on1\": \"action1\", \"action2\": \"action2\", \"action3\": \"action3\"}```. DO NOT ou"
	"tput anything other than JSON values. ONLY JSON is allowed. The JSON key name should not be changed."
	f"""
```json
{{"chapter_title": "{title}", "plot_type based on Freytag's Theory" : "{action_type}", "story": {{"story": "{story}", "action" : "{action}"}}}}
```

""")

	print(f"generated prompt:\n{prompt}")	
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': 0.7,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
	}
	response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

	cursors.append({
		"story": response_json["story"]["story"]
	})
	cur_cursor = cur_cursor + 1

	return (
		response_json["story"]["story"],
		cursors, cur_cursor,
		gr.update(
			maximum=len(cursors), value=cur_cursor+1,
			label=f"{cur_cursor} out of {len(cursors)} chapters", visible=True
		),
		gr.update(value=None, visible=False),
		gr.update(value=None, visible=False),
		gr.update(value=None, visible=False),
        gr.update(value=response_json["story"]["action1"], interactive=True),
        gr.update(value=response_json["story"]["action2"], interactive=True),
        gr.update(value=response_json["story"]["action3"], interactive=True)
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
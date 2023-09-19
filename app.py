import copy
import random

import gradio as gr

from constants.css import STYLE
from constants.init_values import (
	times, places, moods, jobs, ages, mbtis, random_names, personalities, default_character_images, styles
)

from interfaces import ui
from modules.palmchat import GradioPaLMChatPPManager

with gr.Blocks(css=STYLE) as demo:
	chat_mode = gr.State("plot_chat")

	chat_state = gr.State({
		"ppmanager_type": GradioPaLMChatPPManager(),
		"plot_chat": GradioPaLMChatPPManager(),
		"story_chat": GradioPaLMChatPPManager(),
		"export_chat": GradioPaLMChatPPManager(),
	})

	gallery_images1 = gr.State(default_character_images)
	gallery_images2 = gr.State(default_character_images)
	gallery_images3 = gr.State(default_character_images)
	gallery_images4 = gr.State(default_character_images)

	with gr.Row():
		with gr.Column(scale=2):
			with gr.Tabs() as main_tabs:
				with gr.TabItem("background setup", idx=0):
					with gr.Column():
						with gr.Column() as x:
							with gr.Row():
								time_dd = gr.Dropdown(label="time", choices=times, value=times[0], interactive=True, elem_classes=["center-label"])
								place_dd = gr.Dropdown(label="place", choices=places["Middle Ages"], value=places["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])
								mood_dd = gr.Dropdown(label="mood", choices=moods["Middle Ages"], value=moods["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])

							with gr.Tab("main character"):
								with gr.Row():
									with gr.Column(scale=1, elem_classes=["no-width"]):
										char_gallery1 = gr.Gallery(value=default_character_images, height=170, preview=True, elem_classes=["no-label-gallery"])

									with gr.Column(scale=3):
										with gr.Row():
											gr.Markdown("name", elem_classes=["markdown-left"], scale=1)
											name_txt1 = gr.Textbox(random_names[0], elem_classes=["no-label"], scale=2)
											random_name_btn1 = gr.Button("🗳️", elem_classes=["wrap", "control-button"], scale=1)
											gr.Markdown("age", elem_classes=["markdown-center"], scale=1)
											age_dd1 = gr.Dropdown(label=None, choices=ages, value=ages[0], elem_classes=["no-label"], scale=2)

										with gr.Row():
											gr.Markdown("personalities", elem_classes=["markdown-left"], scale=1)
											mbti_dd1 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[0], interactive=True, elem_classes=["no-label"], scale=2)
											personality_dd1 = gr.Dropdown(label=None, choices=personalities, value=personalities[0], interactive=True, elem_classes=["no-label", "left-margin"], scale=2)

										with gr.Row():
											gr.Markdown("job", elem_classes=["markdown-left"], scale=1)
											job_dd1 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gr.Markdown("style", elem_classes=["markdown-left"], scale=1)
											creative_dd1 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gen_char_btn1 = gr.Button("gen character", elem_classes=["wrap", "control-button"], scale=3)

							with gr.Tab("side character 1"):
								with gr.Row():
									with gr.Column(scale=1, elem_classes=["no-width"]):
										char_gallery2 = gr.Gallery(value=default_character_images, height=170, preview=True, elem_classes=["no-label-gallery"])

									with gr.Column(scale=3):
										with gr.Row():
											gr.Markdown("name", elem_classes=["markdown-left"], scale=1)
											name_txt2 = gr.Textbox(random_names[1], elem_classes=["no-label"], scale=2)
											random_name_btn2 = gr.Button("🗳️", elem_classes=["wrap", "control-button"], scale=1)
											gr.Markdown("age", elem_classes=["markdown-center"], scale=1)
											age_dd2 = gr.Dropdown(label=None, choices=ages, value=ages[1], elem_classes=["no-label"], scale=2)

										with gr.Row():
											gr.Markdown("personalities", elem_classes=["markdown-left"], scale=1)
											mbti_dd2 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[0], interactive=True, elem_classes=["no-label"], scale=2)
											personality_dd2 = gr.Dropdown(label=None, choices=personalities, value=personalities[0], interactive=True, elem_classes=["no-label", "left-margin"], scale=2)

										with gr.Row():
											gr.Markdown("job", elem_classes=["markdown-left"], scale=1)
											job_dd2 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gr.Markdown("style", elem_classes=["markdown-left"], scale=1)
											creative_dd2 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gen_char_btn2 = gr.Button("gen character", elem_classes=["wrap", "control-button"], scale=3)


							with gr.Tab("2"):
								with gr.Row():
									with gr.Column(scale=1, elem_classes=["no-width"]):
										char_gallery3 = gr.Gallery(value=default_character_images, height=170, preview=True, elem_classes=["no-label-gallery"])

									with gr.Column(scale=3):
										with gr.Row():
											gr.Markdown("name", elem_classes=["markdown-left"], scale=1)
											name_txt3 = gr.Textbox(random_names[2], elem_classes=["no-label"], scale=2)
											random_name_btn3 = gr.Button("🗳️", elem_classes=["wrap", "control-button"], scale=1)
											gr.Markdown("age", elem_classes=["markdown-center"], scale=1)
											age_dd3 = gr.Dropdown(label=None, choices=ages, value=ages[0], elem_classes=["no-label"], scale=2)

										with gr.Row():
											gr.Markdown("personalities", elem_classes=["markdown-left"], scale=1)
											mbti_dd3 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[0], interactive=True, elem_classes=["no-label"], scale=2)
											personality_dd3 = gr.Dropdown(label=None, choices=personalities, value=personalities[0], interactive=True, elem_classes=["no-label", "left-margin"], scale=2)

										with gr.Row():
											gr.Markdown("job", elem_classes=["markdown-left"], scale=1)
											job_dd3 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gr.Markdown("style", elem_classes=["markdown-left"], scale=1)
											creative_dd3 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gen_char_btn3 = gr.Button("gen character", elem_classes=["wrap", "control-button"], scale=3)

							with gr.Tab("3"):
								with gr.Row():
									with gr.Column(scale=1, elem_classes=["no-width"]):
										char_gallery4 = gr.Gallery(value=default_character_images, height=170, preview=True, elem_classes=["no-label-gallery"])

									with gr.Column(scale=3):
										with gr.Row():
											gr.Markdown("name", elem_classes=["markdown-left"], scale=1)
											name_txt4 = gr.Textbox(random_names[3], elem_classes=["no-label"], scale=2)
											random_name_btn4 = gr.Button("🗳️", elem_classes=["wrap", "control-button"], scale=1)
											gr.Markdown("age", elem_classes=["markdown-center"], scale=1)
											age_dd4 = gr.Dropdown(label=None, choices=ages, value=ages[0], elem_classes=["no-label"], scale=2)

										with gr.Row():
											gr.Markdown("personalities", elem_classes=["markdown-left"], scale=1)
											mbti_dd4 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[0], interactive=True, elem_classes=["no-label"], scale=2)
											personality_dd4 = gr.Dropdown(label=None, choices=personalities, value=personalities[0], interactive=True, elem_classes=["no-label", "left-margin"], scale=2)

										with gr.Row():
											gr.Markdown("job", elem_classes=["markdown-left"], scale=1)
											job_dd4 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gr.Markdown("style", elem_classes=["markdown-left"], scale=1)
											creative_dd4 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=3)
											gen_char_btn4 = gr.Button("gen character", elem_classes=["wrap", "control-button"], scale=3)

					with gr.Column(elem_classes=["ninty-five-width"]):
						with gr.Row(elem_classes=["no-border"]):
							gr.Textbox("Chapter 1.", elem_classes=["no-label"], scale=1)
							chapter1_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

						with gr.Row(elem_classes=["left-margin"]):
							chapter1_first_paragraph = gr.Textbox(placeholder="The first paragraph of the first chapter will be generated here", elem_classes=["no-label"])

						with gr.Row():
							gr.Textbox("Chapter 2.", elem_classes=["no-label"], scale=1)
							chapter2_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

						with gr.Row():
							gr.Textbox("Chapter 3.", elem_classes=["no-label"], scale=1)
							chapter3_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

						with gr.Row():
							gr.Textbox("Chapter 4.", elem_classes=["no-label"], scale=1)
							chapter4_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

						with gr.Row():
							gr.Slider(0.0, 2.0, 1.0, step=0.1, label="temperature")
							plot_gen_btn = gr.Button("gen plot", elem_classes=["control-button"])
							gr.Button("confirm", elem_classes=["control-button"])

				with gr.TabItem("story generation", idx=1):
					with gr.Tab("Chapter 1"):
						gr.Markdown("🔘&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️", elem_classes=["markdown-center", "small-big"])
						gr.Video("assets/recording.mp4", elem_classes=["no-label-gallery"])
						gr.Textbox(
								"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer interdum eleifend tincidunt. Vivamus dapibus, massa ut imperdiet condimentum, quam ipsum vehicula eros, a accumsan nisl metus at nisl. Nullam tortor nibh, vehicula sed tellus at, accumsan efficitur enim. Sed mollis purus vitae nisl ornare volutpat. In vitae tortor nec neque sagittis vehicula. In vestibulum velit eu lorem pulvinar dignissim. Donec eu sapien et sapien cursus pretium elementum eu urna. Proin lacinia ipsum maximus, commodo dui tempus, convallis tortor. Nulla sodales mi libero, nec eleifend eros interdum quis. Pellentesque nulla lectus, scelerisque et consequat vitae, blandit at ante. Sed nec …….",
								lines=12,
								elem_classes=["no-label", "small-big-textarea"]
						)

						with gr.Row():
							gr.Button("Action Choice 1", elem_classes=["control-button"])
							gr.Button("Action Choice 2", elem_classes=["control-button"])
							gr.Button("Action Choice 3", elem_classes=["control-button"])

					with gr.Tab("2"):
						gr.Video("assets/recording.mp4")

					with gr.Tab("3"):
						gr.Video("assets/recording.mp4")

					with gr.Tab("4"):
						gr.Video("assets/recording.mp4")

				with gr.TabItem("export", idx=2):
					gr.Markdown("hello")

		with gr.Column(scale=1):
			chatbot = gr.Chatbot(
				[], 
				avatar_images=("assets/user.png", "assets/ai.png"), 
				elem_id="chatbot", 
				elem_classes=["no-label-chatbot"])
			chat_input_txt = gr.Textbox(placeholder="enter...", interactive=True, elem_classes=["no-label"])

			with gr.Row():
				regen_btn = gr.Button("regen", interactive=False, elem_classes=["control-button"])
				clear_btn = gr.Button("clear", elem_classes=["control-button"])

	main_tabs.select(
		ui.update_on_main_tabs,
		inputs=[chat_state],
		outputs=[chat_mode, chatbot]
	)

	time_dd.select(
		ui.update_on_age,
		outputs=[place_dd, mood_dd, job_dd1, job_dd2, job_dd3, job_dd4]
	)

	gen_char_btn1.click(
		ui.gen_character_image,
		inputs=[
			gallery_images1, name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1, time_dd, place_dd, mood_dd, creative_dd1],
		outputs=[char_gallery1, gallery_images1]
	)

	gen_char_btn2.click(
		ui.gen_character_image,
		inputs=[gallery_images2, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2, time_dd, place_dd, mood_dd, creative_dd2],
		outputs=[char_gallery2, gallery_images2]
	)

	gen_char_btn3.click(
		ui.gen_character_image,
		inputs=[gallery_images3, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3, time_dd, place_dd, mood_dd, creative_dd3],
		outputs=[char_gallery3, gallery_images3]
	)

	gen_char_btn4.click(
		ui.gen_character_image,
		inputs=[gallery_images4, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4, time_dd, place_dd, mood_dd, creative_dd4],
		outputs=[char_gallery4, gallery_images4]
	)

	random_name_btn1.click(
		ui.get_random_name,
		inputs=[name_txt1, name_txt2, name_txt3, name_txt4],
		outputs=[name_txt1],
	)

	random_name_btn2.click(
		ui.get_random_name,
		inputs=[name_txt2, name_txt1, name_txt3, name_txt4],
		outputs=[name_txt2],
	)

	random_name_btn3.click(
		ui.get_random_name,
		inputs=[name_txt3, name_txt1, name_txt2, name_txt4],
		outputs=[name_txt3],
	)

	random_name_btn4.click(
		ui.get_random_name,
		inputs=[name_txt4, name_txt1, name_txt2, name_txt4],
		outputs=[name_txt4],
	)

	plot_gen_btn.click(
		ui.plot_gen,
		inputs= [
			time_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs = [chapter1_title, chapter2_title, chapter3_title, chapter4_title]
	).then(
		ui.first_paragrph_gen,
		inputs= [
			time_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
			chapter1_title, chapter2_title, chapter3_title, chapter4_title
		],
		outputs = [chapter1_first_paragraph]
	)

	chat_input_txt.submit(
		ui.chat,
		inputs=[
			chat_input_txt, chat_mode, chat_state,
			time_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
			chapter1_title, chapter1_first_paragraph,chapter2_title, chapter3_title, chapter4_title
		],
		outputs=[chat_input_txt, chat_state, chatbot, regen_btn]
	)
 
	regen_btn.click(
		ui.rollback_last_ui,
		inputs=[chatbot], outputs=[chatbot]
	).then(
		ui.chat_regen,
		inputs=[chat_mode, chat_state],
		outputs=[chat_state, chatbot]		
	)
 
	clear_btn.click(
		ui.chat_reset,
		inputs=[chat_mode, chat_state],
		outputs=[chat_input_txt, chat_state, chatbot, regen_btn]
	)

demo.launch(share=True)

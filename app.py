import copy
import random

import gradio as gr

from constants.css import STYLE
from constants.init_values import (
	times, places, moods, jobs, ages, mbtis, random_names, personalities, default_character_images, styles
)

from interfaces import ui, chat_ui, plot_gen_ui, story_gen_ui 
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

	gr.Markdown("### 🌐 World setup")
	with gr.Accordion("determine when, where, and asmosphere", open=True) as world_setup_section:
		with gr.Row():
			with gr.Column():
				time_dd = gr.Dropdown(label="time", choices=times, value=times[0], interactive=True, elem_classes=["center-label"])
			with gr.Column():
				place_dd = gr.Dropdown(label="place", choices=places["Middle Ages"], value=places["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])
			with gr.Column():
				mood_dd = gr.Dropdown(label="mood", choices=moods["Middle Ages"], value=moods["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])
	
		world_setup_confirm_btn = gr.Button("Confirm", elem_classes=["wrap", "control-button"])

	gr.Markdown("### 👥 Character setup")
	with gr.Accordion("determine four characters' traits", open=False) as character_setup_section:
		with gr.Tab("main character"):
			char_gallery1 = gr.Gallery(value=default_character_images, height=256, preview=True)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
				name_txt1 = gr.Textbox(random_names[0], elem_classes=["no-label"], scale=3)
				random_name_btn1 = gr.Button("🗳️", elem_classes=["wrap", "control-button", "left-margin"], scale=1)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("age", elem_classes=["markdown-left"], scale=3)
				age_dd1 = gr.Dropdown(label=None, choices=ages, value=ages[0], elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("mbti", elem_classes=["markdown-left"], scale=3)
				mbti_dd1 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[0], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("nature", elem_classes=["markdown-left"], scale=3)
				personality_dd1 = gr.Dropdown(label=None, choices=personalities, value=personalities[0], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("job", elem_classes=["markdown-left"], scale=3)
				job_dd1 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
				creative_dd1 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			gen_char_btn1 = gr.Button("gen character", elem_classes=["wrap", "control-button"])

		with gr.Tab("side character 1"):
			char_gallery2 = gr.Gallery(value=default_character_images, height=256, preview=True)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
				name_txt2 = gr.Textbox(random_names[1], elem_classes=["no-label"], scale=3)
				random_name_btn2 = gr.Button("🗳️", elem_classes=["wrap", "control-button", "left-margin"], scale=1)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("age", elem_classes=["markdown-left"], scale=3)
				age_dd2 = gr.Dropdown(label=None, choices=ages, value=ages[1], elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("mbti", elem_classes=["markdown-left"], scale=3)
				mbti_dd2 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[1], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("nature", elem_classes=["markdown-left"], scale=3)
				personality_dd2 = gr.Dropdown(label=None, choices=personalities, value=personalities[1], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("job", elem_classes=["markdown-left"], scale=3)
				job_dd2 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][1], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
				creative_dd2 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			gen_char_btn2 = gr.Button("gen character", elem_classes=["wrap", "control-button"])

		with gr.Tab("side character 2"):
			char_gallery3 = gr.Gallery(value=default_character_images, height=256, preview=True)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
				name_txt3 = gr.Textbox(random_names[2], elem_classes=["no-label"], scale=3)
				random_name_btn3 = gr.Button("🗳️", elem_classes=["wrap", "control-button", "left-margin"], scale=1)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("age", elem_classes=["markdown-left"], scale=3)
				age_dd3 = gr.Dropdown(label=None, choices=ages, value=ages[2], elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("mbti", elem_classes=["markdown-left"], scale=3)
				mbti_dd3 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[2], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("nature", elem_classes=["markdown-left"], scale=3)
				personality_dd3 = gr.Dropdown(label=None, choices=personalities, value=personalities[2], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("job", elem_classes=["markdown-left"], scale=3)
				job_dd3 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][2], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
				creative_dd3 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			gen_char_btn3 = gr.Button("gen character", elem_classes=["wrap", "control-button"])

		with gr.Tab("side character 3"):
			char_gallery4 = gr.Gallery(value=default_character_images, height=256, preview=True)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
				name_txt4 = gr.Textbox(random_names[3], elem_classes=["no-label"], scale=3)
				random_name_btn4 = gr.Button("🗳️", elem_classes=["wrap", "control-button", "left-margin"], scale=1)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("age", elem_classes=["markdown-left"], scale=3)
				age_dd4 = gr.Dropdown(label=None, choices=ages, value=ages[3], elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("mbti", elem_classes=["markdown-left"], scale=3)
				mbti_dd4 = gr.Dropdown(label=None, choices=mbtis, value=mbtis[3], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("nature", elem_classes=["markdown-left"], scale=3)
				personality_dd4 = gr.Dropdown(label=None, choices=personalities, value=personalities[3], interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("job", elem_classes=["markdown-left"], scale=3)
				job_dd4 = gr.Dropdown(label=None, choices=jobs["Middle Ages"], value=jobs["Middle Ages"][3], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			with gr.Row(elem_classes=["no-gap"]):
				gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
				creative_dd4 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

			gen_char_btn4 = gr.Button("gen character", elem_classes=["wrap", "control-button"])

		character_setup_confirm_btn = gr.Button("Confirm", elem_classes=["wrap", "control-button"])

	gr.Markdown("### 💡 Plot setup")
	with gr.Accordion("generate chapter titles and each plot", open=False) as plot_setup_section:
		title = gr.Markdown("# Title Undetermined Yet", elem_classes=["markdown-center"])

		with gr.Row():
			gr.Textbox("Chapter 1.", elem_classes=["no-label"], scale=1)
			chapter1_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

		with gr.Row(elem_classes=["left-margin"]):
			chapter1_plot = gr.Textbox(placeholder="The plot of the first chapter will be generated here", lines=3, elem_classes=["no-label"])

		with gr.Row():
			gr.Textbox("Chapter 2.", elem_classes=["no-label"], scale=1)
			chapter2_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

		with gr.Row(elem_classes=["left-margin"]):
			chapter2_plot = gr.Textbox(placeholder="The plot of the second chapter will be generated here", lines=3, elem_classes=["no-label"])

		with gr.Row():
			gr.Textbox("Chapter 3.", elem_classes=["no-label"], scale=1)
			chapter3_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

		with gr.Row(elem_classes=["left-margin"]):
			chapter3_plot = gr.Textbox(placeholder="The plot of the third chapter will be generated here", lines=3, elem_classes=["no-label"])

		with gr.Row():
			gr.Textbox("Chapter 4.", elem_classes=["no-label"], scale=1)
			chapter4_title = gr.Textbox(placeholder="Placeholder", elem_classes=["no-label"], scale=5)

		with gr.Row(elem_classes=["left-margin"]):
			chapter4_plot = gr.Textbox(placeholder="The plot of the fourth chapter will be generated here", lines=3, elem_classes=["no-label"])

		with gr.Row():
			gr.Slider(0.0, 2.0, 1.0, step=0.1, label="temperature")
			plot_gen_btn = gr.Button("gen plot", elem_classes=["control-button"])

		plot_setup_confirm_btn = gr.Button("confirm", elem_classes=["control-button"])

	gr.Markdown("### ✍🏼 Story writing")
	with gr.Accordion("generate chapter titles and each plot", open=False) as story_writing_section:
		title_display = gr.Markdown("# Title Undetermined Yet", elem_classes=["markdown-center"])

		with gr.Tab("Chapter 1"):
			chapter1_title_display = gr.Markdown("## Title Undetermined Yet", elem_classes=["markdown-center"])

			chapter1_progress = gr.Markdown("🔘&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️&nbsp; &nbsp;⎯⎯⎯&nbsp; &nbsp;⚪️", elem_classes=["markdown-center", "small-big"])
			gr.Video("assets/recording.mp4", elem_classes=["no-label-gallery"])
			chapter1_content = gr.Textbox(
					"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer interdum eleifend tincidunt. Vivamus dapibus, massa ut imperdiet condimentum, quam ipsum vehicula eros, a accumsan nisl metus at nisl. Nullam tortor nibh, vehicula sed tellus at, accumsan efficitur enim. Sed mollis purus vitae nisl ornare volutpat. In vitae tortor nec neque sagittis vehicula. In vestibulum velit eu lorem pulvinar dignissim. Donec eu sapien et sapien cursus pretium elementum eu urna. Proin lacinia ipsum maximus, commodo dui tempus, convallis tortor. Nulla sodales mi libero, nec eleifend eros interdum quis. Pellentesque nulla lectus, scelerisque et consequat vitae, blandit at ante. Sed nec …….",
					lines=12,
					elem_classes=["no-label", "small-big-textarea"]
			)

			with gr.Row():
				chapter1_action1 = gr.Button("Action Choice 1", elem_classes=["control-button"])
				chapter1_action2 = gr.Button("Action Choice 2", elem_classes=["control-button"])
				chapter1_action3 = gr.Button("Action Choice 3", elem_classes=["control-button"])

		with gr.Tab("Chapter 2"):
			chapter2_title_display = gr.Markdown("## Title Undetermined Yet", elem_classes=["markdown-center"])

			gr.Video("assets/recording.mp4")

		with gr.Tab("Chapter 3"):
			chapter3_title_display = gr.Markdown("## Title Undetermined Yet", elem_classes=["markdown-center"])

			gr.Video("assets/recording.mp4")

		with gr.Tab("Chapter 4"):
			chapter4_title_display = gr.Markdown("## Title Undetermined Yet", elem_classes=["markdown-center"])

			gr.Video("assets/recording.mp4")

	gr.Markdown("### 📤 Export output")
	with gr.Accordion("generate chapter titles and each plot", open=False) as export_section:
		gr.Markdown("hello")

	with gr.Accordion("💬", open=False, elem_id="chat-section") as chat_section:
		with gr.Column(scale=1):
			chatbot = gr.Chatbot(
				[("hello", "world"), ("hello", "world"), ("hello", "world"), ("hello", "world"), ("hello", "world"), ("hello", "world"), ("hello", "world"), ("hello", "world")], 
				avatar_images=("assets/user.png", "assets/ai.png"), 
				elem_id="chatbot", 
				elem_classes=["no-label-chatbot"])
			chat_input_txt = gr.Textbox(placeholder="enter...", interactive=True, elem_id="chat-input", elem_classes=["no-label"])

			with gr.Row(elem_id="chat-buttons"):
				regen_btn = gr.Button("regen", interactive=False, elem_classes=["control-button"])
				clear_btn = gr.Button("clear", elem_classes=["control-button"])

	world_setup_confirm_btn.click(
		lambda: (
			gr.Accordion.update(open=False), 
			gr.Accordion.update(open=True),
		),
		inputs=None,
		outputs=[world_setup_section, character_setup_section]
	)

	character_setup_confirm_btn.click(
		lambda: (
			gr.Accordion.update(open=False), 
			gr.Accordion.update(open=True),
		),
		inputs=None,
		outputs=[character_setup_section, plot_setup_section]
	)

	plot_setup_confirm_btn.click(
		lambda: (
			gr.Accordion.update(open=False), 
			gr.Accordion.update(open=True),
		),
		inputs=None,
		outputs=[plot_setup_section, story_writing_section]
	)

	# main_tabs.select(
	# 	ui.update_on_main_tabs,
	# 	inputs=[chat_state],
	# 	outputs=[chat_mode, chatbot]
	# )

	#### Setups

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
 
	### Plot generation

	plot_gen_btn.click(
		plot_gen_ui.plot_gen,
		inputs= [
			time_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs = [
			title,
    		chapter1_title, chapter2_title, chapter3_title, chapter4_title,
      		chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot
    	]
	)
	### Story generation
 
	# chapter1_action1.click(
	# 	story_gen_ui.next_paragraph_gen,
	# 	inputs = [
    #   		chapter1_action1,
	# 		chapter1_progress,
	# 		time_dd, place_dd, mood_dd, 
	# 		name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
	# 		name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
	# 		name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
	# 		name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
	# 		chapter1_title, chapter2_title, chapter3_title, chapter4_title, chapter1_content
	# 	],
	# 	outputs = [chapter1_progress, chapter1_content, chapter1_action1, chapter1_action2, chapter1_action3]
	# )
 
	### Chatbot

	chat_input_txt.submit(
		chat_ui.chat,
		inputs=[
			chat_input_txt, chat_mode, chat_state,
			time_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
			chapter1_title, chapter2_title, chapter3_title, chapter4_title,
			chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot
		],
		outputs=[chat_input_txt, chat_state, chatbot, regen_btn]
	)
 
	regen_btn.click(
		chat_ui.rollback_last_ui,
		inputs=[chatbot], outputs=[chatbot]
	).then(
		chat_ui.chat_regen,
		inputs=[chat_mode, chat_state],
		outputs=[chat_state, chatbot]		
	)
 
	clear_btn.click(
		chat_ui.chat_reset,
		inputs=[chat_mode, chat_state],
		outputs=[chat_input_txt, chat_state, chatbot, regen_btn]
	)

demo.launch()

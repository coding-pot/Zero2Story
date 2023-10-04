import copy
import random

import gradio as gr

from constants.css import STYLE
from constants.init_values import (
	genres, places, moods, jobs, ages, mbtis, random_names, personalities, default_character_images, styles
)
from constants import desc

from interfaces import (
    ui, chat_ui, story_gen_ui, view_change_ui, export_ui
)
from modules.palmchat import GradioPaLMChatPPManager

with gr.Blocks(css=STYLE) as demo:
	chat_mode = gr.State("plot_chat")

	chat_state = gr.State({
		"ppmanager_type": GradioPaLMChatPPManager(),
		"plot_chat": GradioPaLMChatPPManager(),
		"story_chat": GradioPaLMChatPPManager(),
		"export_chat": GradioPaLMChatPPManager(),
	})
 
	cur_cursor = gr.State(0)
	cursors = gr.State([])

	gallery_images1 = gr.State(default_character_images)
	gallery_images2 = gr.State(default_character_images)
	gallery_images3 = gr.State(default_character_images)
	gallery_images4 = gr.State(default_character_images)
 
	selected_main_char_image1 = gr.State(default_character_images[0])
	selected_side_char_image1 = gr.State(default_character_images[0])
	selected_side_char_image2 = gr.State(default_character_images[0])
	selected_side_char_image3 = gr.State(default_character_images[0])

	with gr.Column(visible=True) as pre_phase:
		gr.Markdown("# 📖 Zero2Story", elem_classes=["markdown-center"])
		gr.Markdown(desc.pre_phase_description, elem_classes=["markdown-justify"])
		pre_to_setup_btn = gr.Button("create a custom story", elem_classes=["wrap", "control-button"])

	with gr.Column(visible=False) as background_setup_phase:
		gr.Markdown("# 🌐 World setup", elem_classes=["markdown-center"])
		gr.Markdown(desc.background_setup_phase_description, elem_classes=["markdown-justify"])
		with gr.Row():
			with gr.Column():
				genre_dd = gr.Dropdown(label="genre", choices=genres, value=genres[0], interactive=True, elem_classes=["center-label"])
			with gr.Column():
				place_dd = gr.Dropdown(label="place", choices=places["Middle Ages"], value=places["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])
			with gr.Column():
				mood_dd = gr.Dropdown(label="mood", choices=moods["Middle Ages"], value=moods["Middle Ages"][0], allow_custom_value=True, interactive=True, elem_classes=["center-label"])
		
		with gr.Row():
			back_to_pre_btn = gr.Button("← back", elem_classes=["wrap", "control-button"], scale=1)
			world_setup_confirm_btn = gr.Button("character setup →", elem_classes=["wrap", "control-button"], scale=2)

	with gr.Column(visible=False) as character_setup_phase:
		gr.Markdown("# 👥 Character setup")
		gr.Markdown(desc.character_setup_phase_description, elem_classes=["markdown-justify"])
		with gr.Row():
			with gr.Column():
				gr.Checkbox(label="character include/enable", value=True, interactive=False)
				char_gallery1 = gr.Gallery(value=default_character_images, height=256, preview=True)

				with gr.Row(elem_classes=["no-gap"]):
					gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
					name_txt1 = gr.Textbox(random_names[0], elem_classes=["no-label"], scale=3)
					random_name_btn1 = gr.Button("🗳️", elem_classes=["wrap", "control-button-green", "left-margin"], scale=1)

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

				with gr.Row(elem_classes=["no-gap"], visible=False):
					gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
					creative_dd1 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

				gen_char_btn1 = gr.Button("gen character", elem_classes=["wrap", "control-button-green"])

			with gr.Column():
				side_char_enable_ckb1 = gr.Checkbox(label="character include/enable", value=False)
				char_gallery2 = gr.Gallery(value=default_character_images, height=256, preview=True)

				with gr.Row(elem_classes=["no-gap"]):
					gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
					name_txt2 = gr.Textbox(random_names[1], elem_classes=["no-label"], scale=3)
					random_name_btn2 = gr.Button("🗳️", elem_classes=["wrap", "control-button-green", "left-margin"], scale=1)

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

				with gr.Row(elem_classes=["no-gap"], visible=False):
					gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
					creative_dd2 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

				gen_char_btn2 = gr.Button("gen character", elem_classes=["wrap", "control-button-green"])

			with gr.Column():
				side_char_enable_ckb2 = gr.Checkbox(label="character include/enable", value=False)
				char_gallery3 = gr.Gallery(value=default_character_images, height=256, preview=True)

				with gr.Row(elem_classes=["no-gap"]):
					gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
					name_txt3 = gr.Textbox(random_names[2], elem_classes=["no-label"], scale=3)
					random_name_btn3 = gr.Button("🗳️", elem_classes=["wrap", "control-button-green", "left-margin"], scale=1)

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

				with gr.Row(elem_classes=["no-gap"], visible=False):
					gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
					creative_dd3 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

				gen_char_btn3 = gr.Button("gen character", elem_classes=["wrap", "control-button-green"])

			with gr.Column():
				side_char_enable_ckb3 = gr.Checkbox(label="character include/enable", value=False)
				char_gallery4 = gr.Gallery(value=default_character_images, height=256, preview=True)

				with gr.Row(elem_classes=["no-gap"]):
					gr.Markdown("name", elem_classes=["markdown-left"], scale=3)
					name_txt4 = gr.Textbox(random_names[3], elem_classes=["no-label"], scale=3)
					random_name_btn4 = gr.Button("🗳️", elem_classes=["wrap", "control-button-green", "left-margin"], scale=1)

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

				with gr.Row(elem_classes=["no-gap"], visible=False):
					gr.Markdown("style", elem_classes=["markdown-left"], scale=3)
					creative_dd4 = gr.Dropdown(choices=styles, value=styles[0], allow_custom_value=True, interactive=True, elem_classes=["no-label"], scale=4)

				gen_char_btn4 = gr.Button("gen character", elem_classes=["wrap", "control-button-green"])

		with gr.Row():
			back_to_background_setup_btn = gr.Button("← back", elem_classes=["wrap", "control-button"], scale=1)
			character_setup_confirm_btn = gr.Button("generate first stories →", elem_classes=["wrap", "control-button"], scale=2)

	gr.Markdown("### 💡 Plot setup", visible=False)
	with gr.Accordion("generate chapter titles and each plot", open=False, visible=False) as plot_setup_section:
		title = gr.Textbox("Title Undetermined Yet", elem_classes=["no-label", "font-big"])
		# plot = gr.Textbox(lines=10, elem_classes=["no-label", "small-big-textarea"])

		gr.Textbox("Rising action", elem_classes=["no-label"])
		with gr.Row(elem_classes=["left-margin"]):
			chapter1_plot = gr.Textbox(placeholder="The plot of the first chapter will be generated here", lines=3, elem_classes=["no-label"])

		gr.Textbox("Crisis", elem_classes=["no-label"])
		with gr.Row(elem_classes=["left-margin"]):  
			chapter2_plot = gr.Textbox(placeholder="The plot of the second chapter will be generated here", lines=3, elem_classes=["no-label"])

		gr.Textbox("Climax", elem_classes=["no-label"])
		with gr.Row(elem_classes=["left-margin"]):  
			chapter3_plot = gr.Textbox(placeholder="The plot of the third chapter will be generated here", lines=3, elem_classes=["no-label"])

		gr.Textbox("Falling action", elem_classes=["no-label"])
		with gr.Row(elem_classes=["left-margin"]):  
			chapter4_plot = gr.Textbox(placeholder="The plot of the fourth chapter will be generated here", lines=3, elem_classes=["no-label"])

		gr.Textbox("Denouement", elem_classes=["no-label"])
		with gr.Row(elem_classes=["left-margin"]):  
			chapter5_plot = gr.Textbox(placeholder="The plot of the fifth chapter will be generated here", lines=3, elem_classes=["no-label"])

		with gr.Row():
			plot_gen_temp = gr.Slider(0.0, 2.0, 1.0, step=0.1, label="temperature")
			plot_gen_btn = gr.Button("gen plot", elem_classes=["control-button"])

		plot_setup_confirm_btn = gr.Button("confirm", elem_classes=["control-button"])

	with gr.Column(visible=False) as writing_phase:
		gr.Markdown("# ✍🏼 Story writing")
		gr.Markdown(desc.story_generation_phase_description, elem_classes=["markdown-justify"])
  
		progress_comp = gr.Textbox(label=None, elem_classes=["no-label"], interactive=False)

		title_display = gr.Markdown("# Title Undetermined Yet", elem_classes=["markdown-center"], visible=False)
		subtitle_display = gr.Markdown("### Title Undetermined Yet", elem_classes=["markdown-center"], visible=False)

		with gr.Row():
			image_gen_btn = gr.Button("🏞️ Image", interactive=False, elem_classes=["control-button-green"])
			audio_gen_btn = gr.Button("🔊 Audio", interactive=False, elem_classes=["control-button-green"])
			img_audio_combine_btn = gr.Button("📀 Image + Audio", interactive=False, elem_classes=["control-button-green"])

		story_image = gr.Image(None, visible=False, type="filepath", interactive=False, elem_classes=["no-label-image-audio"])
		story_audio = gr.Audio(None, visible=False, type="filepath", interactive=False, elem_classes=["no-label-image-audio"])
		story_video = gr.Video(visible=False, interactive=False, elem_classes=["no-label-gallery"])

		story_progress = gr.Slider(
			1, 2, 1, step=1, interactive=True, 
			label="1/2", visible=False
		)

		story_content = gr.Textbox(
				"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer interdum eleifend tincidunt. Vivamus dapibus, massa ut imperdiet condimentum, quam ipsum vehicula eros, a accumsan nisl metus at nisl. Nullam tortor nibh, vehicula sed tellus at, accumsan efficitur enim. Sed mollis purus vitae nisl ornare volutpat. In vitae tortor nec neque sagittis vehicula. In vestibulum velit eu lorem pulvinar dignissim. Donec eu sapien et sapien cursus pretium elementum eu urna. Proin lacinia ipsum maximus, commodo dui tempus, convallis tortor. Nulla sodales mi libero, nec eleifend eros interdum quis. Pellentesque nulla lectus, scelerisque et consequat vitae, blandit at ante. Sed nec …….",
				lines=12,
				elem_classes=["no-label", "small-big-textarea"]
		)		

		action_types = gr.Radio(
			choices=[
				"continue current phase", "move to the next phase"
			],
			value="continue current phase",
			interactive=True,
			elem_classes=["no-label-radio"],
			visible=False,
		)

		with gr.Accordion("regeneration controls", open=False):
			with gr.Row():
				regen_actions_btn = gr.Button("Re-suggest actions", interactive=True, elem_classes=["control-button-green"])
				regen_story_btn = gr.Button("Re-suggest story and actions", interactive=True, elem_classes=["control-button-green"])
	
			custom_prompt_txt = gr.Textbox(placeholder="Re-suggest story and actions based on your own custom request", elem_classes=["no-label", "small-big-textarea"])

		with gr.Row():
			action_btn1 = gr.Button("Action Choice 1", interactive=False, elem_classes=["control-button-green"])
			action_btn2 = gr.Button("Action Choice 2", interactive=False, elem_classes=["control-button-green"])
			action_btn3 = gr.Button("Action Choice 3", interactive=False, elem_classes=["control-button-green"])

		custom_action_txt = gr.Textbox(placeholder="write your own custom action", elem_classes=["no-label", "small-big-textarea"], scale=3)

		with gr.Row():
			restart_from_story_generation_btn = gr.Button("← back", elem_classes=["wrap", "control-button"], scale=1)
			story_writing_done_btn = gr.Button("export your story →", elem_classes=["wrap", "control-button"], scale=2)

	with gr.Column(visible=False) as export_phase:
		gr.Markdown("# 📤 Story writing")
		gr.Markdown(desc.export_phase_description, elem_classes=["markdown-justify"])

		title_txt = gr.Textbox("Your Own Story", elem_classes=["no-label"])
		title_gen_btn = gr.Button("gnerate a title", elem_classes=["control-button-green"])

		export_progress = gr.Textbox("", elem_classes=["no-label"])
		export_btn = gr.Button("export as HTML page", elem_classes=["control-button-green"])

		restart_from_export_btn = gr.Button("start over", elem_classes=["wrap", "control-button"], scale=1)
		with gr.Row():
			restart_from_export_btn = gr.Button("← back", elem_classes=["wrap", "control-button"], scale=1)
			export_done_btn = gr.Button("view exported story →", elem_classes=["wrap", "control-button"], scale=2)

	with gr.Column(visible=False) as export_view_phase:
		export_html = gr.HTML()

		with gr.Row():
			restart_from_export_view_btn = gr.Button("← back", elem_classes=["wrap", "control-button"])

	with gr.Accordion("💬", open=False, elem_id="chat-section") as chat_section:
		with gr.Column(scale=1):
			chatbot = gr.Chatbot(
				[],
				avatar_images=("assets/user.png", "assets/ai.png"), 
				elem_id="chatbot", 
				elem_classes=["no-label-chatbot"])
			chat_input_txt = gr.Textbox(placeholder="enter...", interactive=True, elem_id="chat-input", elem_classes=["no-label"])

			with gr.Row(elem_id="chat-buttons"):
				regen_btn = gr.Button("regen", interactive=False, elem_classes=["control-button"])
				clear_btn = gr.Button("clear", elem_classes=["control-button"])

	pre_to_setup_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[pre_phase, background_setup_phase]
	)
 
	back_to_pre_btn.click(
		view_change_ui.back_to_previous_view,
		inputs=None,
		outputs=[pre_phase, background_setup_phase]
	)

	world_setup_confirm_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[background_setup_phase, character_setup_phase]
	)
 
	back_to_background_setup_btn.click(
		view_change_ui.back_to_previous_view,
		inputs=None,
		outputs=[background_setup_phase, character_setup_phase]		
	)
 
	restart_from_story_generation_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[pre_phase, writing_phase]		
	)

	story_writing_done_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[writing_phase, export_phase]
	)
 
	export_done_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[export_phase, export_view_phase]
	)

	character_setup_confirm_btn.click(
		view_change_ui.move_to_next_view,
		inputs=None,
		outputs=[character_setup_phase, writing_phase]
	).then(
		story_gen_ui.first_story_gen,
		inputs=[			
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			cursors, cur_cursor, story_content, story_progress, image_gen_btn, audio_gen_btn,
			story_image, story_audio, story_video
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)

	regen_actions_btn.click(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]		
	)
 
	regen_story_btn.click(
		story_gen_ui.update_story_gen,
		inputs=[
			cursors, cur_cursor,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,			
		],
		outputs=[
			cursors, cur_cursor, story_content, story_progress, image_gen_btn, audio_gen_btn
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)
 
	#### Setups

	genre_dd.select(
		ui.update_on_age,
		outputs=[place_dd, mood_dd, job_dd1, job_dd2, job_dd3, job_dd4]
	)

	gen_char_btn1.click(
		ui.gen_character_image,
		inputs=[
			gallery_images1, name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1, genre_dd, place_dd, mood_dd, creative_dd1],
		outputs=[char_gallery1, gallery_images1, selected_main_char_image1]
	)

	gen_char_btn2.click(
		ui.gen_character_image,
		inputs=[gallery_images2, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2, genre_dd, place_dd, mood_dd, creative_dd2],
		outputs=[char_gallery2, gallery_images2, selected_side_char_image1]
	)

	gen_char_btn3.click(
		ui.gen_character_image,
		inputs=[gallery_images3, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3, genre_dd, place_dd, mood_dd, creative_dd3],
		outputs=[char_gallery3, gallery_images3, selected_side_char_image2]
	)

	gen_char_btn4.click(
		ui.gen_character_image,
		inputs=[gallery_images4, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4, genre_dd, place_dd, mood_dd, creative_dd4],
		outputs=[char_gallery4, gallery_images4, selected_side_char_image3]
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
		inputs=[name_txt4, name_txt1, name_txt2, name_txt3],
		outputs=[name_txt4],
	)
 
	### Story generation
	story_content.input(
		story_gen_ui.update_story_content,
		inputs=[story_content, cursors, cur_cursor],
		outputs=[cursors],
	)

	image_gen_btn.click(
		story_gen_ui.image_gen,
		inputs=[
			genre_dd, place_dd, mood_dd, title, story_content, cursors, cur_cursor, story_audio
		],
		outputs=[
			story_image, img_audio_combine_btn, cursors, progress_comp,
		]
	)

	audio_gen_btn.click(
		story_gen_ui.audio_gen,
		inputs=[
			genre_dd, place_dd, mood_dd, title, story_content, cursors, cur_cursor, story_image
		],
		outputs=[story_audio, img_audio_combine_btn, cursors, progress_comp]
	)

	img_audio_combine_btn.click(
		story_gen_ui.video_gen,
		inputs=[
			story_image, story_audio, story_content, cursors, cur_cursor
		],
		outputs=[
			story_image, story_audio, story_video, cursors, progress_comp
		],
	)	

	story_progress.input(
		story_gen_ui.move_story_cursor,
		inputs=[
			story_progress, cursors
		],
		outputs=[
			cur_cursor,
			story_progress, 
			story_content,
			story_image, story_audio, story_video,
			action_btn1, action_btn2, action_btn3,
		]
	)

	action_btn1.click(
		lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
		inputs=None,
		outputs=[
			image_gen_btn, audio_gen_btn, img_audio_combine_btn
		]
	).then(
		story_gen_ui.next_story_gen,
		inputs=[
			cursors,
			action_btn1,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,	
		],
		outputs=[
			cursors, cur_cursor,
			story_content, story_progress,
			image_gen_btn, audio_gen_btn,
			story_image, story_audio, story_video
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)

	action_btn2.click(
		lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
		inputs=None,
		outputs=[
			image_gen_btn, audio_gen_btn, img_audio_combine_btn
		]
	).then(
		story_gen_ui.next_story_gen,
		inputs=[
			cursors,
			action_btn2,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,	
		],
		outputs=[
			cursors, cur_cursor,
			story_content, story_progress,
			image_gen_btn, audio_gen_btn,
			story_image, story_audio, story_video
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)

	action_btn3.click(
		lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
		inputs=None,
		outputs=[
			image_gen_btn, audio_gen_btn, img_audio_combine_btn
		]
	).then(
		story_gen_ui.next_story_gen,
		inputs=[
			cursors,
			action_btn3,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,	
		],
		outputs=[
			cursors, cur_cursor,
			story_content, story_progress,
			image_gen_btn, audio_gen_btn,
			story_image, story_audio, story_video
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)

	custom_action_txt.submit(
		lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
		inputs=None,
		outputs=[
			image_gen_btn, audio_gen_btn, img_audio_combine_btn
		]
	).then(
		story_gen_ui.next_story_gen,
		inputs=[
			cursors,
			custom_action_txt,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,	
		],
		outputs=[
			cursors, cur_cursor,
			story_content, story_progress,
			image_gen_btn, audio_gen_btn,
			story_image, story_audio, story_video
		]
	).then(
		story_gen_ui.actions_gen,
		inputs=[
			cursors,
			genre_dd, place_dd, mood_dd, 
			name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
		],
		outputs=[
			action_btn1, action_btn2, action_btn3, progress_comp
		]
	)

	### Chatbot

	# chat_input_txt.submit(
	# 	chat_ui.chat,
	# 	inputs=[
	# 		chat_input_txt, chat_mode, chat_state,
	# 		genre_dd, place_dd, mood_dd, 
	# 		name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
	# 		name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
	# 		name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
	# 		name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,
	# 		chapter1_title, chapter2_title, chapter3_title, chapter4_title,
	# 		chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot
	# 	],
	# 	outputs=[chat_input_txt, chat_state, chatbot, regen_btn]
	# )
 
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

	export_btn.click(
		export_ui.export,
		inputs=[
			title_txt,
			cursors, 
			selected_main_char_image1, name_txt1, age_dd1, mbti_dd1, personality_dd1, job_dd1,
			side_char_enable_ckb1, selected_side_char_image1, name_txt2, age_dd2, mbti_dd2, personality_dd2, job_dd2,
			side_char_enable_ckb2, selected_side_char_image2, name_txt3, age_dd3, mbti_dd3, personality_dd3, job_dd3,
			side_char_enable_ckb3, selected_side_char_image3, name_txt4, age_dd4, mbti_dd4, personality_dd4, job_dd4,			
		],
		outputs=[
			export_html
		]
	)

	char_gallery1.select(
		ui.update_selected_char_image,
		inputs=None,
		outputs=[selected_main_char_image1]
	)

	char_gallery2.select(
		ui.update_selected_char_image,
		inputs=None,
		outputs=[selected_side_char_image1]
	)

	char_gallery3.select(
		ui.update_selected_char_image,
		inputs=None,
		outputs=[selected_side_char_image2]
	)

	char_gallery4.select(
		ui.update_selected_char_image,
		inputs=None,
		outputs=[selected_side_char_image3]
	)

demo.queue().launch(share=True)

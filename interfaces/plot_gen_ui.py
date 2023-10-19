import re
import gradio as gr
from interfaces import utils
from modules import get_llm_factory

async def plot_gen(
	temperature,
	genre, place, mood,
	side_char_enable1, side_char_enable2, side_char_enable3,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	llm_type="PaLM"
):
	factory = get_llm_factory(llm_type)
	prompts = factory.create_prompt_manager().prompts
	llm_service = factory.create_llm_service()

	side_char_prompt = utils.add_side_character(
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
	prompt = prompts['plot_gen']['main_plot_gen'].format(
		genre=genre, place=place, mood=mood,
		main_char_name=main_char_name,
		main_char_job=main_char_job,
		main_char_age=main_char_age,
		main_char_personality=main_char_personality,
		side_char_placeholder=side_char_prompt,
	)
	
	print(f"generated prompt:\n{prompt}")
	parameters = llm_service.make_params(mode="text", temperature=temperature, top_k=40, top_p=1.0, max_output_tokens=4096)
	response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

	return (
		response_json['title'],
		f"## {response_json['title']}",
		response_json['outline']['rising action'],
		response_json['outline']['crisis'],
		response_json['outline']['climax'],
		response_json['outline']['falling action'],
		response_json['outline']['denouement'],
	)


async def first_story_gen(
	title, 
	rising_action, crisis, climax, falling_action, denouement,
	genre, place, mood,
	side_char_enable1, side_char_enable2, side_char_enable3,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
	cursors, cur_cursor,
	llm_type="PaLM"
):
	factory = get_llm_factory(llm_type)
	prompts = factory.create_prompt_manager().prompts
	llm_service = factory.create_llm_service()

	side_char_prompt = utils.add_side_character(
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
	prompt = prompts['plot_gen']['first_story_gen'].format(
		genre=genre, place=place, mood=mood,
		main_char_name=main_char_name,
		main_char_job=main_char_job,
		main_char_age=main_char_age,
		main_char_personality=main_char_personality,
		side_char_placeholder=side_char_prompt,
		title=title,
		rising_action=rising_action,
		crisis=crisis,
		climax=climax,
		falling_action=falling_action,
		denouement=denouement,
	)

	print(f"generated prompt:\n{prompt}")
	parameters = llm_service.make_params(mode="text", temperature=1.0, top_k=40, top_p=1.0, max_output_tokens=4096)
	response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

	chapter_title = response_json["chapter_title"]
	pattern = r"Chapter\s+\d+\s*[:.]"
	chapter_title = re.sub(pattern, "", chapter_title)

	cursors.append({
		"title": chapter_title,
		"plot_type": "rising action",
		"story": "\n\n".join(response_json["paragraphs"])
	})

	return (
		f"### {chapter_title} (\"rising action\")",
		"\n\n".join(response_json["paragraphs"]),
		cursors,
		cur_cursor, 
		gr.update(interactive=True),
		gr.update(interactive=True),
		gr.update(value=response_json["actions"][0], interactive=True),
		gr.update(value=response_json["actions"][1], interactive=True),
		gr.update(value=response_json["actions"][2], interactive=True),
	)
import gradio as gr
from interfaces import utils
from modules import palmchat

def _add_side_character(
	enable, prompt, cur_side_chars,
	name, age, mbti, personality, job
):
	if enable:
		prompt = prompt + f"""
side character{cur_side_chars}: {{
name: {name},
job: {job},
age: {age},
mbti: {mbti},
personality: {personality}
}}"""
		cur_side_chars = cur_side_chars + 1
		
	return prompt, cur_side_chars
	

async def plot_gen(
	temperature,
	time, place, mood,
	side_char_enable1, side_char_enable2, side_char_enable3,
	name1, age1, mbti1, personality1, job1,
	name2, age2, mbti2, personality2, job2,
	name3, age3, mbti3, personality3, job3,
	name4, age4, mbti4, personality4, job4,
):
	cur_side_chars = 1
	
	prompt = ("You are a world-renowned novelist and TRPG creator. You specialize in long, "
	"descriptive sentences and enigmatic plots. As you write, you need to follow Ronald To"
	"bias's plot theory. You also need to create a outline for your novel based on the inp"
	"ut we give you, and generate a title based on the outline. You must create the outlin"
	"e at least more tham 2000 words long. YOU MUST FOLLOW THESE RULES.\n"
	"Output template is as follows: ```json{\"title\": \"title\", \"outline\": \"outline\""
	"}```. DO NOT output anything other than JSON values. ONLY JSON is allowed."
	f"""
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

""")

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
	
	print(f"generated prompt:\n{prompt}")
	parameters = {
		'model': 'models/text-bison-001',
		'candidate_count': 1,
		'temperature': temperature,
		'top_k': 40,
		'top_p': 1,
		'max_output_tokens': 4096,
	}    	
	response_json = await utils.retry_until_valid_json(prompt, parameters=parameters)

	return (
		response_json['title'],
		f"## {response_json['title']}",
		response_json['outline']
	)


async def first_story_gen(
	title, plot,
	cursors, cur_cursor
):
	prompt = ("You are a world-renowned novelist and TRPG creator. You specialize in long, "
	"descriptive sentences and enigmatic plots. When writing, you must follow Ronald Tobia"
	"s's plot theory. You must tell a story based on a given plot. Your story must include"
	" descriptive sentences and dialog. Your story must be a minimum of 1500 words and a m"
	"aximum of 2500 words. At the end of the story, you must create 3 actions, each of whi"
	"ch must be different and affect the next story. YOU MUST FOLLOW THESE RULES.\n"
	"Output template is as follows: ```json{\"chapter_title\": \"chapter_title\", \"story\""
	": {{\"story\" : \"story\", \"action1\" : \"action1\", \"action2\" : \"action2\", \"act"
	"ion3\" : \"action3\"}}```. DO NOT output anything other than JSON values. ONLY JSON is"
	" allowed. The JSON key name should not be changed."
	f"""
title: {title}
outline: {plot}

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
		"title": response_json["chapter_title"],
		"plot_type": "rising action",
		"story": response_json["story"]["story"]
	})

	return (
		response_json["story"]["story"],
		cursors,
		cur_cursor, 
		gr.update(interactive=True),
		gr.update(interactive=True),
		gr.update(value=response_json["story"]["action1"], interactive=True),
		gr.update(value=response_json["story"]["action2"], interactive=True),
		gr.update(value=response_json["story"]["action3"], interactive=True),
	)
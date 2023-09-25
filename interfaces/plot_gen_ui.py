import gradio as gr
from interfaces import utils
from modules import palmchat

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
	prompt = f"""Write a title and an outline of a novel based on the background information below in Ronald Tobias's plot theory. The outline should follow the  "rising action", "crisis", "climax", "falling action", and "denouement" plot types. Each should be filled with a VERY detailed and descriptive at least two paragraphs of string. Randomly choose if the story goes optimistic or tragic.

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

JSON output:
{{
	"title": "string", 
	"outline": {{
		"rising action": "paragraphs of string", 
		"crisis": "paragraphs of string", 
		"climax": "paragraphs of string", 
		"falling action": "paragraphs of string", 
		"denouement": "paragraphs of string"
	}}
}}

background information:
- genre: {time}
- where: {place}
- mood: {mood}

main character
- name: {name1}
- job: {job1}
- age: {age1}
- mbti: {mbti1}
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

	prompt = prompt + "JSON output:\n"
	
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
		response_json['outline']['rising action'],
		response_json['outline']['crisis'],
		response_json['outline']['climax'],
		response_json['outline']['falling action'],
		response_json['outline']['denouement'],
	)


async def first_story_gen(
	title, plot,
	cursors, cur_cursor
):
	prompt = f"""Write the chapter title and the first few paragraphs of the "rising action" plot based on the background information below in Ronald Tobias's plot theory. Also, suggest three choosable actions to drive current story in different directions. The first few paragraphs should be filled with a VERY MUCH detailed and descriptive at least two paragraphs of string. 

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

JSON output:
{
	"chapter_title": "string",
	"paragraphs": ["string", "string", ...],
	"actions:": ["string", "string", "string"]
}

background information:
- genre: Middle Ages
- where: Royal Palace
- mood: Epic Adventure

main character
- name: Aaron
- job: Knight,
- age: 10s,
- mbti: ESTJ,
- personality: Optimistic

overall outline
- title: The Young Knight
- rising action: Aaron was a young knight in training at the Royal Palace. He was eager to prove himself and was always looking for ways to help his kingdom. One day, he heard that a group of bandits were terrorizing the countryside. He knew he had to do something, so he set out with a group of other knights to stop them.
- crisis: The knights tracked the bandits to their hideout, but they were outnumbered and outmatched. Just when it seemed like they were about to be defeated, Aaron came up with a plan. He distracted the bandits while the other knights snuck into the hideout and captured them.
- climax: The knights returned to the palace victorious, and Aaron was hailed as a hero. The king was so impressed that he promoted Aaron to the rank of captain and gave him his own knights to command.
- falling action: Aaron continued to serve the king faithfully for many years. He led his knights in many battles and always came out victorious. He was a true hero and an inspiration to all who knew him.
- denouement: Aaron eventually retired from the military and lived a long and happy life. He was loved by everyone who knew him and was remembered as one of the greatest knights who ever lived.

JSON output:
"""

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
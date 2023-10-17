import copy
import json
import string
import random

from modules import (
	palmchat, palm_prompts,
)

from pingpong.context import CtxLastWindowStrategy

def add_side_character_to_export(
	characters,	enable, img, 
	name, age, personality, job
):
	if enable:
		characters.append(
			{
				'img': img,
				'name': name
			}
		)

	return characters

def add_side_character(enable, name, age, personality, job):
	cur_side_chars = 1
	prompt = ""
	for idx in range(len(enable)):
		if enable[idx]:
			prompt += palm_prompts['story_gen']['add_side_character'].format(
										cur_side_chars=cur_side_chars,
										name=name[idx],
										job=job[idx],
										age=age[idx],
										personality=personality[idx]
									)
			cur_side_chars += 1
	return "\n" + prompt if prompt else ""

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def parse_first_json_code_snippet(code_snippet):
	json_parsed_string = None
	
	try:
		json_parsed_string = json.loads(code_snippet, strict=False)
	except:
		json_start_index = code_snippet.find('```json')
		json_end_index = code_snippet.find('```', json_start_index + 6)

		if json_start_index < 0 or json_end_index < 0:
			raise ValueError('No JSON code snippet found in string.')

		json_code_snippet = code_snippet[json_start_index + 7:json_end_index]
		json_parsed_string = json.loads(json_code_snippet, strict=False)
	finally:
		return json_parsed_string

async def retry_until_valid_json(prompt, parameters=None):
	response_json = None

	for _ in range(3):
		try:
			response, response_txt = await palmchat.gen_text(prompt, mode="text", parameters=parameters)
			print(response_txt)
		except Exception as e:
			print("PaLM API has withheld a response due to content safety concerns. Retrying...")
			continue
		
		try:
			response_json = parse_first_json_code_snippet(response_txt)
			break
		except:
			print("Parsing JSON failed. Retrying...")
			pass
	
	if len(response.filters) > 0:
		raise ValueError("PaLM API has withheld a response due to content safety concerns.")
	elif response_json is None:
		print("=== Failed to generate valid JSON response. ===")
		print(response_txt)
		raise ValueError("Failed to generate valid JSON response.")
			
	return response_json

def build_prompts(ppm, win_size=3):
	dummy_ppm = copy.deepcopy(ppm)
	lws = CtxLastWindowStrategy(win_size)
	return lws(dummy_ppm)

async def get_chat_response(prompt, ctx=None):
	parameters = {
		'model': 'models/chat-bison-001',
		'candidate_count': 1,
		'context': "" if ctx is None else ctx,
		'temperature': 1.0,
		'top_k': 50,
		'top_p': 0.9,
	}
	
	_, response_txt = await palmchat.gen_text(
		prompt, 
		parameters=parameters
	)

	return response_txt

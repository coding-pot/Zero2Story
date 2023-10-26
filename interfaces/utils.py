import copy
import json
import string
import random
import asyncio

from modules.llms import get_llm_factory

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

def add_side_character(enable, name, age, personality, job, llm_type="PaLM"):
	prompts = get_llm_factory(llm_type).create_prompt_manager().prompts

	cur_side_chars = 1
	prompt = ""
	for idx in range(len(enable)):
		if enable[idx]:
			prompt += prompts['story_gen']['add_side_character'].format(
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
	
	json_start_index = code_snippet.find('{')
	json_end_index = code_snippet.rfind('}')

	if json_start_index >= 0 and json_end_index >= 0:
		json_code_snippet = code_snippet[json_start_index:json_end_index+1]
		print(json_code_snippet)
		try:
			json_parsed_string = json.loads(json_code_snippet, strict=False)
		except:
			print("failed to parse string into JSON format")
			print("---------------------------------------")
			print(json_parsed_string)
	else:
		raise ValueError('No JSON code snippet found in string.')
	
	return json_parsed_string

async def retry_until_valid_json(prompt, llm_factory=None, parameters=None, context=None, examples=None, llm_type="PaLM", mode="text"):
	response_json = None
	if llm_factory is None:
		llm_factory = get_llm_factory(llm_type)
	llm_service = llm_factory.create_llm_service()

	for _ in range(3):
		try:
			if mode == "text":
				response, response_txt = await asyncio.wait_for(
						llm_service.gen_text(
							prompt, mode="text", 
							parameters=parameters
					),
					timeout=10
				)
			else:
				response, response_txt = await asyncio.wait_for(
						llm_service.gen_text(
							prompt, mode="chat", 
							parameters=parameters,
							context=context,
							examples=examples
					),
					timeout=20
				)
			print(response_txt)
		except asyncio.TimeoutError:
			raise TimeoutError(f"The response time for {llm_type} API exceeded the limit.")
		except Exception as e:
			print(f"{llm_type} API has encountered an error. Retrying...")
			continue
		
		try:
			response_json = parse_first_json_code_snippet(response_txt)
			if not response_json:
				print("Parsing JSON failed. Retrying...")
				continue
			else:
				break
		except:
			print("Parsing JSON failed. Retrying...")
			pass
	
	if len(response.filters) > 0:
		raise ValueError(f"{llm_type} API has withheld a response due to content safety concerns.")
	elif response_json is None:
		print("=== Failed to generate valid JSON response. ===")
		print(response_txt)
		raise ValueError("Failed to generate valid JSON response.")
			
	return response_json

def build_prompts(ppm, win_size=3):
	dummy_ppm = copy.deepcopy(ppm)
	lws = CtxLastWindowStrategy(win_size)
	return lws(dummy_ppm)

async def get_chat_response(prompt, ctx=None, llm_type="PaLM"):
	factory = get_llm_factory(llm_type)
	llm_service = factory.create_llm_service()
	parameters = llm_service.make_params(mode="chat", temperature=1.0, top_k=50, top_p=0.9)
	
	_, response_txt = await llm_service.gen_text(
		prompt, 
		parameters=parameters
	)

	return response_txt

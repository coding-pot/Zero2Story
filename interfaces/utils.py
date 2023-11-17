import copy
import json
import string
import random
import asyncio

from modules.llms import get_llm_factory
from modules.llms.palm_service import PaLMChatPPManager

from pingpong import PingPong
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

def build_title_gen_prompts(
	llm_mode, llm_factory, stories
):
	examples = None

	if llm_mode == "text":
		prompts = llm_factory.create_prompt_manager().prompts
	else:
		prompts = llm_factory.create_prompt_manager().chat_prompts

	if llm_mode == "text": 
		prompt = prompts['story_gen']['title'].format(stories=stories)
	else:
		examples =  prompts['story_gen']['examples']
		prompt = prompts['story_gen']['query']['title_prompt'].format(stories=stories)
  
		ppm = llm_factory.to_ppm("", [PingPong(prompt, "")])
		prompt = ppm.build_prompts()

	return examples, prompt

def add_side_character(prompts, enable, name, age, personality, job):
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

def build_actions_gen_prompts(
	llm_mode,
	llm_factory,
	summary, #only for test
	stories, #only for chat
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
):
	context = None
	examples = None
	ppm = None

	if llm_mode == "text":
		prompts = llm_factory.create_prompt_manager().prompts
	else:
		prompts = llm_factory.create_prompt_manager().chat_prompts

	side_char_prompt = add_side_character(
		prompts,
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)

	if llm_mode == "text": 
		prompt = prompts['story_gen']['actions_gen'].format(
					genre=genre, place=place, mood=mood,
					main_char_name=main_char_name,
					main_char_job=main_char_job,
					main_char_age=main_char_age,
					main_char_personality=main_char_personality,
					side_char_placeholder=side_char_prompt,
					summary=summary,
				)
	else:
		context = prompts['story_gen']['context'].format(
			genre=genre, place=place, mood=mood,
			main_char_name=main_char_name,
			main_char_job=main_char_job,
			main_char_age=main_char_age,
			main_char_personality=main_char_personality,
			side_char_placeholder=side_char_prompt,
		)
		examples =  prompts['story_gen']['examples']
		first_conversation = PingPong(
			prompts['story_gen']['query']['first_prompt'], 
			f"""{{"text": "{stories}"}}"""
		)
  
		ppm = llm_factory.to_ppm(context, [first_conversation])	
		prompt = prompts['story_gen']['query']['action_prompt']
		ppm.add_pingpong(PingPong(prompt, ""))
		prompt = ppm.build_prompts()

	return ppm, context, examples, prompt

def build_next_story_gen_prompts(
    llm_mode, llm_factory,
	action, stories, 
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,	
):
	context = ""
	examples = None
	ppm = None
 
	if llm_mode == "text":
		prompts = llm_factory.create_prompt_manager().prompts
	else:
		prompts = llm_factory.create_prompt_manager().chat_prompts

	side_char_prompt = add_side_character(
		prompts,
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
 
	if llm_mode == "text":
		prompt = prompts['story_gen']['next_story_gen'].format(
			genre=genre, place=place, mood=mood,
			main_char_name=main_char_name,
			main_char_job=main_char_job,
			main_char_age=main_char_age,
			main_char_personality=main_char_personality,
			side_char_placeholder=side_char_prompt,
			stories=stories, action=action,
		)
	else:
		context = prompts['story_gen']['context'].format(
			genre=genre, place=place, mood=mood,
			main_char_name=main_char_name,
			main_char_job=main_char_job,
			main_char_age=main_char_age,
			main_char_personality=main_char_personality,
			side_char_placeholder=side_char_prompt,
		)
		examples =  prompts['story_gen']['examples']
		first_conversation = PingPong(
			prompts['story_gen']['query']['first_prompt'], 
			f"""{{"text": "{stories}"}}"""
		)
  
		ppm = llm_factory.to_ppm(context, [first_conversation])
		prompt = prompts['story_gen']['query']['next_prompt'].format(action=action)
		ppm.add_pingpong(PingPong(prompt, ""))
  
	return context, examples, prompt, ppm

def build_first_story_gen_prompts(
    llm_mode,
	llm_factory,
	genre, place, mood,
	main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
):
	context = ""
	examples = None
	ppm = None
    
	if llm_mode == "text":
		prompts = llm_factory.create_prompt_manager().prompts
	else:
		prompts = llm_factory.create_prompt_manager().chat_prompts
    
	side_char_prompt = add_side_character(
		prompts,
		[side_char_enable1, side_char_enable2, side_char_enable3],
		[side_char_name1, side_char_name2, side_char_name3],
		[side_char_job1, side_char_job2, side_char_job3],
		[side_char_age1, side_char_age2, side_char_age3],
		[side_char_personality1, side_char_personality2, side_char_personality3],
	)
 
	if llm_mode == "text":
		prompt = prompts['story_gen']['first_story_gen'].format(
			genre=genre, place=place, mood=mood,
			main_char_name=main_char_name,
			main_char_job=main_char_job,
			main_char_age=main_char_age,
			main_char_personality=main_char_personality,
			side_char_placeholder=side_char_prompt,
		)
	else:
		context = prompts['story_gen']['context'].format(
			genre=genre, place=place, mood=mood,
			main_char_name=main_char_name,
			main_char_job=main_char_job,
			main_char_age=main_char_age,
			main_char_personality=main_char_personality,
			side_char_placeholder=side_char_prompt,
		)
		examples =  prompts['story_gen']['examples']
  		
		query = prompts['story_gen']['query']['first_prompt']
		pingpong = PingPong(query, "")
		ppm = llm_factory.to_ppm(context, [pingpong])
		prompt = ppm.build_prompts()
 
	return context, examples, prompt, ppm

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def find_json_code_snippet(raw_code_snippet):
	json_parsed_string = None
    
	json_start_index = raw_code_snippet.find('{')
	json_end_index = raw_code_snippet.rfind('}')

	if json_start_index >= 0 and json_end_index >= 0:
		json_code_snippet = raw_code_snippet[json_start_index:json_end_index+1]
		try:
			json_parsed_string = json.loads(json_code_snippet, strict=False)
		except:
			raise ValueError('failed to parse string into JSON format')
	else:
		raise ValueError('No JSON code snippet found in string.')

	return json_parsed_string

def parse_first_json_code_snippet(code_snippet):
	json_parsed_string = None
    
	if isinstance(code_snippet, list):
		for code_snippet_piece in code_snippet:
			try:
				json_parsed_string = find_json_code_snippet(code_snippet_piece)
				return json_parsed_string
			except:
				pass
	else:
		try:
			json_parsed_string = find_json_code_snippet(code_snippet)
		except Exception as e:
			print(e)
			raise ValueError()
	
	return json_parsed_string

async def retry_until_valid_json(prompt, llm_factory=None, parameters=None, context=None, examples=None, candidate=1, llm_type="PaLM", mode="text"):
	response_json = None
	if llm_factory is None:
		print("not exist factory.")
		llm_factory = get_llm_factory(llm_type)
	llm_service = llm_factory.create_llm_service()

	for _ in range(10):
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
							num_candidate=candidate,
							examples=[] if examples is None else examples
					),
					timeout=30
				)
		except asyncio.TimeoutError:
			raise TimeoutError(f"The response time for {llm_factory} API exceeded the limit.")
		except Exception as e:
			print(e)
			print(f"{llm_factory} API has encountered an error. Retrying...")
			continue
		
		try:
			response_json = parse_first_json_code_snippet(response_txt)
			if not response_json:
				print("1. Parsing JSON failed. Retrying...")
				continue
			else:
				break
		except:
			print("2. Parsing JSON failed. Retrying...")
			pass
	
	# if len(response.filters) > 0:
		# raise ValueError(f"{llm_type} API has withheld a response due to content safety concerns.")
	if response_json is None:
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

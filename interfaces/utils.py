import copy
import json 

from modules import palmchat
from pingpong.context import CtxLastWindowStrategy

def parse_first_json_code_snippet(string):
  """Parses the first JSON code snippet in a string.

  Args:
    string: A string containing the JSON code snippet.

  Returns:
    A Python object representing the JSON code snippet.
  """

  json_start_index = string.find('```json')
  json_end_index = string.find('```', json_start_index + 6)

  if json_start_index < 0 or json_end_index < 0:
    raise ValueError('No JSON code snippet found in string.')

  json_code_snippet = string[json_start_index + 7:json_end_index]

  return json.loads(json_code_snippet, strict=False)

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
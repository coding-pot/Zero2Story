import os
import toml
from pathlib import Path
import google.generativeai as palm_api

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt

from .utils import set_palm_api_key


# Set PaLM API Key
set_palm_api_key()

# Load PaLM Prompt Templates
palm_prompts = toml.load(Path('.') / 'assets' / 'palm_prompts.toml')

class PaLMChatPromptFmt(PromptFmt):
    @classmethod
    def ctx(cls, context):
        pass

    @classmethod
    def prompt(cls, pingpong, truncate_size):
        ping = pingpong.ping[:truncate_size]
        pong = pingpong.pong
        
        if pong is None or pong.strip() == "":
            return [
                {
                    "author": "USER",
                    "content": ping
                },
            ]
        else:
            pong = pong[:truncate_size]

            return [
                {
                    "author": "USER",
                    "content": ping
                },
                {
                    "author": "AI",
                    "content": pong
                },
            ]

class PaLMChatPPManager(PPManager):
    def build_prompts(self, from_idx: int=0, to_idx: int=-1, fmt: PromptFmt=PaLMChatPromptFmt, truncate_size: int=None):
        results = []
        
        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        for idx, pingpong in enumerate(self.pingpongs[from_idx:to_idx]):
            results += fmt.prompt(pingpong, truncate_size=truncate_size)

        return results    

class GradioPaLMChatPPManager(PaLMChatPPManager):
    def build_uis(self, from_idx: int=0, to_idx: int=-1, fmt: UIFmt=GradioChatUIFmt):
        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        results = []

        for pingpong in self.pingpongs[from_idx:to_idx]:
            results.append(fmt.ui(pingpong))

        return results    

async def gen_text(
    prompt,
    mode="chat", #chat or text
    parameters=None,
    use_filter=True
):
    if parameters is None:
        temperature = 1.0
        top_k = 40
        top_p = 0.95
        max_output_tokens = 1024
        
        # default safety settings
        safety_settings = [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},
                           {"category":"HARM_CATEGORY_TOXICITY","threshold":1},
                           {"category":"HARM_CATEGORY_VIOLENCE","threshold":2},
                           {"category":"HARM_CATEGORY_SEXUAL","threshold":2},
                           {"category":"HARM_CATEGORY_MEDICAL","threshold":2},
                           {"category":"HARM_CATEGORY_DANGEROUS","threshold":2}]
        if not use_filter:
            for idx, _ in enumerate(safety_settings):
                safety_settings[idx]['threshold'] = 4

        if mode == "chat":
            parameters = {
                'model': 'models/chat-bison-001',
                'candidate_count': 1,
                'context': "",
                'temperature': temperature,
                'top_k': top_k,
                'top_p': top_p,
            }
        else:
            parameters = {
                'model': 'models/text-bison-001',
                'candidate_count': 1,
                'temperature': temperature,
                'top_k': top_k,
                'top_p': top_p,
                'max_output_tokens': max_output_tokens,
                'safety_settings': safety_settings,
            }

    try:
        if mode == "chat":
            response = await palm_api.chat_async(**parameters, messages=prompt)
        else:
            response = palm_api.generate_text(**parameters, prompt=prompt)
    except:
        raise Exception("PaLM API is not available.")
    
    if use_filter and len(response.filters) > 0 and \
        response.filters[0]['reason'] == 2:
        response_txt = "your request is blocked for some reasons"
    else:
        if mode == "chat":
            response_txt = response.last
        else:
            response_txt = response.result
    
    return response, response_txt
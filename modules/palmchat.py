import os
import google.generativeai as palm_api

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt


palm_api_token = os.getenv("PALM_API_KEY")
if palm_api_token is None:
    raise ValueError("PaLM API Token is not set")
else:
    palm_api.configure(api_key=palm_api_token)

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
    parameters=None
):
    if parameters is None:
        temperature = 0.7
        top_k = 40
        top_p = 0.95
        max_output_tokens = 1024
        
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
            }            

    if mode == "chat":
        response = await palm_api.chat_async(**parameters, messages=prompt)
    else:
        response = palm_api.generate_text(**parameters, prompt=prompt)
    
    if len(response.filters) > 0 and \
        response.filters[0]['reason'] == 2:
        response_txt = "your request is blocked for some reasons"
    else:
        if mode == "chat":
            response_txt = response.last
        else:
            response_txt = response.result
    
    return response, response_txt
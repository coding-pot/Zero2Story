import os
import threading
import toml
from pathlib import Path
import google.generativeai as palm_api

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt

from modules.llms import (
    LLMFactory, PromptManager, LLMService
)

class PaLMFactory(LLMFactory):
    _palm_api_key = None

    def __init__(self, palm_api_key=None):
        if not PaLMFactory._palm_api_key and (palm_api_key is None or palm_api_key == ""):
            PaLMFactory.load_palm_api_key()
            assert PaLMFactory._palm_api_key, "PaLM API Key is missing."
            palm_api.configure(api_key=PaLMFactory._palm_api_key)
        
        if palm_api_key and palm_api_key != "":
            PaLMFactory._palm_api_key = palm_api_key

    def create_prompt_format(self):
        return PaLMChatPromptFmt()

    def create_prompt_manager(self, prompts_path: str=None, chat_prompts_path: str=None):
        return PaLMPromptManager(
            (prompts_path or Path('.') / 'prompts' / 'palm_prompts.toml'),
            (chat_prompts_path or Path('.') / 'prompts' / 'palm_chat_prompts.toml'),
        )
    
    def create_pp_manager(self):
        return PaLMChatPPManager()

    def create_ui_pp_manager(self):
        return GradioPaLMChatPPManager()
    
    def create_llm_service(self):
        return PaLMService()
    
    def to_ppm(self, context, pingpongs):
        ppm = PaLMChatPPManager()
        ppm.ctx = context
        ppm.pingpongs = pingpongs
        
        return ppm
    
    @classmethod
    def load_palm_api_key(cls, palm_api_key: str=None):
        if palm_api_key:
            cls._palm_api_key = palm_api_key
        else:
            palm_api_key = os.getenv("PALM_API_KEY")

            if palm_api_key is None:
                with open('.palm_api_key.txt', 'r') as file:
                    palm_api_key = file.read().strip()

            if not palm_api_key:
                raise ValueError("PaLM API Key is missing.")
            cls._palm_api_key = palm_api_key
    
    @property
    def palm_api_key(self):
        return PaLMFactory._palm_api_key
    
    @palm_api_key.setter
    def palm_api_key(self, palm_api_key: str):
        assert palm_api_key, "PaLM API Key is missing."
        PaLMFactory._palm_api_key = palm_api_key
        palm_api.configure(api_key=PaLMFactory._palm_api_key)


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

class PaLMPromptManager(PromptManager):
    _instance = None
    _lock = threading.Lock()
    _prompts = None
    _chat_prompts = None

    def __new__(cls, prompts_path, chat_prompts_path):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PaLMPromptManager, cls).__new__(cls)
                    cls._instance.prompts_path = prompts_path
                    cls._instance.chat_prompts_path = chat_prompts_path
        return cls._instance

    def reload_prompts(self):
        assert self._prompts_path, "Prompt path is missing."
        self._prompts = toml.load(self._prompts_path)

    def reload_chat_prompts(self):
        assert self._chat_prompts_path, "Chat prompt path is missing."
        self._chat_prompts = toml.load(self._chat_prompts_path)

    @property
    def prompts_path(self):
        return self._prompts_path

    @property
    def chat_prompts_path(self):
        return self._chat_prompts_path
    
    @prompts_path.setter
    def prompts_path(self, prompts_path):
        self._prompts_path = prompts_path
        self.reload_prompts()

    @prompts_path.setter
    def chat_prompts_path(self, chat_prompts_path):
        self._chat_prompts_path = chat_prompts_path
        self.reload_chat_prompts()

    @property
    def prompts(self):
        if self._prompts is None:
            self.reload_prompts()
        return self._prompts

    @property
    def chat_prompts(self):
        if self._chat_prompts is None:
            self.reload_chat_prompts()
        return self._chat_prompts

class PaLMService(LLMService):
    def __init__(self):
        self._default_parameters_text = {
                        'model': 'models/text-bison-001',
                        'temperature': 0.7,
                        'candidate_count': 1,
                        'top_k': 40,
                        'top_p': 0.95,
                        'max_output_tokens': 1024,
                        'stop_sequences': [],
                        'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},
                                            {"category":"HARM_CATEGORY_TOXICITY","threshold":1},
                                            {"category":"HARM_CATEGORY_VIOLENCE","threshold":2},
                                            {"category":"HARM_CATEGORY_SEXUAL","threshold":2},
                                            {"category":"HARM_CATEGORY_MEDICAL","threshold":2},
                                            {"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
                    }
        self._default_parameters_chat = {
                        'model': 'models/chat-bison-001',
                        'temperature': 0.25,
                        'candidate_count': 1,
                        'top_k': 40,
                        'top_p': 0.95,
                    }


    def make_params(self, mode="chat",
                    temperature=None,
                    candidate_count=None,
                    top_k=None,
                    top_p=None,
                    max_output_tokens=None,
                    use_filter=True):
        parameters = None

        if mode == "chat":
            parameters = self._default_parameters_chat.copy()
        elif mode == "text":
            parameters = self._default_parameters_text.copy()
        
        if temperature is not None:
            parameters['temperature'] = temperature
        if candidate_count is not None:
            parameters['candidate_count'] = candidate_count
        if top_k is not None:
            parameters['top_k'] = top_k
        if max_output_tokens is not None and mode == "text":
            parameters['max_output_tokens'] = max_output_tokens
        if not use_filter and mode == "text":
            for idx, _ in enumerate(parameters['safety_settings']):
                parameters['safety_settings'][idx]['threshold'] = 4

        return parameters


    async def gen_text(
        self,
        prompt,
        mode="chat", #chat or text
        parameters=None,
        context=None, #chat only
        examples=None, #chat only
        num_candidate=1, #chat only
        use_filter=True,
    ):
        if parameters is None:
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
                    'candidate_count': num_candidate,
                    'context': context,
                    'examples': examples,
                    'temperature': 0.25,
                    'top_k': 40,
                    'top_p': 0.95,
                    # 'safety_settings': safety_settings,
                }
            else:
                parameters = {
                    'model': 'models/text-bison-001',
                    'candidate_count': 1,
                    'temperature': 1.0,
                    'top_k': 40,
                    'top_p': 0.95,
                    'max_output_tokens': 4096,
                    'safety_settings': safety_settings,
                }

        try:
            if mode == "chat":
                response = await palm_api.chat_async(**parameters, messages=prompt)
            else:
                response = palm_api.generate_text(**parameters, prompt=prompt)
        except:
            raise EnvironmentError("PaLM API is not available.")

        if use_filter and len(response.filters) > 0:
            raise Exception("PaLM API has withheld a response due to content safety concerns.")
        else:
            if mode == "chat":
                if num_candidate > 1:
                    response_txt = []
                    for candidate in response.candidates:
                        response_txt.append(candidate["content"])
                else:
                    response_txt = response.last    
            else:
                response_txt = response.result
        
        return response, response_txt
import os
import threading
import requests
import sseclient
import json
import toml
from pathlib import Path

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt

from modules.llms import (
    LLMFactory, PromptManager, LLMService
)

class LLaMAFactory(LLMFactory):
    def __init__(self, hf_llama_api_key=None):
        if not LLaMAFactory._hf_llama_api_key and (hf_llama_api_key is None or hf_llama_api_key == ""):
            LLaMAFactory.load_hf_llama_api_key()
            assert LLaMAFactory._hf_llama_api_key, "Hugging Face LLaMA API Key is missing."

        if hf_llama_api_key and hf_llama_api_key != "":
            LLaMAFactory._hf_llama_api_key = hf_llama_api_key

    def create_prompt_format(self):
        return LLaMAChatPromptFmt()

    def create_prompt_manager(self, prompts_path: str=None):
        return LLaMAPromptManager((prompts_path or Path('.') / 'prompts' / 'llama_prompts.toml'))
    
    def create_pp_manager(self):
        return LLaMAChatPPManager()

    def create_ui_pp_manager(self):
        return GradioLLaMAChatPPManager()
    
    def create_llm_service(self):
        return LLaMAService(hf_llama_api_key=LLaMAFactory._hf_llama_api_key)
    
    @classmethod
    def load_hf_llama_api_key(cls, hf_llama_api_key: str=None):
        if hf_llama_api_key:
            cls._hf_llama_api_key = hf_llama_api_key
        else:
            hf_llama_api_key = os.getenv("HF_LLAMA_API_KEY")

            if hf_llama_api_key is None:
                with open('.hf_llama_api_key.txt', 'r') as file:
                    hf_llama_api_key = file.read().strip()

            if not hf_llama_api_key:
                raise ValueError("Hugging Face LlaMA API Key is missing.")
            cls._hf_llama_api_key = hf_llama_api_key

class LLaMAChatPromptFmt(PromptFmt):
    @classmethod
    def ctx(cls, context):
        if context is None or context == "":
            return ""
        else:
            return f"""<<SYS>>
{context}
<</SYS>>
"""

    @classmethod
    def prompt(cls, pingpong, truncate_size):
        ping = pingpong.ping[:truncate_size]
        pong = "" if pingpong.pong is None else pingpong.pong[:truncate_size]
        return f"""[INST] {ping} [/INST] {pong}"""

class LLaMAChatPPManager(PPManager):
    def build_prompts(self, from_idx: int=0, to_idx: int=-1, fmt: PromptFmt=LLaMAChatPromptFmt, truncate_size: int=None):
        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        results = fmt.ctx(self.ctx)

        for idx, pingpong in enumerate(self.pingpongs[from_idx:to_idx]):
            results += fmt.prompt(pingpong, truncate_size=truncate_size)

        return results

class GradioLLaMAChatPPManager(LLaMAChatPPManager):
    def build_uis(self, from_idx: int=0, to_idx: int=-1, fmt: UIFmt=GradioChatUIFmt):
        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        results = []

        for pingpong in self.pingpongs[from_idx:to_idx]:
            results.append(fmt.ui(pingpong))

        return results

class LLaMAPromptManager(PromptManager):
    _instance = None
    _lock = threading.Lock()
    _prompts = None

    def __new__(cls, prompts_path):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LLaMAPromptManager, cls).__new__(cls)
                    cls._instance.load_prompts(prompts_path)
        return cls._instance

    def load_prompts(self, prompts_path):
        self._prompts_path = prompts_path
        self.reload_prompts()

    def reload_prompts(self):
        assert self.prompts_path, "Prompt path is missing."
        self._prompts = toml.load(self.prompts_path)

    @property
    def prompts_path(self):
        return self._prompts_path
    
    @prompts_path.setter
    def prompts_path(self, prompts_path):
        self._prompts_path = prompts_path
        self.reload_prompts()

    @property
    def prompts(self):
        if self._prompts is None:
            self.load_prompts()
        return self._prompts

class LLaMAService(LLMService):
    def __init__(self, hf_llama_api_key: str=None):
        self._hf_llama_api_key = None
        self._default_parameters_text = None
        self._default_parameters_chat = {
                        'temperature': 0.25,
                        'top_k': 50,
                        # 'top_p': 0.95,
                        'repetition_penalty': 1.2,
                        'do_sample': True,
                        'return_full_text': False
                    }
            
    def make_params(self, mode="chat",
                    temperature=None,
                    candidate_count=None,
                    top_k=None,
                    top_p=None,
                    max_output_tokens=None,
                    use_filter=False):
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
            parameters['max_new_tokens'] = max_output_tokens
        if not use_filter and mode == "text":
            for idx, _ in enumerate(parameters['safety_settings']):
                parameters['safety_settings'][idx]['threshold'] = 4

        return parameters
    
    async def gen_text(
        self,
        prompt,
        mode="chat", #chat or text
        parameters=None,
        use_filter=True,
        **kwargs
    ):
        stream_mode = False
        if "stream" in kwargs:
            stream_mode = kwargs['stream']
        
        if parameters is None:
            parameters = {
                'max_new_tokens': 512,
                'do_sample': True,
                'return_full_text': False,
                'temperature': 1.0,
                'top_k': 50,
                'repetition_penalty': 1.2
            }

        model = 'meta-llama/Llama-2-70b-chat-hf'
        url = f'https://api-inference.huggingface.co/models/{model}'
        headers={
            'Authorization': f'Bearer {self._hf_llama_api_key}',
            'Content-type': 'application/json'
        }
        data = {
            'inputs': prompt,
            'stream': stream_mode,
            'options': {
                'use_cache': False,
            },
            'parameters': parameters
        }

        r = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),
            stream=True
        )

        if stream_mode:
            client = sseclient.SSEClient(r)
            for event in client.events():
                yield json.loads(event.data)['token']['text']
        else:
            yield json.loads(r.text)[0]["generated_text"]
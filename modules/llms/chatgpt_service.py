import os
import threading
import toml
from pathlib import Path

from openai import OpenAI

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt

from modules.llms import (
    LLMFactory, PromptManager, LLMService
)


class ChatGPTFactory(LLMFactory):
    _openai_api_key = None
    _client = None

    def __init__(self, openai_api_key=None):
        if not ChatGPTFactory._openai_api_key and (openai_api_key is None or openai_api_key == ""):
            ChatGPTFactory.load_openai_api_key()
            assert ChatGPTFactory._openai_api_key, "OpenAI API Key is missing."
            ChatGPTFactory._client = OpenAI(api_key=ChatGPTFactory._openai_api_key, )

        if openai_api_key and openai_api_key != "":
            ChatGPTFactory._openai_api_key = openai_api_key

    def create_prompt_format(self):
        return ChatGPTPromptFmt()

    def create_prompt_manager(self, prompts_path: str = None, chat_prompts_path: str = None):
        return ChatGPTPromptManager(
            (prompts_path or Path('.') / 'prompts' / 'chatgpt_prompts.toml'),
            (chat_prompts_path or Path('.') / 'prompts' / 'chatgpt_chat_prompts.toml'),
        )

    def create_pp_manager(self):
        return ChatGPTPPManager()

    def create_ui_pp_manager(self):
        return GradioChatGPTPPManager()

    def create_llm_service(self):
        llm_service = ChatGPTService()
        llm_service.client = ChatGPTFactory._client
        return llm_service

    def to_ppm(self, context, pingpongs):
        ppm = ChatGPTPPManager()
        ppm.ctx = context
        ppm.pingpongs = pingpongs

        return ppm

    @classmethod
    def load_openai_api_key(cls, openai_api_key: str = None):
        if openai_api_key:
            cls._openai_api_key = openai_api_key
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")

            if openai_api_key is None:
                with open('.openai_api_key.txt', 'r') as file:
                    openai_api_key = file.read().strip()

            if not openai_api_key:
                raise ValueError("OpenAI API Key is missing.")
            cls._openai_api_key = openai_api_key

    @property
    def openai_api_key(self):
        return ChatGPTFactory._openai_api_key

    @openai_api_key.setter
    def openai_api_key(self, openai_api_key: str):
        assert openai_api_key, "OpenAI API Key is missing."
        ChatGPTFactory._openai_api_key = openai_api_key
        ChatGPTFactory._client = OpenAI(api_key=ChatGPTFactory._openai_api_key, )


class ChatGPTPromptManager(PromptManager):
    _instance = None
    _lock = threading.Lock()
    _prompts = None
    _chat_prompts = None

    def __new__(cls, prompts_path, chat_prompts_path):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ChatGPTPromptManager, cls).__new__(cls)
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


class ChatGPTPromptFmt(PromptFmt):
    @classmethod
    def ctx(cls, context):
        return {"role": "system", "content": context}

    @classmethod
    def prompt(cls, pingpong, truncate_size):
        ping = pingpong.ping[:truncate_size]
        pong = pingpong.pong

        if pong is None or pong.strip() == "":
            return [
                {
                    "role": "user",
                    "content": ping
                },
            ]
        else:
            pong = pong[:truncate_size]

            return [
                {
                    "role": "user",
                    "content": ping
                },
                {
                    "role": "assistant",
                    "content": pong
                },
            ]


class ChatGPTPPManager(PPManager):
    def build_prompts(self, from_idx: int = 0, to_idx: int = -1, fmt: PromptFmt = ChatGPTPromptFmt,
                      truncate_size: int = None):
        results = [fmt.ctx(self.ctx)]

        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        for idx, pingpong in enumerate(self.pingpongs[from_idx:to_idx]):
            results += fmt.prompt(pingpong, truncate_size=truncate_size)

        return results


class GradioChatGPTPPManager(ChatGPTPPManager):
    def build_uis(self, from_idx: int = 0, to_idx: int = -1, fmt: UIFmt = GradioChatUIFmt):
        if to_idx == -1 or to_idx >= len(self.pingpongs):
            to_idx = len(self.pingpongs)

        results = []

        for pingpong in self.pingpongs[from_idx:to_idx]:
            results.append(fmt.ui(pingpong))

        return results


class ChatGPTService(LLMService):
    def __init__(self):
        self._default_parameters_text = None
        self._default_parameters_chat = {
            'model': "gpt-3.5-turbo-1106",
            # 'candidate_count': num_candidate,
            'temperature': 1.0,
            'top_p': 0.95,
            'max_tokens': 1000,
            'stream': False
        }

    def make_params(self, mode="chat",
                    temperature=None,
                    # candidate_count=None,
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
        # if candidate_count is not None:
        # parameters['candidate_count'] = candidate_count
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
            mode="chat",  # chat or text
            parameters=None,
            context=None,  # chat only
            examples=None,  # chat only
            num_candidate=1,  # chat only
            use_filter=True,
    ):
        print("run chatgpt gen_text")
        if parameters is None:
            # if mode == "chat":
            parameters = {
                'model': "gpt-3.5-turbo-1106",
                # 'candidate_count': num_candidate,
                'temperature': 1.0,
                'top_p': 0.95,
                'max_tokens': 1000,
                'stream': False
            }

        response_chatgpt = self.client.chat.completions.create(
            model=parameters['model'],
            stream=parameters['stream'],
            temperature=parameters['temperature'],
            top_p=parameters['top_p'],
            frequency_penalty=0.0,
            presence_penalty=0.0,
            max_tokens=parameters['max_tokens'],
            response_format={"type": "json_object"},
            messages=prompt
        )

        print("------------------------------")
        print(response_chatgpt.choices[0].message.content)
        print("------------------------------")

        return response_chatgpt, response_chatgpt.choices[0].message.content

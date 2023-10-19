import os
import threading
import toml
from pathlib import Path

from pingpong import PingPong
from pingpong.pingpong import PPManager
from pingpong.pingpong import PromptFmt
from pingpong.pingpong import UIFmt
from pingpong.gradio import GradioChatUIFmt

from modules.llms import (
    LLMFactory,
    PromptFmt, PromptManager, PPManager, UIPPManager, LLMService
)

class ChatGPTFactory(LLMFactory):
    def __init__(self):
        pass

    def create_prompt_format(self):
        return ChatGPTChatPromptFmt()

    def create_prompt_manager(self, prompts_path: str=None):
        return ChatGPTPromptManager((prompts_path or Path('.') / 'prompts' / 'chatgpt_prompts.toml'))
    
    def create_pp_manager(self):
        return ChatGPTChatPPManager()

    def create_ui_pp_manager(self):
        return GradioChatGPTChatPPManager()
    
    def create_llm_service(self):
        return ChatGPTService()
    

class ChatGPTChatPromptFmt(PromptFmt):
    @classmethod
    def ctx(cls, context):
        pass

    @classmethod
    def prompt(cls, pingpong, truncate_size):
        pass


class ChatGPTPromptManager(PromptManager):
    _instance = None
    _lock = threading.Lock()
    _prompts = None

    def __new__(cls, prompts_path):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ChatGPTPromptManager, cls).__new__(cls)
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


class ChatGPTChatPPManager(PPManager):
    def build_prompts(self, from_idx: int=0, to_idx: int=-1, fmt: PromptFmt=None, truncate_size: int=None):
        pass


class GradioChatGPTChatPPManager(UIPPManager, ChatGPTChatPPManager):
    def build_uis(self, from_idx: int=0, to_idx: int=-1, fmt: UIFmt=GradioChatUIFmt):
        pass

class ChatGPTService(LLMService):
    async def gen_text(
        self,
        prompt,
        mode="chat", #chat or text
        parameters=None,
        use_filter=True
    ):
        pass
from abc import ABC, ABCMeta, abstractmethod

class LLMFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_prompt_format(self):
        pass

    @abstractmethod
    def create_prompt_manager(self):
        pass

    @abstractmethod
    def create_pp_manager(self):
        pass

    @abstractmethod
    def create_ui_pp_manager(self):
        pass
    
    @abstractmethod
    def create_llm_service(self):
        pass
    
    @abstractmethod
    def to_ppm(self, context, pingpongs):
        pass


class PromptFmt(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def ctx(cls, context):
        pass

    @classmethod
    @abstractmethod
    def prompt(cls, pingpong, truncate_size):
        pass


class PromptManager(ABC):
    @abstractmethod
    def reload_prompts(self):
        pass

    @abstractmethod
    def reload_chat_prompts(self):
        pass
    
    @property
    @abstractmethod
    def prompts_path(self):
        pass

    @property
    @abstractmethod
    def chat_prompts_path(self):
        pass
    
    @prompts_path.setter
    @abstractmethod
    def prompts_path(self, prompts_path):
        pass

    @prompts_path.setter
    @abstractmethod
    def chat_prompts_path(self, prompts_path):
        pass

    @property
    @abstractmethod
    def prompts(self):
        pass

    @property
    @abstractmethod
    def chat_prompts(self):
        pass

class LLMService(metaclass=ABCMeta):
    @abstractmethod
    def make_params(self, mode="chat",
                          temperature=None,
                          candidate_count=None,
                          top_k=None,
                          top_p=None,
                          max_output_tokens=None,
                          use_filter=True,
                          **kwargs):
        pass
    
    @abstractmethod
    async def gen_text(self, prompt, mode="chat", parameters=None, use_filter=True):
        pass

from modules.llms import *

def get_llm_factory(llm_type: str) -> 'PaLM':
    factory = None
    if llm_type.lower() == 'palm':
        factory = PaLMFactory()
    
    return factory

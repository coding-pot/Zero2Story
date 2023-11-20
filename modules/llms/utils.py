from modules.llms import *

def get_llm_factory(llm_type: str, api_key: str=None) -> 'PaLM':
    factory = None
    if llm_type.lower() == 'palm':
        factory = PaLMFactory(palm_api_key=api_key)
    elif llm_type.lower() == 'chatgpt':
        factory = ChatGPTFactory(openai_api_key=api_key)
    elif llm_type.lower() == 'llama2':
        factory = LLaMAFactory(hf_llama_api_key=api_key)

    print("change llm to ",factory)
    
    return factory

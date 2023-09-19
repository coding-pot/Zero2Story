from interfaces import utils
from modules import palmchat

from pingpong import PingPong

def rollback_last_ui(history):
    return history[:-1]

async def chat(
    user_input, chat_mode, chat_state,
    time, place, mood,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
    chapter1_title, chapter2_title, chapter3_title, chapter4_title,
    chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot
):
    chapter_title_ctx = ""
    if chapter1_title != "":
        chapter_title_ctx = f"""
chapter1 {{
    title: {chapter1_title},
    plot: {chapter1_plot}
}}

chapter2 {{
    title: {chapter2_title},
    plot: {chapter2_plot}
}}

chapter3 {{
    title: {chapter3_title},
    plot: {chapter3_plot}
}}

chapter4 {{
    title: {chapter4_title},
    plot: {chapter4_plot}
}}
"""

    ctx = f"""You are a professional writing advisor, especially specialized in developing ideas on plotting stories and creating characters. I provide when, where, and mood along with the rough description of one main character and three side characters. 

Give creative but not too long responses based on the following information.

when: {time}
where: {place}
mood: {mood}

main character: {{
name: {name1},
job: {job1},
age: {age1},
mbti: {mbti1},
personality: {personality1} 
}}

side character1: {{
name: {name2},
job: {job2},
age: {age2},
mbti: {mbti2},
personality: {personality2} 
}}

side character2: {{
name: {name3},
job: {job3},
age: {age3},
mbti: {mbti3},
personality: {personality3} 
}}

side character3: {{
name: {name4},
job: {job4},
age: {age4},
mbti: {mbti4},
personality: {personality4} 
}}

{chapter_title_ctx}
"""

    ppm = chat_state[chat_mode]
    ppm.ctx = ctx
    ppm.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = utils.build_prompts(ppm)

    response_txt = await utils.get_chat_response(prompt, ctx=ctx)
    ppm.replace_last_pong(response_txt)
    
    chat_state[chat_mode] = ppm

    return (
        "", 
        chat_state, 
        ppm.build_uis(), 
        gr.update(interactive=True)
    )

async def chat_regen(chat_mode, chat_state):
    ppm = chat_state[chat_mode]
    
    user_input = ppm.pingpongs[-1].ping
    ppm.pingpongs = ppm.pingpongs[:-1]
    ppm.add_pingpong(
        PingPong(user_input, '')
    )    
    prompt = utils.build_prompts(ppm)

    response_txt = await utils.get_chat_response(prompt, ctx=ppm.ctx)
    ppm.replace_last_pong(response_txt)
    
    chat_state[chat_mode] = ppm

    return (
        chat_state,
        ppm.build_uis()
    )

def chat_reset(chat_mode, chat_state):
    chat_state[chat_mode] = palmchat.GradioPaLMChatPPManager()

    return (
        "", 
        chat_state, 
        [], 
        gr.update(interactive=False)
    )
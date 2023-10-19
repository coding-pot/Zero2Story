import gradio as gr

from pingpong import PingPong

from interfaces import utils
from modules.llms import get_llm_factory

def rollback_last_ui(history):
    return history[:-1]


def add_side_character(enable, name, age, personality, job, llm_type='PaLM'):
    prompts = get_llm_factory(llm_type).create_prompt_manager().prompts

    cur_side_chars = 1
    prompt = ""
    for idx in range(len(enable)):
        if enable[idx]:
            prompt += prompts['chat_gen']['add_side_character'].format(
                                        cur_side_chars=cur_side_chars,
                                        name=name[idx],
                                        job=job[idx],
                                        age=age[idx],
                                        personality=personality[idx]
                                    )
            cur_side_chars += 1
    return "\n" + prompt if prompt else ""


def add_chapter_title_ctx(chapter_title, chapter_plot, llm_type='PaLM'):
    prompts = get_llm_factory(llm_type).create_prompt_manager().prompts

    title_idx = 1
    prompt = ""
    for idx in range(len(chapter_title)):
        if chapter_title[idx] :
            prompt += prompts['chat_gen']['chapter_title_ctx'].format(
                                        title_idx=title_idx,
                                        chapter_title=chapter_title[idx],
                                        chapter_plot=chapter_plot[idx],
                                    )
            title_idx += 1
    return "\n" + prompt if prompt else ""


async def chat(
    user_input, chat_mode, chat_state,
    genre, place, mood,
    main_char_name, main_char_age, main_char_personality, main_char_job,
    side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
    side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
    side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
    chapter1_title, chapter2_title, chapter3_title, chapter4_title,
    chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot,
    side_char_enable1, side_char_enable2, side_char_enable3,
    llm_type='PaLM',
):
    prompts = get_llm_factory(llm_type).create_prompt_manager().prompts

    chapter_title_ctx = add_chapter_title_ctx(
        [chapter1_title, chapter2_title, chapter3_title, chapter4_title],
        [chapter1_plot, chapter2_plot, chapter3_plot, chapter4_plot],
    )
    side_char_prompt = add_side_character(
        [side_char_enable1, side_char_enable2, side_char_enable3],
        [side_char_name1, side_char_name2, side_char_name3],
        [side_char_job1, side_char_job2, side_char_job3],
        [side_char_age1, side_char_age2, side_char_age3],
        [side_char_personality1, side_char_personality2, side_char_personality3],
    )
    prompt = prompts['chat_gen']['chat_context'].format(
        genre=genre, place=place, mood=mood,
        main_char_name=main_char_name,
        main_char_job=main_char_job,
        main_char_age=main_char_age,
        main_char_personality=main_char_personality,
        side_char_placeholder=side_char_prompt,
        chapter_title_placeholder=chapter_title_ctx,
    )

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

def chat_reset(chat_mode, chat_state, llm_type='PaLM'):
    factory = get_llm_factory(llm_type)

    chat_state[chat_mode] = factory.create_ui_pp_manager()

    return (
        "", 
        chat_state, 
        [], 
        gr.update(interactive=False)
    )
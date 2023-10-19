import gradio as gr
from templates import parser
from interfaces import utils
from modules.llms import get_llm_factory

template_file = "templates/basic.jinja"

async def title_gen(cursors, llm_type="PaLM"):
    stories = ""
    for cursor in cursors:
        stories = stories + cursor["story"]
    
    factory = get_llm_factory(llm_type)
    prompts = factory.create_prompt_manager().prompts
    llm_service = factory.create_llm_service()

    prompt = prompts['story_gen']['title'].format(stories=stories)

    parameters = llm_service.make_params(mode="text", temperature=0.7, top_k=40, top_p=1.0, max_output_tokens=4096)
    _, title = await llm_service.gen_text(prompt, mode="text", parameters=parameters)
    return title

def export(
    title, cursors,
	main_char_img, main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_img1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_img2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_img3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,    
):
    print(main_char_img)
    characters = [
        {
            'img': main_char_img,
            'name': main_char_name,
        }
    ]
    utils.add_side_character_to_export(
        characters, side_char_enable1, side_char_img1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1
    )
    utils.add_side_character_to_export(
        characters, side_char_enable2, side_char_img2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2
    )
    utils.add_side_character_to_export(
        characters, side_char_enable3, side_char_img3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3
    )

    html_as_string = parser.gen_from_file(
        template_file,
        kwargs={
            "title": title,
            "characters": characters,
            "items": cursors
        }
    )

    return html_as_string

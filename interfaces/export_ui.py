import gradio as gr
from templates import parser
from interfaces import utils

template_file = "templates/basic.jinja"

def title_gen():
    return "hello world"

def export(
    title, cursors,
	main_char_img, main_char_name, main_char_age, main_char_mbti, main_char_personality, main_char_job,
	side_char_enable1, side_char_img1, side_char_name1, side_char_age1, side_char_mbti1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_img2, side_char_name2, side_char_age2, side_char_mbti2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_img3, side_char_name3, side_char_age3, side_char_mbti3, side_char_personality3, side_char_job3,    
):
    characters = [
        {
            'img': main_char_img['name'],
            'name': main_char_name,
        }
    ]
    utils.add_side_character_to_export(
        side_char_enable1, side_char_img1['name'], side_char_name1, side_char_age1, side_char_mbti1, side_char_personality1, side_char_job1
    )
    utils.add_side_character_to_export(
        side_char_enable2, side_char_img2['name'], side_char_name2, side_char_age2, side_char_mbti2, side_char_personality2, side_char_job2
    )
    utils.add_side_character_to_export(
        side_char_enable3, side_char_img3['name'], side_char_name3, side_char_age3, side_char_mbti3, side_char_personality3, side_char_job3
    )

    html_as_string = parser.gen_from_file(
        template_file,
        kwargs={
            "characters": characters,
            "items": cursors
        }
    )

    return html_as_string
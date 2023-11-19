import os
import copy
import shutil
import gradio as gr
from templates import parser
from interfaces import utils
from modules.llms import get_llm_factory

template_file = "templates/basic.jinja"
export_template_file = "templates/basic_export.jinja"

async def title_gen(
    llm_factory, llm_mode, cursors
):
    stories = ""
    for cursor in cursors:
        stories = stories + cursor["story"]
    
    examples, prompt = utils.build_title_gen_prompts(llm_mode, llm_factory, stories)
    print(f"generated prompt export_ui:\n{prompt}")

    try:
        if llm_mode == "text":
            llm_service = llm_factory.create_llm_service()
            _, title = await llm_service.gen_text(prompt, mode="text")
        else:
            parsing_key = "title"
            res_json = await utils.retry_until_valid_json(
				prompt=prompt, llm_factory=llm_factory, examples=examples, mode="chat", candidate=8,
            )
            title = res_json[parsing_key]

    except Exception as e:
        raise gr.Error(e)    
    
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

def generate_zip(
    title, cursors,
	main_char_img, main_char_name, main_char_age, main_char_personality, main_char_job,
	side_char_enable1, side_char_img1, side_char_name1, side_char_age1, side_char_personality1, side_char_job1,
	side_char_enable2, side_char_img2, side_char_name2, side_char_age2, side_char_personality2, side_char_job2,
	side_char_enable3, side_char_img3, side_char_name3, side_char_age3, side_char_personality3, side_char_job3,
):
    base_name = utils.id_generator(size=10)
    output_filename = base_name
    base_foldername = base_name
    asset_foldername = f"{base_foldername}/assets"
    html_filename = f"{base_foldername}/output.html"
    
    # create temporary folder to be compressed
    os.mkdir(base_foldername)
    os.mkdir(asset_foldername)
    
    # copy assets to asset_foldername
    # - copy images of the characters
    main_char_img_copy =  f"{asset_foldername}/{os.path.basename(main_char_img)}"
    side_char_img1_copy = f"{asset_foldername}/{os.path.basename(side_char_img1)}"
    side_char_img2_copy = f"{asset_foldername}/{os.path.basename(side_char_img2)}"
    side_char_img3_copy = f"{asset_foldername}/{os.path.basename(side_char_img3)}"
    
    shutil.copyfile(main_char_img, main_char_img_copy)
    if side_char_enable1:
        shutil.copyfile(side_char_img1, side_char_img1_copy)
    if side_char_enable2:
        shutil.copyfile(side_char_img2, side_char_img2_copy)
    if side_char_enable3:
        shutil.copyfile(side_char_img3, side_char_img3_copy)
        
    # - create character info based on copies
    characters_copy = [
        {
            'img': os.path.join(*(main_char_img_copy.split(os.path.sep)[1:])),
            'name': main_char_name,
        }
    ]
    utils.add_side_character_to_export(
        characters_copy, side_char_enable1, 
        os.path.join(*(side_char_img1_copy.split(os.path.sep)[1:])), 
        side_char_name1, side_char_age1, side_char_personality1, side_char_job1
    )
    utils.add_side_character_to_export(
        characters_copy, side_char_enable2, 
        os.path.join(*(side_char_img2_copy.split(os.path.sep)[1:])),
        side_char_name2, side_char_age2, side_char_personality2, side_char_job2
    )
    utils.add_side_character_to_export(
        characters_copy, side_char_enable3, 
        os.path.join(*(side_char_img3_copy.split(os.path.sep)[1:])),
        side_char_name3, side_char_age3, side_char_personality3, side_char_job3
    )
    
    # - copy any medias in the cursors(video, audio, img)
    cursors_copy = copy.deepcopy(cursors)
    for cursor in cursors_copy:
        if "video" in cursor:
            video_filename = cursor["video"]
            video_filename_copy = f"{asset_foldername}/{os.path.basename(video_filename)}"
            shutil.copyfile(video_filename, video_filename_copy)
            cursor["video"] = os.path.join(*(video_filename_copy.split(os.path.sep)[1:]))
        
        if "audio" in cursor:
            audio_filename = cursor["audio"]
            audio_filename_copy = f"{asset_foldername}/{os.path.basename(audio_filename)}"
            shutil.copyfile(audio_filename, audio_filename_copy)
            cursor["audio"] = os.path.join(*(audio_filename_copy.split(os.path.sep)[1:]))
        
        if "img" in cursor:
            img_filename = cursor["img"]
            img_filename_copy = f"{asset_foldername}/{os.path.basename(img_filename)}"
            shutil.copyfile(img_filename, img_filename_copy)
            cursor["img"] = os.path.join(*(img_filename_copy.split(os.path.sep)[1:]))

    # save constructed HTML as file
    html_as_string = parser.gen_from_file(
        export_template_file,
        kwargs={
            "title": title,
            "characters": characters_copy,
            "items": cursors_copy
        }
    )
    
    html_file = open(html_filename, "w")
    _ = html_file.write(html_as_string)
    html_file.close()
    
    # compress
    shutil.make_archive(output_filename, 'tar', base_foldername)
    
    # delete temporary directory
    shutil.rmtree(base_foldername)
    
    return gr.update(
        value=f"{output_filename}.tar",
        visible=True
    )
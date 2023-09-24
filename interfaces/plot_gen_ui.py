from interfaces import utils
from modules import palmchat

def _add_side_character(
    enable, prompt, cur_side_chars,
    name, age, mbti, personality, job
):
    if enable:
        prompt = prompt + f"""
side character{cur_side_chars}: {{
name: {name},
job: {job},
age: {age},
mbti: {mbti},
personality: {personality}
}}"""
        
    return prompt, cur_side_chars
    

async def plot_gen(
    time, place, mood,
    side_char_enable1, side_char_enable2, side_char_enable3,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
):
    cur_side_chars = 1
    
    prompt = f"""You are a world-renowned novelist and TRPG creator. You specialize in long, descriptive sentences and enigmatic plots. As you write, you need to follow Ronald Tobias's plot theory. You also need to create a outline for your novel based on the input we give you, and generate a title based on the outline. You must create the outline at least more tham 2000 words long. YOU MUST FOLLOW THESE RULES.

Output template is as follows: ```json{{"title": "title", "outline": "outline"}}```. DO NOT output anything other than JSON values. ONLY JSON is allowed.

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
"""

    prompt, cur_side_chars = _add_side_character(
        side_char_enable1, prompt, cur_side_chars,
        name2, job2, age2, mbti2, personality2
    )
    prompt, cur_side_chars = _add_side_character(
        side_char_enable2, prompt, cur_side_chars,
        name3, job3, age3, mbti3, personality3
    )
    prompt, cur_side_chars = _add_side_character(
        side_char_enable3, prompt, cur_side_chars,
        name4, job4, age4, mbti4, personality4
    )
    
    print(f"generated prompt:\n{prompt}")

    response_json = None
    while response_json is None:
        _, response_txt = await palmchat.gen_text(prompt, mode="text")
        print(response_txt)

        try:
            response_json = utils.parse_first_json_code_snippet(response_txt)
        except:
            pass

    return (
        response_json['title'],
        response_json['outline']
        # f"# {response_json['title']}",
        # response_json["plot"][0]["chapter_title"],
        # response_json["plot"][1]["chapter_title"],
        # response_json["plot"][2]["chapter_title"],
        # response_json["plot"][3]["chapter_title"],
        # f"## {response_json['plot'][0]['chapter_title']}",
        # f"## {response_json['plot'][1]['chapter_title']}",
        # f"## {response_json['plot'][2]['chapter_title']}",
        # f"## {response_json['plot'][3]['chapter_title']}",        
        # response_json["plot"][0]["chapter_plot"],
        # response_json["plot"][1]["chapter_plot"],
        # response_json["plot"][2]["chapter_plot"],
        # response_json["plot"][3]["chapter_plot"],
    )

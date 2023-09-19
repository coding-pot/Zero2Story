from interfaces import utils
from modules import palmchat

async def plot_gen(
    time, place, mood,
    name1, age1, mbti1, personality1, job1,
    name2, age2, mbti2, personality2, job2,
    name3, age3, mbti3, personality3, job3,
    name4, age4, mbti4, personality4, job4,
):
    prompt = f"""You are a world-renowned novelist and TRPG creator. You specialize in long, descriptive sentences and enigmatic plots. As you write, you need to follow Ronald Tobias's plot theory. You also need to create a basic outline for your novel based on the input we give you, and generate a title based on the outline.

Output template is as follows: ```json{{"title": "title", "plot": [{{"chapter_title" : "chapter_title", "chapter_plot" : "chapter_plot"}}]}}```. DO NOT output anything other than JSON values. ONLY JSON is allowed. The JSON key name should not be changed.

You must create only four chapters, no more, no less. 

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
"""

    response_json = None
    while response_json is None:
        _, response_txt = await palmchat.gen_text(prompt, mode="text")
        print(response_txt)

        try:
            response_json = utils.parse_first_json_code_snippet(response_txt)
        except:
            pass

    return (
        f"# {response_json['title']}",
        response_json["plot"][0]["chapter_title"],
        response_json["plot"][1]["chapter_title"],
        response_json["plot"][2]["chapter_title"],
        response_json["plot"][3]["chapter_title"],
        response_json["plot"][0]["chapter_plot"],
        response_json["plot"][1]["chapter_plot"],
        response_json["plot"][2]["chapter_plot"],
        response_json["plot"][3]["chapter_plot"],
    )
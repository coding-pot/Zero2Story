pre_phase_description = """
![](file/assets/overview.png)

Zero2Story is a framework built on top of [PaLM API](https://developers.generativeai.google), [Stable Diffusion](https://en.wikipedia.org/wiki/Stable_Diffusion), [MusicGen](https://audiocraft.metademolab.com/musicgen.html) for ordinary people to create their own stories. This framework consists of the **background setup**, **character setup**, and **interative story generation** phases.
"""

background_setup_phase_description = """
In this phase, users can setup the genre, place, and mood of the story. Especially, genre is the key that others are depending on. 
"""
character_setup_phase_description = """
In this phase, users can setup characters up to four. For each character, users can decide their characteristics and basic information such as name, age, MBTI, and personality. Also, the image of each character could be generated based on the information using Stable Diffusion. 

PaLM API translates the given character information into a list of keywords that Stable Diffusion could effectively understands. Then, Stable Diffusion generates images using the keywords as a prompt.
"""
story_generation_phase_description = """
In this phase, the first few paragraphs are generated solely based on the information from the background and character setup phases. Afterwards, users could choose a direction from the given three options that PaLM API generated. Then, further stories are generated based on users' choice. This cycle of choosing an option and generating further stories are interatively continued until users decides to stop. 

In each story generation, users also could generate background images and music that describe each scene using Stable Diffusion and MusicGen. If the generated story, options, image, and music in each turn, users could ask to re-generate them.
"""
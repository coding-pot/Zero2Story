# Zero2Story

- **The paper about this project has been accepted at [NeurIPS 2023 Workshop on Machine Learning for Creativity and Design](https://neuripscreativityworkshop.github.io/2023/). Please find more information at the [NeurIPS page](https://nips.cc/virtual/2023/75059)**.
- This project is currently running on [Hugging Face Space](https://huggingface.co/spaces/chansung/zero2story).

![](assets/overview.png)

Zero2Story is a framework built on top of [PaLM API](https://developers.generativeai.google), [Stable Diffusion](https://en.wikipedia.org/wiki/Stable_Diffusion), [MusicGen](https://audiocraft.metademolab.com/musicgen.html) for ordinary people to create their own stories. This framework consists of the **background setup**, **character setup**, and **interative story generation** phases.

**1. Background setup**: In this phase, users can setup the genre, place, and mood of the story. Especially, genre is the key that others are depending on. 

**2. Character setup**: In this phase, users can setup characters up to four. For each character, users can decide their characteristics and basic information such as name, age, MBTI, and personality. Also, the image of each character could be generated based on the information using Stable Diffusion. 
- PaLM API translates the given character information into a list of keywords that Stable Diffusion could effectively understands.
- Then, Stable Diffusion generates images using the keywords as a prompt.

**3. Interactive story generation:**: In this phase, the first few paragraphs are generated solely based on the information from the background and character setup phases. Afterwards, users could choose a direction from the given three options that PaLM API generated. Then, further stories are generated based on users' choice. This cycle of choosing an option and generating further stories are interatively continued until users decides to stop. 
- In each story generation, users also could generate background images and music that describe each scene using Stable Diffusion and MusicGen.
- If the generated story, options, image, and music in each turn, users could ask to re-generate them.

## Prerequisites

### PaLM API key

This project heavily depends on [PaLM API](https://developers.generativeai.google). If you want to run it on your own environment, you need to get [PaLM API key](https://developers.generativeai.google/tutorials/setup) and paste it in `.palm_api_key.txt` file within the root directory.

### Packages

Make sure you have installed all of the following prerequisites on your development machine:
* CUDA Toolkit 11.8 with cuDNN 8 - [Download & Install CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) It is highly recommended to run on a GPU. If you run it in a CPU environment, it will be very slow.
* Poetry - [Download & Install Poetry](https://python-poetry.org/docs/#installation) It is the python packaging and dependency manager.
* SQLite3 v3.35.0 or higher - It is required to be installed due to dependencies.
    - Ubuntu 22.04 and later
    ```shell
    $ sudo apt install libc6 sqlite3 libsqlite3
    ```
    - Ubuntu 20.04
    ```shell
    $ sudo sh -c 'cat <<EOF >> /etc/apt/sources.list
      deb http://archive.ubuntu.com/ubuntu/ jammy main
      deb http://security.ubuntu.com/ubuntu/ jammy-security main
      EOF'
    $ sudo apt update
    $ sudo apt install libc6 sqlite3 libsqlite3
    ```
* FFmpeg (Optional) - Installing FFmpeg enables local video mixing, which in turn generates results more quickly than [other methods](https://huggingface.co/spaces/fffiloni/animated-audio-visualizer)
    ```shell
    $ sudo apt install ffmpeg

## Installation

Before running the application for the first time, install the required dependencies:
```shell
$ poetry install
```

If dependencies change or need updates in the future, you can use:
```shell
$ poetry update
```

## Run

```shell
$ poetry run python app.py
```

## Todo

- [ ] Exporting of generated stories as PDF


## Stable Diffusion Model Information

### Checkpoints
- For character image generation: [CIVIT.AI Model 129896](https://civitai.com/models/129896)
- For background image generation: [CIVIT.AI Model 93931](https://civitai.com/models/93931?modelVersionId=148652)

### VAEs
- For character image generation: [CIVIT.AI Model 23906](https://civitai.com/models/23906)
- For background image generation: [CIVIT.AI Model 65728](https://civitai.com/models/65728)

## prompt-cli

**prompt-cli** is an interactive neural search and llama chat.

## Features
- [x] vector search (qdrant) of 3.5 million public stable diffusion prompts
- [x] free form chat with search results (RAG - mistral) with up to 32k context.
- [x] on demand image generation of selected prompts with stable diffusion
- [x] in terminal image display with kitty graphics protocol

![Screenshot](https://raw.githubusercontent.com/hexive/prompt-cli/main/screenshot.jpg)

## Install

Check the [wiki](https://github.com/hexive/prompt-cli/wiki) for full documentation about install, configuration, tips & tricks, etc

1. [Install](https://github.com/hexive/prompt-cli/wiki/Install)  
1. [Configure](https://github.com/hexive/prompt-cli/wiki/Config)
1. [Run it](https://github.com/hexive/prompt-cli/wiki/Run)
1. [Update](https://github.com/hexive/prompt-cli/wiki/Update)

## Backstory

Um, what? long story short -- the [prompt quil](https://github.com/osi1880vr/prompt_quill) creator compiled a gigantic list of 3.5 million image prompts from public sources (mostly civitai), encoded them, and threw them into a vector database (qdrant). He built a whole gradio site around it that does tons of cool stuff -- you should definitely check it out.

**prompt-cli** is a more minimal, lightweight and free flowing interaction with the database. You can vector search the 3.5 million promps, filter them by keyword, automatically generate stable-diffusion images from the results -- all from the comfort of your terminal. You can also fire up the llm and chat with it about your results. "what are the names of all the artists used?" or "count how many female vs male characters?" or "create a new image prompt based on the style and themes from this context" etc.










import os
import torch
from llama_cpp import Llama
from search import result_check
from transformers import AutoTokenizer
from util import *


#######################################################
######################  LLM  ##########################
#######################################################

# lazy load llama.cpp only on /ask
llama = None

def preflight(documents):
    #any problems loading llama.cpp?
    global llama
    if llama is None:
        try:
            with console.status("\nLlama.cpp is loading..."):
                llama = get_model()
        except Exception as e:
            console.print("\nError loading llama.cpp", style=f"{error_color}")
            console.print(f"--{e}\n--set 'verbose=True' in user_config.ini & rerun for details\n--you may continue with search & image generation.", style=f"{error_color}")
            # on for debug?
            #import traceback
            #console.print(f"--Traceback says: ", style=f"bold {error_color}")
            #traceback.print_exc()
            #console.print("\n\n")
            return False

    # are there documents to chat with?
    if not result_check(documents):
        return False

    return True

def prepare_response(documents, query):
    with console.status("\nLlama is now analyzing full context..."):
        try:
            return generate_response(documents, query)
        except Exception as e:
            console.print("\nSomething went wrong. Error returned is:", style=f"{error_color}")
            console.print(f"--{e}\n", style=f"{error_color}")
            return False
        

def estimate_tokens(text: str) -> int:
    return len(text) // 3.5  # 4 char per token ? 3.5

def trim(text: str):

    chars_to_keep = (config('llm','n_ctx', int) * 2.5)
    chars_to_keep = round(chars_to_keep)
    trimmed_text = text[:chars_to_keep]
    
    return trimmed_text

def get_model():
    global llama
    if llama is None:
        
        # get values from user_config.ini
        n_gpu_layers=config('llm','n_gpu_layers',int)
        main_gpu=config('llm','main_gpu',int)
        split_mode=config('llm','split_mode',int)
        n_ctx=config('llm','n_ctx',int)
        verbose=config('llm','verbose',bool)

        llm_model_path = install_path() + "/models/Mistral-7B-Instruct-v0.3-Q6_K.gguf"
        llama = Llama(model_path=llm_model_path, n_gpu_layers=n_gpu_layers, main_gpu=main_gpu, split_mode=split_mode, n_ctx=n_ctx, verbose=verbose)
    return llama

def generate_response(documents, query):
    documents = documents['result']

    context = "\n".join(documents)
    if config('ui','debug',bool):print(f"context tokens pre: {estimate_tokens(text=context)}")
    if config('ui','debug',bool):print(f"from config: {config('llm','n_ctx', int)}")
    if estimate_tokens(text=context) > config('llm','n_ctx', int):
        context = trim(context)
        if config('ui','debug',bool):print(f"context tokens post: {estimate_tokens(text=context)}")

    prompt = f"Context:\n{context}\n\nQuery: {query}\n\nAnswer:"
    if config('ui','debug',bool): print(f"final prompt: {estimate_tokens(text=prompt)}")
    
    response = llama(prompt, max_tokens=350)
    return response['choices'][0]['text'].strip()
    

def print_response(response):
    console.print("\nLlama Response:\n", style=f"bold {llm_color}")
    console.print(response, style=f"{llm_color}")
    console.print("\n")

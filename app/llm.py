import os
import torch
from llama_cpp import Llama
from search import result_check
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
            #sys.exit()

    # are there documents to chat with?
    if not result_check(documents):
        return False

    return True

def prepare_response(documents, query):
    with console.status("\nLlama is now analyzing full context..."):
        return generate_response(documents, query)

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
    prompt = f"Context:\n{context}\n\nQuery: {query}\n\nAnswer:"
    response = llama(prompt, max_tokens=350)
    return response['choices'][0]['text'].strip()

def print_response(response):
    console.print("\nLlama Response:\n", style=f"bold {llm_color}")
    console.print(response, style=f"{llm_color}")
    console.print("\n")

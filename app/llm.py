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
            console.print(f"--try again with 'verbose=true' and 'debug=true' in user_config.ini", style=f"{error_color}")
            print_error(e)
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
            console.print("\nOops something went wrong preparing Llama's response.", style=f"{error_color}")
            console.print(f"--if error continues 'debug=true' in user_config.ini for details", style=f"{error_color}")
            print_error(e)
            return False

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

def get_tokenizer():
    local_directory = install_path() + "/models/tokenizer/"
    return AutoTokenizer.from_pretrained(local_directory)

def estimate_tokens(text: str) -> int:
    tokenizer = get_tokenizer()
    return len(tokenizer.encode(text))

def trim_tokens(text: str, remove_num_tokens: int):
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(text, add_special_tokens=False)
    
    if remove_num_tokens > 0:
        tokens = tokens[:-remove_num_tokens]
        # decode back to text
        trimmed_text = tokenizer.decode(tokens)
    else:
        trimmed_text = text

    return trimmed_text

def generate_response(documents, query):
    documents = documents['result']
    context = "\n".join(documents)

    prompt = f"Context:\n{context}\n\nQuery: {query}\n\nAnswer:"

    # Make sure we don't send more context than the user set max_context 
    max_context_size = round(config('llm', 'n_ctx', int) * 0.98) #2% buffer
    total_tokens = estimate_tokens(prompt)
    remove_num_tokens = total_tokens - max_context_size

    if remove_num_tokens > 0:
        context = trim_tokens(context, remove_num_tokens)
        prompt = f"Context:\n{context}\n\nQuery: {query}\n\nAnswer:"
    
    response = llama(prompt, max_tokens=350)
    return response['choices'][0]['text'].strip()
    
def print_response(response):
    console.print("\nLlama Response:\n", style=f"bold {llm_color}")
    console.print(response, style=f"{llm_color}")
    console.print("\n")

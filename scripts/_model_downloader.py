import os
import requests
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm


def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

# install path
install_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# grab the encode model
encode_model_path = install_path + "/models/BAII/model.safetensors"
if os.path.exists(encode_model_path):
	print("encoding model already exists. skipping.")
else:
	print("--downloading encoding model (~440 MB)")
	model_name="BAAI/bge-base-en-v1.5"
	#save_directory="BAII"
	save_directory=install_path + "/models/BAII/"

	# Download and save the tokenizer
	tokenizer = AutoTokenizer.from_pretrained(model_name)
	tokenizer.save_pretrained(save_directory)

	# Download and save the model
	model = AutoModel.from_pretrained(model_name)
	model.save_pretrained(save_directory)

	print("encoding model has downloaded")

# grab the llm model
llm_model_path = install_path + "/models/Mistral-7B-Instruct-v0.3-Q6_K.gguf"
if os.path.exists(llm_model_path):
	print("llm model already exists. skipping.")
else:
	print("--downloading llm model (~6 GB)")
	url = "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q6_K.gguf"
	try:
		download_file(url, llm_model_path)
		print("llm model has downloaded")
	except:
		print("something has gone wrong with the llm downloaded")
	



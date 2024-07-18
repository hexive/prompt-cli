#!/usr/bin/env bash
# "Starting prompt-cli installer"


cd "$(dirname "${BASH_SOURCE[0]}")"

# "--creating venv environment"
python3 -m venv .venv

# "--using venv environment" 
source .venv/bin/activate 

# "--building llama cpp with cuda for GPU support" 
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# "--installng some python dependencies" 
pip install qdrant-client transformers torch rich prompt_toolkit

# "--downloading models if they don't exist"
python models/_model_downloader.py

echo "*********************************"
echo "done. use start_linux.sh to begin"
echo "*********************************"
#!/usr/bin/env bash
echo "Starting prompt-cli installer/updater"


cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ -f .venv/bin/activate ]]
    then
	echo "--found venv environment - activating"
        source .venv/bin/activate
    else
        echo "--creating venv environment"
	python3 -m venv .venv
	source .venv/bin/activate
    fi

CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

pip install qdrant-client transformers torch rich prompt_toolkit sentencepiece

python scripts/_model_downloader.py

echo "*********************************"
echo "done. use start_linux.sh to begin"
echo "*********************************"

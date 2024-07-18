#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

#if venv deactivate?

source .venv/bin/activate
python app/app.py
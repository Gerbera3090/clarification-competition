#!/bin/sh
set -eu

# Runs only while this terminal command is active. Press Ctrl+C to stop it.
export OLLAMA_NO_CLOUD=1
export OLLAMA_KEEP_ALIVE=0
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH=4096

exec ollama serve

#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
. ./.env
export SSL_CERT_FILE="$(uv run --frozen python -c 'import certifi; print(certifi.where())')"

if ! curl --fail --silent --max-time 2 "$OLLAMA_API_BASE/api/version" >/dev/null; then
  echo 'Ollama is not running. Start ./.local/start-ollama.sh in another terminal.' >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo 'Docker is not ready. Start Docker Desktop and wait for docker info to succeed.' >&2
  exit 1
fi

head -n 1 data/mbpp_demo_test.jsonl > .local/smoke-input.jsonl

uv run --frozen python generate_responses.py clarify/algorithms/my_clarification.py \
  --dataset_path .local/smoke-input.jsonl \
  --output_path .local/quickstart-output.jsonl \
  --language_model "$ECC_LOCAL_MODEL" \
  --clarification_model "$ECC_LOCAL_MODEL" \
  --max_workers 1

uv run --frozen python evaluate_responses.py \
  --benchmark_path .local/smoke-input.jsonl \
  --generation_path .local/quickstart-output.jsonl \
  --output_path .local/quickstart-results.jsonl \
  --force_rerun

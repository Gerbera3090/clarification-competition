#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
. ./.env

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo 'OPENAI_API_KEY is empty. Add a project API key to the ignored .env file.' >&2
  exit 1
fi

case "$ECC_OPENAI_MODEL" in
  openai/*) ;;
  *) echo 'ECC_OPENAI_MODEL must be an OpenAI API model.' >&2; exit 1 ;;
esac

if ! docker info >/dev/null 2>&1; then
  echo 'Docker is not ready. Start Docker Desktop and wait for docker info to succeed.' >&2
  exit 1
fi

export SSL_CERT_FILE="$(uv run --frozen python -c 'import certifi; print(certifi.where())')"
head -n 1 data/mbpp_demo_test.jsonl > .local/openai-smoke-input.jsonl

uv run --frozen python generate_responses.py clarify/algorithms/my_clarification.py \
  --dataset_path .local/openai-smoke-input.jsonl \
  --output_path .local/openai-smoke-output.jsonl \
  --language_model "$ECC_OPENAI_MODEL" \
  --clarification_model "$ECC_OPENAI_MODEL" \
  --fail_on_exception=True \
  --max_workers 1

uv run --frozen python evaluate_responses.py \
  --benchmark_path .local/openai-smoke-input.jsonl \
  --generation_path .local/openai-smoke-output.jsonl \
  --output_path .local/openai-smoke-results.jsonl \
  --force_rerun

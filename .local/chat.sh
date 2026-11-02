#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
. ./.env

case "$ECC_LOCAL_MODEL" in
  ollama/*) ;;
  *) echo "Expected a local Ollama model, got: $ECC_LOCAL_MODEL" >&2; exit 1 ;;
esac

if ! curl --fail --silent --max-time 2 "$OLLAMA_API_BASE/api/version" >/dev/null; then
  echo 'Ollama is not running. Start ./.local/start-ollama.sh in another terminal.' >&2
  exit 1
fi

printf 'Using local model: %s\n' "$ECC_LOCAL_MODEL"
exec uv run --frozen python chat.py clarify/algorithms/my_clarification.py \
  --model_name "$ECC_LOCAL_MODEL"

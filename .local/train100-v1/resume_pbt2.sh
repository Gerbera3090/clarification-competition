#!/bin/sh
# Continue only uncompleted inputs after the stalled batch was interrupted.
set -eu
cd "$(dirname "$0")/../.."
root=.local/train100-v1
. ./.env
: "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
: "${ECC_OPENAI_MODEL:?ECC_OPENAI_MODEL is required}"
export SSL_CERT_FILE="$(/opt/homebrew/bin/uv run --frozen python -c 'import certifi; print(certifi.where())')"
# LiteLLM normally permits a longer wait; keep an idle network call bounded.
export REQUEST_TIMEOUT=90
for batch in mbpp-04-recovery humaneval-05 mbpp-05; do
  case "$batch" in
    mbpp-04-recovery) input="$root/recovery/mbpp-04-pending.jsonl" ;;
    *) input="$root/batches/$batch.jsonl" ;;
  esac
  output="$root/pbt2/$batch-output.jsonl"
  log="$root/pbt2/$batch-generate.log"
  if [ -e "$output" ] || [ -e "$log" ]; then echo "Existing output: $batch" >&2; exit 1; fi
  printf 'START %s (recovery)\n' "$batch" >> "$root/pbt2/status.log"
  /usr/bin/time -p /opt/homebrew/bin/uv run --frozen python generate_responses.py \
    "$root/algorithms/pbt_clarifier2.py" --dataset_path "$input" --output_path "$output" \
    --language_model "$ECC_OPENAI_MODEL" --clarification_model "$ECC_OPENAI_MODEL" \
    --fail_on_exception=True --max_workers 1 > "$log" 2>&1
  python3 - "$input" "$output" <<'PY'
import json, sys
read = lambda path: [json.loads(line) for line in open(path) if line.strip()]
expected, actual = read(sys.argv[1]), read(sys.argv[2])
keys = lambda rows: {(r['task_id'], r['prompt']) for r in rows}
assert len(expected) == len(actual) and keys(expected) == keys(actual)
PY
  printf 'DONE %s (recovery)\n' "$batch" >> "$root/pbt2/status.log"
done

#!/bin/sh
# Run one frozen 100-example algorithm; stop on errors and never overwrite a batch.
set -eu
case "${1:-}" in
  pbt2) algorithm=pbt_clarifier2 ;;
  pbt3) algorithm=pbt_clarifier3 ;;
  *) echo 'Usage: sh run_generation.sh pbt2|pbt3' >&2; exit 2 ;;
esac
cd "$(dirname "$0")/../.."
root=.local/train100-v1
out="$root/$1"
. ./.env
: "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
: "${ECC_OPENAI_MODEL:?ECC_OPENAI_MODEL is required}"
export SSL_CERT_FILE="$(/opt/homebrew/bin/uv run --frozen python -c 'import certifi; print(certifi.where())')"
python3 - "$root" "$algorithm" <<'PY'
import hashlib, json, pathlib, sys
root, algorithm = pathlib.Path(sys.argv[1]), sys.argv[2]
manifest = json.loads((root / 'manifest.json').read_text())
snapshots = json.loads((root / 'algorithm-snapshots.json').read_text())
actual = hashlib.sha256((root / 'algorithms' / (algorithm + '.py')).read_bytes()).hexdigest()
assert actual == snapshots[algorithm], 'Algorithm snapshot differs from frozen version'
for batch in manifest['batches']:
    actual = hashlib.sha256((root / batch['path']).read_bytes()).hexdigest()
    assert actual == batch['sha256'], f"Changed input: {batch['path']}"
PY
for num in 01 02 03 04 05; do
  for family in humaneval mbpp; do
    batch="$family-$num"
    input="$root/batches/$batch.jsonl"
    output="$out/$batch-output.jsonl"
    log="$out/$batch-generate.log"
    if [ -e "$output" ] || [ -e "$log" ]; then
      echo "Refusing to overwrite existing batch: $batch" >&2
      exit 1
    fi
    printf 'START %s\n' "$batch" >> "$out/status.log"
    /usr/bin/time -p /opt/homebrew/bin/uv run --frozen python generate_responses.py \
      "$root/algorithms/$algorithm.py" --dataset_path "$input" --output_path "$output" \
      --language_model "$ECC_OPENAI_MODEL" --clarification_model "$ECC_OPENAI_MODEL" \
      --fail_on_exception=True --max_workers 1 > "$log" 2>&1
    python3 - "$input" "$output" <<'PY'
import json, sys
read = lambda p: [json.loads(line) for line in open(p) if line.strip()]
expected, actual = read(sys.argv[1]), read(sys.argv[2])
keys = lambda rows: {(r['task_id'], r['prompt']) for r in rows}
assert len(actual) == 10 and keys(expected) == keys(actual), 'Incomplete or mismatched batch'
PY
    printf 'DONE %s\n' "$batch" >> "$out/status.log"
  done
done

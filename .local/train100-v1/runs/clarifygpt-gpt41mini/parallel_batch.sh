#!/bin/sh
# Process one unclaimed frozen batch in parallel; the main runner reuses it.
set -eu
case "${1:-}" in
  mbpp-01|mbpp-02|mbpp-03|mbpp-04|mbpp-05|humaneval-02|humaneval-03|humaneval-04|humaneval-05) batch="$1" ;;
  *) echo 'Invalid batch' >&2; exit 2 ;;
esac
cd "$(dirname "$0")/../../../.."
root=.local/train100-v1
out="$root/runs/clarifygpt-gpt41mini"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
. ./.env
: "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
: "${ECC_OPENAI_MODEL:?ECC_OPENAI_MODEL is required}"
export SSL_CERT_FILE="$(/opt/homebrew/bin/uv run --frozen python -c 'import certifi; print(certifi.where())')"
export REQUEST_TIMEOUT=90
python3 - "$root" "$out" "$batch" "$ECC_OPENAI_MODEL" <<'PY'
import hashlib, json, pathlib, sys
root, out, batch, model = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((out/'experiment.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
assert state['model']==model and state['manifest_sha256']==sha(root/'manifest.json')
assert state['algorithm_sha256']==sha(out/'algorithm.py')
assert all(sha(pathlib.Path(name))==digest for name,digest in state['sdk_sha256'].items()), 'SDK changed'
entry=next(x for x in manifest['batches'] if pathlib.Path(x['path']).stem==batch)
assert sha(root/entry['path'])==entry['sha256']
assert not (out/f'{batch}-output.jsonl').exists() and not (out/f'{batch}-generate.log').exists(), 'Batch already claimed'
PY
/usr/bin/time -p /opt/homebrew/bin/uv run --frozen python generate_responses.py \
  "$out/algorithm.py" --dataset_path "$root/batches/$batch.jsonl" --output_path "$out/$batch-output.jsonl" \
  --language_model "$ECC_OPENAI_MODEL" --clarification_model "$ECC_OPENAI_MODEL" \
  --fail_on_exception=True --max_workers 1 > "$out/$batch-generate.log" 2>&1
python3 - "$root/batches/$batch.jsonl" "$out/$batch-output.jsonl" <<'PY'
import json,sys
read=lambda p:[json.loads(x) for x in open(p) if x.strip()]
a,b=read(sys.argv[1]),read(sys.argv[2]);keys=lambda r:{(x['task_id'],x['prompt']) for x in r}
assert len(a)==len(b)==10 and keys(a)==keys(b), 'Batch incomplete'
print('Completed parallel batch:',sys.argv[2])
PY

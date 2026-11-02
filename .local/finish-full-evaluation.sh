#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
export SSL_CERT_FILE="$(uv run --frozen python -c 'import certifi; print(certifi.where())')"
run_status_file=.local/full-run-20261029-status.txt

wait_for_generation() {
  run_pid=$1
  run_name=$2
  expected=$3
  printf '%s\n' "Waiting for $run_name generation." > "$run_status_file"
  while ps -p "$run_pid" -o command= 2>/dev/null | rg -Fq "full-$run_name-20261029-output.jsonl"; do
    sleep 10
  done
  python3 - "$run_name" "$expected" <<'PY'
import json, sys
from pathlib import Path
name, expected = sys.argv[1], int(sys.argv[2])
path = Path(f'.local/full-{name}-20261029-output.jsonl')
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
if len(rows) != expected or any('clarification_history' not in row for row in rows):
    raise SystemExit(f'{name}: expected {expected} complete results; got {len(rows)}')
print(f'{name}: {len(rows)} complete generated responses')
PY
}

ensure_docker() {
  if docker info >/dev/null 2>&1; then return; fi
  open -a Docker
  i=0
  while [ "$i" -lt 60 ]; do
    if docker info >/dev/null 2>&1; then return; fi
    i=$((i + 1))
    sleep 2
  done
  echo 'Docker did not become ready.' >&2
  return 1
}

evaluate_split() {
  run_name=$1
  result_path=".local/full-$run_name-20261029-results.jsonl"
  if [ -e "$result_path" ]; then
    echo "Refusing to overwrite $result_path" >&2
    return 1
  fi
  printf '%s\n' "Evaluating $run_name." > "$run_status_file"
  /usr/bin/time -p uv run --frozen python evaluate_responses.py \
    --split "$run_name" \
    --generation_path ".local/full-$run_name-20261029-output.jsonl" \
    --output_path "$result_path" \
    --max_workers 1 > ".local/full-$run_name-20261029-evaluate.log" 2>&1
}

trap 'printf "%s\n" "Stopped or failed. See .local/full-run-20261029-supervisor.log." > "$run_status_file"' EXIT
wait_for_generation 38259 val 770
ensure_docker
evaluate_split val
wait_for_generation 40036 train 7961
ensure_docker
evaluate_split train
printf '%s\n' 'Complete: validation and train results are available.' > "$run_status_file"
trap - EXIT

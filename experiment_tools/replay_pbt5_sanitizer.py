#!/usr/bin/env python3
"""Apply the original PBT5 sanitizer to the same saved PBT5_1 responses.

The sanitizer may call the configured LLM for format repair. With --execute,
record those calls and write a separate generation file for local grading.
No competition SDK files or original experiment results are modified.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from clarify.env import ClarificationConfiguration, ClarificationEnvironment
from clarify.runtime import _validate_and_parse_evalplus_result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def evalplus_code(response: str) -> str | None:
    # Match EvaluationFunction: it wraps non-fenced responses before parsing.
    value = response if '```python' in response else f'```python\n{response.strip()}\n```'
    try:
        return _validate_and_parse_evalplus_result(value)
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, help='Completed PBT5_1 experiment directory')
    parser.add_argument('--sanitizer-run', required=True, help='Original PBT5 experiment directory')
    parser.add_argument('--output-dir', required=True, help='Separate new replay directory')
    parser.add_argument('--execute', action='store_true', help='Allow sanitizer repair model calls')
    args = parser.parse_args()
    run, baseline, output = map(lambda v: Path(v).resolve(), (args.run, args.sanitizer_run, args.output_dir))
    state = json.loads((run / 'experiment.json').read_text())
    old_state = json.loads((baseline / 'experiment.json').read_text())
    if any(state.get(key) != old_state.get(key) for key in ('model','decision_model','manifest_sha256','sdk_sha256')):
        raise ValueError('Source runs use different models, sample, or SDK files')
    sanitizer_path = baseline / 'algorithm.py'
    if digest(sanitizer_path) != old_state['algorithm_sha256']:
        raise ValueError('PBT5 sanitizer snapshot hash differs from experiment metadata')
    for name, expected_hash in state['sdk_sha256'].items():
        if digest(ROOT / name) != expected_hash:
            raise ValueError(f'SDK file changed after generation: {name}')
    benchmark = ROOT / '.local/train100-v1'
    manifest = json.loads((benchmark / 'manifest.json').read_text())
    if digest(benchmark / 'manifest.json') != state['manifest_sha256']:
        raise ValueError('Benchmark manifest changed')
    by_key = {}
    for batch in manifest['batches']:
        batch_path = benchmark / batch['path']
        if digest(batch_path) != batch['sha256']:
            raise ValueError('Benchmark input changed')
        for row in read_rows(batch_path):
            by_key[(row['task_id'], row['prompt'])] = row
    raw_path = run / 'all-output.jsonl'
    rows = read_rows(raw_path)
    if len(rows) != 100 or {(r['task_id'],r['prompt']) for r in rows} != set(by_key):
        raise ValueError('Expected the complete frozen 100-task generation')
    print(f'Plan: apply original PBT5 sanitizer to {len(rows)} saved PBT5_1 responses; model={state["model"]}')
    print('The sanitizer may make up to two billable LLM calls for each response that fails its static checks.')
    if not args.execute:
        print('Preview only; no model calls or files written.')
        return 0
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory is not empty; choose a new one')
    output.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('pbt5_original_snapshot', sanitizer_path)
    if spec is None or spec.loader is None:
        raise ValueError('Could not load PBT5 sanitizer snapshot')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = []
    sanitized_rows = []
    for row in rows:
        key = (row['task_id'], row['prompt'])
        entry = str(by_key[key]['entry_point'])
        clarifications = row.get('clarification_history') or []
        info = '\n'.join(f"Clarification question: {h[0]}\nUser's answer: {h[3]}" for h in clarifications) if clarifications else 'No clarification was requested.'
        coding_prompt = f'''Implement the Python function `{entry}` in a self-contained script.
Follow the task and any clarification; do not assume the candidate properties
were verified. Return only the implementation in a ```python fenced block.
TASK:\n{row['prompt']}\n{info}'''
        hooks = []
        env = ClarificationEnvironment(ClarificationConfiguration(language_model=state['model'], temperature=0.7),
                                       {'prompt':row['prompt'], 'entry_point':entry}, llm_api_hook=hooks.append)
        raw = row['prompt_result']
        output_text = io.StringIO()
        with contextlib.redirect_stdout(output_text):
            sanitized = module._sanitize_code_response(env, raw, entry, coding_prompt, 2)
        marker = output_text.getvalue().strip()
        new_row = dict(row, prompt_result=sanitized)
        sanitized_rows.append(new_row)
        records.append({'task_id': row['task_id'], 'raw_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                        'sanitized_sha256': hashlib.sha256(sanitized.encode()).hexdigest(),
                        'same_evaluator_code': evalplus_code(raw) == evalplus_code(sanitized),
                        'marker': marker, 'repair_calls_attempted': sum(m.get('role')=='user' for m in hooks),
                        'repair_recorded_cost': env.prompt_cost})
        print(f'[{len(records)}/{len(rows)}] {row["task_id"]}: {marker}', flush=True)
    (output / 'generation.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sanitized_rows),encoding='utf-8')
    (output / 'replay.json').write_text(json.dumps({'raw_path':str(raw_path),'raw_sha256':digest(raw_path),
        'sanitizer_path':str(sanitizer_path),'sanitizer_sha256':digest(sanitizer_path),
        'model':state['model'],'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote replay outputs: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

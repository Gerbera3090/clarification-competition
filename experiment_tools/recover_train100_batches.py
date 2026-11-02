#!/usr/bin/env python3
"""Resume interrupted frozen train100 generation without repeating completed tasks.

Preserves the prior logs and partial results as numbered recovery segments,
then writes a complete batch in frozen input order. Calls the normal competition
generator. Requires the matching run metadata and unchanged snapshot/SDK.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / '.local/train100-v1'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def key(row: dict) -> tuple[str, str]:
    return row['task_id'], row['prompt']


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--batch', action='append', required=True, help='Frozen batch stem; repeat as needed')
    parser.add_argument('--execute', action='store_true', help='Allow model calls for missing problems')
    args=parser.parse_args()
    run=Path(args.run).resolve()
    state=json.loads((run/'experiment.json').read_text())
    snapshot=run/'algorithm.py'
    manifest_path=BENCHMARK/'manifest.json'
    if sha(snapshot)!=state['algorithm_sha256'] or sha(manifest_path)!=state['manifest_sha256']:
        raise ValueError('Snapshot or benchmark metadata changed')
    for name,digest in state['sdk_sha256'].items():
        if sha(ROOT/name)!=digest:
            raise ValueError(f'SDK file changed: {name}')
    manifest=json.loads(manifest_path.read_text())
    batches={Path(b['path']).stem:b for b in manifest['batches']}
    if len(set(args.batch)) != len(args.batch) or any(name not in batches for name in args.batch):
        raise ValueError('Batch names must be distinct frozen batch stems')
    print(f'Recover {len(args.batch)} batch(es) in {run}; completed task outputs will be reused.',flush=True)
    if not args.execute:
        print('Preview only. Add --execute to allow model calls.')
        return 0

    def recover(name: str) -> None:
        entry=batches[name]; source=BENCHMARK/entry['path']
        if sha(source)!=entry['sha256']:
            raise ValueError(f'Frozen batch changed: {name}')
        expected=read(source); expected_keys={key(r) for r in expected}
        target=run/f'{name}-output.jsonl'; orig_log=run/f'{name}-generate.log'
        if target.exists():
            rows=read(target);keys=[key(r) for r in rows]
            if len(rows)==len(expected) and set(keys)==expected_keys:
                print(f'{name}: already complete',flush=True);return
            if len(keys)!=len(set(keys)) or not set(keys)<=expected_keys:
                raise ValueError(f'Partial result contains unexpected or duplicate task: {target}')
            if not orig_log.exists():
                raise ValueError(f'Missing log for interrupted result: {orig_log}')
            i=1
            while (run/f'{name}-recovery-{i:02d}-output.jsonl').exists() or (run/f'{name}-recovery-{i:02d}-generate.log').exists():i+=1
            # Move the pair in a recoverable order. Neither destination exists.
            os.rename(orig_log,run/f'{name}-recovery-{i:02d}-generate.log')
            os.rename(target,run/f'{name}-recovery-{i:02d}-output.jsonl')
        found={}
        for segment in sorted(run.glob(f'{name}-recovery-*-output.jsonl')):
            for row in read(segment):
                k=key(row)
                if k not in expected_keys or k in found:
                    raise ValueError(f'Duplicate/unexpected saved recovery row in {segment}')
                found[k]=row
        remaining=[row for row in expected if key(row) not in found]
        if remaining:
            i=1
            while (run/f'{name}-recovery-{i:02d}-output.jsonl').exists() or (run/f'{name}-recovery-{i:02d}-generate.log').exists():i+=1
            inp=run/f'{name}-recovery-{i:02d}-benchmark.jsonl'; out=run/f'{name}-recovery-{i:02d}-output.jsonl';log=run/f'{name}-recovery-{i:02d}-generate.log'
            text=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in remaining)
            if inp.exists() and inp.read_text(encoding='utf-8')!=text:
                raise ValueError(f'Existing recovery input differs: {inp}')
            if not inp.exists():inp.write_text(text,encoding='utf-8')
            cmd=[sys.executable,str(ROOT/'generate_responses.py'),str(snapshot),'--dataset_path',str(inp),
                 '--output_path',str(out),'--language_model',state['model'],'--clarification_model',state['model'],
                 '--fail_on_exception=True','--max_workers','1']
            if state.get('decision_model'):cmd += ['--decision_model',state['decision_model']]
            print(f'{name}: resuming {len(remaining)}/{len(expected)} missing problems',flush=True)
            with log.open('x',encoding='utf-8') as f:
                completed=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=False)
            if completed.returncode:
                raise RuntimeError(f'{name}: generation failed; outputs preserved in {out} and {log}')
            generated=read(out)
            if len(generated)!=len(remaining) or {key(r) for r in generated}!={key(r) for r in remaining}:
                raise RuntimeError(f'{name}: incomplete result; outputs preserved in {out}')
            found.update({key(row):row for row in generated})
        if set(found)!=expected_keys:
            raise ValueError(f'{name}: recovered task set does not match frozen input')
        with target.open('x',encoding='utf-8') as f:
            f.write(''.join(json.dumps(found[key(r)],ensure_ascii=False)+'\n' for r in expected))
        print(f'{name}: completed with all {len(expected)} unique tasks',flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(2,len(args.batch))) as pool:
        futures=[pool.submit(recover,name) for name in args.batch]
        for f in futures:f.result()
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,KeyError) as e:
        print(f'Error: {e}',file=sys.stderr);raise SystemExit(2)

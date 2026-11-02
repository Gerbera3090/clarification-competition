#!/usr/bin/env python3
"""Compare frozen 100-task runs after regrading known entry-point mismatches.

Input files remain immutable. A separate report substitutes only the outcomes
re-evaluated with the current runtime. No model calls occur here.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'experiment_tools'))
from compare_train100 import _metric, _result_path


def read(path: Path) -> list[dict]:
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(row: dict) -> tuple[str, str]:
    return row['task_id'], row['prompt']


def main() -> None:
    benchmark = ROOT / '.local/train100-v1'
    review = benchmark / 'current-runtime-review'
    regraded = read(review / 'results.jsonl')
    original_subset = read(review / 'input.jsonl')
    matches = {(r['_comparison_source'], *key(r)): r for r in regraded}
    originals = {(r['_comparison_source'], *key(r)): r for r in original_subset}
    if len(matches) != len(regraded) or set(matches) != set(originals):
        raise ValueError('Regraded historical examples do not match the preserved source examples')
    reg = json.loads((benchmark / 'comparison-registry.json').read_text())
    entries = []
    for entry in reg['entries']:
        src = _result_path(benchmark, entry['results_path'])
        if digest(src) != entry['results_sha256']:
            raise ValueError(f'Original registered result changed: {src}')
        rows = read(src)
        corrected=[]
        original_rows=[]
        changes=[]
        for row in rows:
            rkey=(entry['label'], *key(row))
            if rkey in matches:
                original = originals[rkey]
                replacement = dict(matches[rkey]); replacement.pop('_comparison_source', None)
                if row['success'] not in (original['success'], replacement['success']):
                    raise ValueError('Historical source differs from the regrading input')
                original_row = dict(original); original_row.pop('_comparison_source', None)
                original_rows.append(original_row)
                # Registry may already point at the independently regraded result.
                corrected.append(row if row['success'] == replacement['success'] else replacement)
                if replacement['success'] != original['success']:
                    changes.append({'task_id':row['task_id'],'before':original['success'],'after':replacement['success']})
            else:
                corrected.append(row)
                original_rows.append(row)
        before, after = _metric(original_rows), _metric(corrected)
        entries.append({'label':entry['label'], 'algorithm':entry['algorithm'], 'model':entry['model'],
                        'decision_model':entry.get('provenance',{}).get('decision_model'),
                        'original_results':str(src), 'original_results_sha256':digest(src),
                        'before':before,'after':after,'changed':changes})
    lines=['# train100-v1 동일 채점 기준 비교', '',
           '- 현재 runtime에서는 문제에 제공한 함수명을 사용하도록 바뀌었다.',
           '- 고정 100문제 중 기존 EvalPlus 함수명과 표기가 다른 3개에 대해 각 과거 응답을 현재 runtime으로 다시 채점했다.',
           '- 다른 97개는 호출 함수명이 동일하고 현재 변경의 영향을 받지 않아 기존 결과를 보존했다.',
           '- 재채점에는 모델 호출이 없다. 기존 비교 레지스트리가 이미 재채점 결과를 가리키면 이를 재사용했다.',
           '- 반환 타입·문제 조건에 대한 모델 차이나 동일 채점에서의 확률적 변동은 여전히 남는다.', '',
           '| 알고리즘 / 실행 | 이전 통과 | 현재 기준 통과 | TDS | 질문 | 기록 모델 비용 | 변경된 문제 |',
           '|---|---:|---:|---:|---:|---:|---|']
    for entry in entries:
        before, after = entry['before'], entry['after']
        cost=after['recorded_model_cost']
        cost_text=f'${cost:.4f}' if cost is not None else '미기록'
        changed=', '.join(f"{c['task_id']} ({'통과' if c['after'] else '실패'})" for c in entry['changed']) or '없음'
        lines.append(f"| {entry['algorithm']} / {entry['label']} | {before['pass']}/100 | {after['pass']}/100 | {after['tds']:.4f} | {after['questions']}/100 | {cost_text} | {changed} |")
    payload={'runtime_sha256':digest(ROOT/'clarify/runtime.py'),'historical_subset_sha256':digest(review/'input.jsonl'),
             'regraded_subset_sha256':digest(review/'results.jsonl'),'entries':entries}
    (review/'COMPARISON-current-runtime.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (review/'COMPARISON-current-runtime.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Wrote {review / "COMPARISON-current-runtime.md"}')


if __name__ == '__main__':
    main()

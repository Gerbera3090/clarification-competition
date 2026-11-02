#!/usr/bin/env python3
"""Summarize logged PBT5 decisions and compare paired PBT4 outcomes, no API calls."""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'experiment_tools'))
from analyze_run import _extract_json, extract_traces

STATUSES = ('established', 'ambiguous', 'contradicted', 'not_applicable')


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main() -> None:
    run = Path(sys.argv[1]).resolve()
    comparison = Path(sys.argv[2]).resolve()
    rows = read_rows(run / 'results.jsonl')
    old_rows = read_rows(comparison / 'results.jsonl')
    old_by_key = {(r['task_id'], r['prompt']): r for r in old_rows}
    traces, trace_diag = extract_traces(comparison, old_rows)
    old_status = {}
    for r in old_rows:
        key = (r['task_id'], r['prompt'])
        t = traces.get(key)
        if not t:
            continue
        result = {}
        previous = None
        for event in t['events']:
            stage = event['stage']
            if stage == 'format_repair':
                stage = previous
            elif stage != 'other':
                previous = stage
            if stage != 'property_classification':
                continue
            try:
                obj = _extract_json(event['response'])
            except (ValueError, TypeError):
                continue
            for row in obj.get('properties', []):
                if isinstance(row, dict) and type(row.get('id')) is int and row.get('status') in STATUSES:
                    result[row['id']] = row['status']
        old_status[key] = result

    decisions = {}
    markers = collections.Counter()
    for log in sorted(run.glob('*-generate.log')):
        for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
            if 'PBT5_DECISIONS_JSON ' in line:
                try:
                    record = json.loads(line.split('PBT5_DECISIONS_JSON ', 1)[1])
                except ValueError:
                    markers['record_parse_failed'] += 1
                    continue
                digest = record.get('prompt_sha256')
                if digest in decisions:
                    raise ValueError(f'Duplicate decision record: {digest}')
                decisions[digest] = record.get('answers', {})
            for marker in ('PBT5_DECISION_RETRY', 'PROPERTY_PAIR_DISCARDED',
                           'PROPERTY_PAIR_VALIDATION_FAILED', 'DIRECT_CONFLICT_VALIDATION_FAILED',
                           'CONFLICT_SELECTION_FAILED', 'PROPERTY_QUESTION_VALIDATION_FAILED',
                           'SANITIZE_LLM', 'SANITIZE_FAILED'):
                if marker in line:
                    markers[marker] += 1
    statuses = collections.Counter()
    matrix = collections.Counter()
    cases = []
    paired = collections.Counter()
    for row in rows:
        key = (row['task_id'], row['prompt'])
        old = old_by_key[key]
        paired[(old['success'], row['success'])] += 1
        digest = hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest()
        answers = decisions.get(digest, {})
        scan = {}
        for k, answer in answers.items():
            if k.startswith('property_') and k[9:].isdigit() and isinstance(answer, dict):
                choice = answer.get('choice')
                if choice in STATUSES:
                    scan[int(k[9:])] = choice
        statuses.update(scan.values())
        old_scan = old_status.get(key, {})
        for i in set(scan) & set(old_scan):
            matrix[(old_scan[i], scan[i])] += 1
        h = row.get('clarification_history') or []
        old_h = old.get('clarification_history') or []
        cases.append({'task_id': row['task_id'], 'pbt5_pass': row['success'], 'pbt4_pass': old['success'],
                      'decision_count': len(scan), 'decision_statuses': dict(collections.Counter(scan.values())),
                      'pbt4_status_count': len(old_scan), 'pbt4_statuses': dict(collections.Counter(old_scan.values())),
                      'question': h[0][0] if h else None, 'answer': h[0][3] if h else None,
                      'pbt4_question': old_h[0][0] if old_h else None})
    payload = {'task_count': len(rows), 'recorded_decision_count': len(decisions), 'pbt4_trace_diagnostics': trace_diag,
               'pbt5_classifications': dict(statuses), 'status_matrix': {a:{b:matrix[(a,b)] for b in STATUSES} for a in STATUSES},
               'paired_outcomes': {'both_pass': paired[(True,True)], 'pbt4_only': paired[(True,False)],
                                   'pbt5_only': paired[(False,True)], 'both_fail': paired[(False,False)]},
               'diagnostic_markers': dict(markers), 'cases': cases}
    (run / 'PBT5_ANALYSIS.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# PBT5 decision model 실험 분석', '', f"- PBT5 결정 기록: {len(decisions)}/{len(rows)} 문제",
             f"- PBT4 로그 연결: {trace_diag['matched']}/{len(old_rows)} 문제",
             f'- PBT5 속성 판정: {dict(statuses)}', f"- PBT4/PBT5 짝 비교: {payload['paired_outcomes']}",
             f'- 실행 진단 기록: {dict(markers)}',
             '- PBT4는 과거 100문제 스냅샷이며 PBT5는 나중에 추가된 코드 형식 정리기를 포함한다.',
             '- PBT5의 선택형 출력에는 PBT4의 구체적 claim이 없어서 GPT 후속 단계의 입력도 달라진다.',
             '- 두 모델의 판정 차이는 정답 여부가 아니다. PBT4 로그에서 파싱한 항목만 비교한다.', '',
             '## 속성 판정 교차표', '', '| PBT4 ↓ / PBT5 → | ' + ' | '.join(STATUSES) + ' |',
             '|---|' + '---:|'*len(STATUSES)]
    for a in STATUSES:
        lines.append('| ' + a + ' | ' + ' | '.join(str(matrix[(a,b)]) for b in STATUSES) + ' |')
    lines += ['', '## 문제별 결과와 질문', '', '| 문제 | PBT4 | PBT5 | PBT5 판정 수 | PBT5 질문 |', '|---|---|---|---:|---|']
    for c in cases:
        q=str(c['question'] or '없음').replace('\n',' ').replace('|','\\|')
        lines.append(f"| {c['task_id']} | {'통과' if c['pbt4_pass'] else '실패'} | {'통과' if c['pbt5_pass'] else '실패'} | {c['decision_count']} | {q} |")
    (run / 'PBT5_ANALYSIS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k != 'cases'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

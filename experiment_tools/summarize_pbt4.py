#!/usr/bin/env python3
"""Summarize PBT4's recorded intermediate model outputs without model calls."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from clarify.algorithms.pbt_clarifier4 import _valid_pairs
from analyze_run import extract_traces, _extract_json


def main() -> None:
    run = Path(sys.argv[1]).resolve()
    rows = [json.loads(line) for line in (run / 'results.jsonl').read_text().splitlines() if line.strip()]
    traces, diagnostics = extract_traces(run, rows)
    statuses: collections.Counter[str] = collections.Counter()
    source: collections.Counter[str] = collections.Counter()
    scan_coverage: collections.Counter[int] = collections.Counter()
    records = []
    for row in rows:
        trace = traces.get((row['task_id'], row['prompt']))
        if not trace:
            continue
        scan: dict[int, str] = {}
        pair_response = None
        selection = None
        direct = None
        last_primary_stage = None
        for event in trace['events']:
            stage = event['stage']
            if stage == 'format_repair':
                stage = last_primary_stage
            elif stage != 'other':
                last_primary_stage = stage
            try:
                response = _extract_json(event['response'])
            except (ValueError, TypeError):
                continue
            if stage == 'property_classification' and isinstance(response.get('properties'), list):
                for item in response['properties']:
                    if isinstance(item, dict) and type(item.get('id')) is int and isinstance(item.get('status'), str):
                        scan[item['id']] = item['status']
            elif stage == 'contradiction_gate':
                direct = response
            elif stage == 'property_conflict_detection':
                pair_response = response
            elif stage == 'conflict_question_selection':
                selection = response
        statuses.update(scan.values())
        scan_coverage[len(scan)] += 1
        relevant = {i for i, status in scan.items() if status in ('established', 'ambiguous')}
        raw = pair_response.get('conflicts', []) if isinstance(pair_response, dict) else []
        if not isinstance(raw, list):
            raw = []
        valid = [p for p in raw if _valid_pairs({'conflicts': [p]}, relevant, row['prompt'])]
        selected = selection.get('source') if isinstance(selection, dict) else None
        source[selected or ('property_fallback_or_unknown' if row['clarification_history'] else 'no_question_or_unknown')] += 1
        records.append({'task_id': row['task_id'], 'success': row['success'],
                        'question': row['clarification_history'][0][0] if row['clarification_history'] else None,
                        'answer': row['clarification_history'][0][3] if row['clarification_history'] else None,
                        'scan_ids_in_trace': len(scan), 'scan_status_counts': dict(collections.Counter(scan.values())),
                        'direct_candidate': direct, 'valid_property_pairs_observed': valid,
                        'selection_observed': selection})
    markers = collections.Counter()
    for log in run.glob('*-generate.log'):
        text = log.read_text(encoding='utf-8', errors='replace')
        for marker in ('PROPERTY_PAIR_DISCARDED', 'PROPERTY_PAIR_VALIDATION_FAILED',
                       'DIRECT_CONFLICT_VALIDATION_FAILED', 'PROPERTY_SCAN_FAILED',
                       'CONFLICT_SELECTION_FAILED', 'PROPERTY_QUESTION_VALIDATION_FAILED'):
            markers[marker] += text.count(marker)
    payload = {'trace_diagnostics': diagnostics, 'scan_coverage': dict(scan_coverage),
               'status_counts_from_parseable_logs': dict(statuses), 'selection_sources_observed': dict(source),
               'validation_markers': dict(markers), 'cases': records}
    (run / 'PBT4_TRACE_SUMMARY.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    lines = ['# PBT4 중간 판정 요약', '',
             f"- 추적 로그를 문제와 연결: {diagnostics['matched']}/{len(rows)}",
             f'- 로그에서 읽은 속성 ID 개수별 문제 수: {dict(scan_coverage)}',
             f'- 로그에서 읽은 속성 판정 수: {dict(statuses)}',
             f'- 로그에서 확인한 충돌 질문 선택 출처: {dict(source)}',
             f'- 형식 검증 기록: {dict(markers)}',
             '- 로그의 JSON 파싱이나 재시도 연결이 불완전할 수 있어 위 수치는 전체 모델 판정과 다를 수 있다.',
             '- 속성 간 충돌 여부는 LLM의 판단이며, 검증은 주로 형식과 인용 일치 여부를 확인한다.', '',
             '| 문제 | 결과 | 속성별 충돌 후보 | 선택 출처 | 질문 |',
             '|---|---|---:|---|---|']
    for r in records:
        question = str(r['question'] or '없음').replace('\n', ' ').replace('|', '\\|')
        selected = (r['selection_observed'] or {}).get('source', '확인 불가')
        lines.append(f"| {r['task_id']} | {'통과' if r['success'] else '실패'} | {len(r['valid_property_pairs_observed'])} | {selected} | {question} |")
    (run / 'PBT4_TRACE_SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in payload.items() if k != 'cases'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

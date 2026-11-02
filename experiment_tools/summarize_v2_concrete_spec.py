#!/usr/bin/env python3
"""Summarize completed V2 gate decisions on the frozen train100 sample; no model calls."""
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / '.local/train100-v1'


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def digest(row):
    return hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest()


def main():
    run = Path(sys.argv[1]).resolve()
    rows = read(run / 'results.jsonl')
    manifest = json.loads((BENCH / 'manifest.json').read_text())
    strata = {r['task_id']: (r['dataset'], r['source']) for r in manifest['tasks']}
    old = {r['task_id']: r for r in read(BENCH / 'v1_1-decision-properties-20261101/results.jsonl')}
    records, diagnostics = {}, collections.Counter()
    token = 'V1_CONCRETE_GATE_JSON '
    for log in sorted(run.glob('*-generate.log')):
        output = log.with_name(log.name.replace('-generate.log', '-output.jsonl'))
        if not output.exists():
            diagnostics['missing_segment_output'] += 1
            continue
        completed = {digest(r) for r in read(output)}
        for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
            if token not in line:
                continue
            try:
                event = json.loads(line.split(token, 1)[1]); h = event['prompt_sha256']
            except (ValueError, KeyError):
                diagnostics['malformed'] += 1
                continue
            if h not in completed:
                diagnostics['unfinished_ignored'] += 1
                continue
            if h in records:
                raise ValueError(f'duplicate gate log for completed task: {h}')
            records[h] = event['data']
    groups = collections.defaultdict(collections.Counter)
    cases = []
    for row in rows:
        ident = row['task_id']; gate = records.get(digest(row)); history = row['clarification_history']
        if ident not in old or old[ident]['prompt'] != row['prompt']:
            raise ValueError(f'No matching v1_1 task: {ident}')
        dataset, source = strata[ident]
        selected = bool(gate and gate.get('ask') and history and
                        ' '.join(gate['question'].split()) == ' '.join(history[0][0].split()))
        issue = gate.get('issue', 'invalid_or_missing') if gate else 'invalid_or_missing'
        for group in ('all', dataset, f'{dataset}/{source}'):
            c = groups[group]; c['n'] += 1; c['gate_asked'] += selected
            c['gate_not_selected'] += not selected; c['passed'] += row['success']
            c['v1_1_passed'] += old[ident]['success']; c['questions'] += bool(history)
            c['gate_pass'] += selected and row['success']; c['gate_fail'] += selected and not row['success']
            c['no_gate_pass'] += not selected and row['success']; c['v2_only'] += row['success'] and not old[ident]['success']
            c['v1_1_only'] += old[ident]['success'] and not row['success']
            if selected: c['issue:' + issue] += 1
        cases.append({'task_id':ident,'dataset':dataset,'source':source,'success':row['success'],
                      'v1_1_success':old[ident]['success'],'gate_selected':selected,'gate':gate,
                      'question':history[0][0] if history else None,
                      'quality':history[0][2] if history else None,'answer':history[0][3] if history and len(history[0])>3 else None,
                      'v1_1_question':old[ident]['clarification_history'][0][0] if old[ident]['clarification_history'] else None,
                      'test_result':row.get('test_result'),'prompt':row['prompt']})
    payload = {'groups':{k:dict(v) for k,v in groups.items()},'diagnostics':dict(diagnostics),
               'matched_gate_records':len(records),'cases':cases}
    (run/'V2_ANALYSIS.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# v2 concrete spec gate 분석','',f'- 기록을 연결한 문제: {len(records)}/{len(rows)}',
           '- 게이트 판정은 모델의 판정으로 정답 표기가 아니다.',
           '- 기존 v1_1과 문제와 채점 설정은 같지만 모델 응답은 확률적이며 실행 시점이 다르다.', '',
           '| 표본 | 문제 | 게이트 질문 | 전체 질문 | v2 통과 | v1_1 통과 | v2만 통과 | v1_1만 통과 |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k in ('all','humaneval','humaneval/original','humaneval/larbi_contradictory','mbpp','mbpp/original','mbpp/larbi_contradictory'):
        c=groups[k];lines.append(f'| {k} | {c["n"]} | {c["gate_asked"]} | {c["questions"]} | {c["passed"]} | {c["v1_1_passed"]} | {c["v2_only"]} | {c["v1_1_only"]} |')
    lines+=['','## 문제별 게이트와 결과','','| 문제 | 분류 | 게이트 | v2 / v1_1 | 질문 |','|---|---|---|---|---|']
    for r in cases:
        question=str(r['question'] or '없음').replace('\n',' ').replace('|','\\|')
        lines.append(f'| {r["task_id"]} | {r["dataset"]}/{r["source"]} | {r["gate"].get("issue", "미확인") if r["gate"] else "미확인"} | {"통과" if r["success"] else "실패"} / {"통과" if r["v1_1_success"] else "실패"} | {question} |')
    (run/'V2_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='cases'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Compare a completed multi-turn v2 run with the frozen one-turn v2 run."""
from __future__ import annotations
import collections
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / '.local/train100-v1'


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def hash_prompt(row):
    return hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest()


def metric(rows):
    n = len(rows)
    tds = sum(math.log(10) / math.log(10 + len(r['clarification_history'])) for r in rows if r['success']) / n
    ndcg = 0.0
    for row in rows:
        history = row['clarification_history']
        gains = [math.log(2) / math.log(i + 2) for i in range(len(history))]
        if gains:
            ndcg += sum(g for g, h in zip(gains, history) if str(h[2]) == '3') / sum(gains)
    return {'n': n, 'pass': sum(r['success'] for r in rows), 'tds': tds, 'ndcg': ndcg / n,
            'questioned': sum(bool(r['clarification_history']) for r in rows),
            'total_turns': sum(len(r['clarification_history']) for r in rows),
            'turn_distribution': dict(collections.Counter(str(len(r['clarification_history'])) for r in rows)),
            'quality': dict(collections.Counter(str(h[2]) for r in rows for h in r['clarification_history'])),
            'recorded_cost': sum(float(r.get('prompt_cost', 0) or 0) + float(r.get('clarification_cost', 0) or 0) for r in rows)}


def norm(s):
    return ' '.join(str(s).split())


def failure_kind(row):
    if row['success']: return 'pass'
    text = str(row.get('test_result', ''))
    if re.search(r'takes .* positional arguments? but .* (?:was|were) given|missing \d+ required positional arguments?', text): return 'arity'
    for t in ('AssertionError', 'TypeError', 'ValueError', 'SyntaxError', 'Timeout'):
        if t in text: return t
    return 'other'


def main():
    run = Path(sys.argv[1]).resolve()
    state = json.loads((run/'experiment.json').read_text())
    if state.get('max_clarification_turns') != 3: raise ValueError('Expected recorded maximum of three turns')
    newer, older = read(run/'results.jsonl'), read(BENCH/'v2-concrete-spec-20261102/results.jsonl')
    old = {(r['task_id'], r['prompt']): r for r in older}
    if len(newer)!=100 or len(old)!=100 or {(r['task_id'],r['prompt']) for r in newer} != set(old):
        raise ValueError('The two result files must match the frozen 100 task IDs and prompts')
    if any(len(r['clarification_history']) > 3 for r in newer): raise ValueError('Exceeded question budget')
    manifest = json.loads((BENCH/'manifest.json').read_text())
    strata = {r['task_id']: (r['dataset'], r['source']) for r in manifest['tasks']}
    events = collections.defaultdict(list); diag = collections.Counter()
    tokens = ('TURN', 'CONCRETE_GATE', 'DUPLICATE_SKIPPED')
    for log in sorted(run.glob('*-generate.log')):
        output=log.with_name(log.name.replace('-generate.log','-output.jsonl'))
        if not output.exists(): diag['missing_output'] += 1; continue
        completed={hash_prompt(r) for r in read(output)}
        for line in log.read_text(encoding='utf-8',errors='replace').splitlines():
            for typ in tokens:
                prefix='V1_'+typ+'_JSON '
                if prefix not in line: continue
                try: event=json.loads(line.split(prefix,1)[1]); h=event['prompt_sha256']
                except (ValueError, KeyError): diag['malformed_event']+=1; continue
                if h not in completed: diag['unfinished_ignored']+=1; continue
                events[h].append({'type':typ,'data':event['data']})
    cases=[]; source=collections.Counter(); turns_by_number=collections.Counter()
    for row in newer:
        previous=old[(row['task_id'],row['prompt'])]; history=row['clarification_history']; ev=events[hash_prompt(row)]
        traced=[e['data'] for e in ev if e['type']=='TURN']
        if len(traced)!=len(history) or any(t['turn']!=i+1 or norm(t['question'])!=norm(h[0]) for i,(t,h) in enumerate(zip(traced,history))):
            diag['turn_trace_mismatch']+=1
        for i,t in enumerate(traced,1): source[t['source']]+=1;turns_by_number[(str(i),t['source'])]+=1
        cases.append({'task_id':row['task_id'],'dataset':strata[row['task_id']][0], 'stratum':strata[row['task_id']][1],
            'success':row['success'],'old_success':previous['success'], 'new_failure_kind':failure_kind(row),
            'old_failure_kind':failure_kind(previous),'prompt':row['prompt'], 'turns':[{'question':h[0],'requirement_id':h[1],
             'quality':h[2], 'answer':h[3] if len(h)>3 else None, 'source':traced[i]['source'] if i < len(traced) else 'unmatched'}
              for i,h in enumerate(history)],'old_history':previous['clarification_history'], 'test_result':row.get('test_result'),
            'gate_decisions':[e['data'] for e in ev if e['type']=='CONCRETE_GATE'],
            'duplicate_skips':[e['data'] for e in ev if e['type']=='DUPLICATE_SKIPPED']})
    groups={}
    for name in ('all','humaneval','mbpp','humaneval/original','humaneval/larbi_contradictory','mbpp/original','mbpp/larbi_contradictory'):
        def member(r):
            a,b=strata[r['task_id']]
            return name=='all' or name==a or name==f'{a}/{b}'
        nr=[r for r in newer if member(r)];pr=[old[(r['task_id'],r['prompt'])] for r in nr]
        groups[name]={'new':metric(nr),'old':metric(pr), 'both_pass':sum(a['success'] and b['success'] for a,b in zip(nr,pr)),
           'new_only':sum(a['success'] and not b['success'] for a,b in zip(nr,pr)),
           'old_only':sum(not a['success'] and b['success'] for a,b in zip(nr,pr)),
           'both_fail':sum(not a['success'] and not b['success'] for a,b in zip(nr,pr))}
    payload={'groups':groups,'turn_sources':dict(source),'turn_number_sources':{f'{k[0]}:{k[1]}':v for k,v in turns_by_number.items()},
      'diagnostics':dict(diag),'gate_format_errors':sum(d.get('status')=='invalid_model_output' for c in cases for d in c['gate_decisions']),
      'duplicate_skips':sum(len(c['duplicate_skips']) for c in cases),
      'failures_new':dict(collections.Counter(failure_kind(r) for r in newer if not r['success'])),
      'failures_old':dict(collections.Counter(failure_kind(r) for r in older if not r['success'])),'cases':cases}
    (run/'MULTITURN_ANALYSIS.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# v2 3회 루프 비교 분석','', '- 동일한 고정 train 100문제와 현재 채점 기준.',
      '- 기존 1회 v2와 새 3회 루프는 최대 턴뿐 아니라 반복 구조·프롬프트가 다르므로 차이를 턴 수만의 효과로 해석할 수 없다.',
      '- 모델·가상 사용자 응답은 확률적이며, 기록 비용은 라이브러리 추정치다.', '',
      '| 표본 | 기존 통과 | 3회 루프 통과 | 기존 TDS | 루프 TDS | 기존만 통과 | 루프만 통과 |', '|---|---:|---:|---:|---:|---:|---:|']
    for name,g in groups.items():
        o,n=g['old'],g['new'];lines.append(f'| {name} | {o["pass"]}/{o["n"]} | {n["pass"]}/{n["n"]} | {o["tds"]:.4f} | {n["tds"]:.4f} | {g["old_only"]} | {g["new_only"]} |')
    lines += ['', f'질문 수 분포: {groups["all"]["new"]["turn_distribution"]}',
              f'질문 단계: {dict(source)}',f'로그 매칭 진단: {dict(diag)}','', '## 문제별 대화', '']
    for c in cases:
        lines += [f'### {c["task_id"]} ({c["dataset"]}/{c["stratum"]})', '',
                  f'통과: 기존 {c["old_success"]}, 3회 루프 {c["success"]}.', '']
        for i,t in enumerate(c['turns'],1):
            lines += [f'{i}. [{t["source"]}, 품질 {t["quality"]}] 질문: {t["question"]}',f'   답변: {t["answer"]}']
        if not c['turns']: lines.append('질문 없음.')
        lines.append('')
    (run/'MULTITURN_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='cases'},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()

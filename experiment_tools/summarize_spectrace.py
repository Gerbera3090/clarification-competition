#!/usr/bin/env python3
"""Summarize logged requirements and verification decisions without LLM calls."""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main() -> None:
    run = Path(sys.argv[1]).resolve()
    benchmark = run.parent
    rows = read(run/'results.jsonl')
    manifest = json.loads((benchmark/'manifest.json').read_text())
    strata = {r['task_id']:(r['dataset'],r['source']) for r in manifest['tasks']}
    records = collections.defaultdict(dict)
    diagnostics = collections.Counter()
    for path in sorted(run.glob('*-generate.log')):
        # An interrupted log may include an unfinished extra task. Match only
        # tasks actually present in this segment's result file, so a retry does
        # not duplicate events from an abandoned attempt.
        segment_output = path.with_name(path.name.replace('-generate.log', '-output.jsonl'))
        if not segment_output.exists():
            diagnostics['missing_segment_output'] += 1
            continue
        completed = {hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest()
                     for row in read(segment_output)}
        for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
            for stage in ('REQUIREMENTS','CONFLICT','VERIFICATION'):
                token=f'SPECTRACE_{stage}_JSON '
                if token in line:
                    try: event=json.loads(line.split(token,1)[1])
                    except ValueError:
                        diagnostics['malformed_logs']+=1
                        continue
                    h=event['prompt_sha256']
                    if h not in completed:
                        diagnostics['unfinished_events_ignored'] += 1
                        continue
                    if stage in records[h]:
                        raise ValueError(f'Duplicate {stage} record for {h}')
                    records[h][stage]=event['data']
            for marker in ('SPECTRACE_EXTRACTION_INVALID','SPECTRACE_CONFLICT_INVALID','SPECTRACE_VERIFICATION_INVALID'):
                if marker in line: diagnostics[marker]+=1
    metrics=collections.Counter(); group=collections.defaultdict(collections.Counter); cases=[]
    for row in rows:
        h=hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest();rec=records.get(h,{})
        requirements=rec.get('REQUIREMENTS',{})
        conflict=rec.get('CONFLICT',{})
        verify=rec.get('VERIFICATION',{})
        candidate=conflict.get('conflict') is True
        confirmed=verify.get('confirmed') is True
        rejected=verify.get('confirmed') is False
        asked=bool(row['clarification_history']);passed=row['success']
        metrics['requirements_logged']+=bool(requirements)
        metrics['requirements_total']+=len(requirements.get('items',[]))
        metrics['requirements_discarded']+=requirements.get('discarded',0)
        metrics['conflict_candidates']+=candidate
        metrics['confirmed_candidates']+=confirmed
        metrics['rejected_candidates']+=rejected
        metrics['questions']+=asked
        metrics['pass']+=passed
        g=group[' / '.join(strata[row['task_id']])]
        g['tasks']+=1;g['candidates']+=candidate;g['confirmed']+=confirmed;g['asked']+=asked;g['pass']+=passed
        hist=row['clarification_history']
        cases.append({'task_id':row['task_id'],'success':passed, 'stratum':list(strata[row['task_id']]),
                      'requirements':requirements,'conflict':conflict,'verification':verify,
                      'question':hist[0][0] if hist else None, 'answer':hist[0][3] if hist else None})
    payload={'count':len(rows),'metrics':dict(metrics),'strata':dict(group),'diagnostics':dict(diagnostics),'cases':cases}
    (run/'SPECTRACE_ANALYSIS.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# SpecTrace 명세 충돌 분석', '',f'- 고정 문제: {len(rows)}개',
           f'- 원문에 연결한 요구사항 기록: {metrics["requirements_logged"]}문제, {metrics["requirements_total"]}개',
           f'- 원문 인용 검증에서 제외된 요구: {metrics["requirements_discarded"]}개',
           f'- 모델이 제시한 충돌 후보: {metrics["conflict_candidates"]}문제',
           f'- 확인 모델이 수용: {metrics["confirmed_candidates"]}문제, 기각: {metrics["rejected_candidates"]}문제',
           f'- 질문: {metrics["questions"]}문제, 코드 통과: {metrics["pass"]}문제',
           f'- 형식 검증과 중단 로그 진단: {dict(diagnostics)} (형식 오류 횟수는 중단된 시도도 포함할 수 있음)',
           '- 후보·검증은 모두 LLM의 판단이며 참 충돌 여부를 증명하거나 실제 테스트를 실행한 결과가 아니다.',
           '- 원본/모순 변형 출처 표시는 데이터 구성 정보이며 모든 개별 문장의 충돌 정답을 뜻하지 않는다.', '',
           '## 데이터 출처별', '', '| 데이터 / 출처 | 문제 | 충돌 후보 | 확인 통과 | 질문 | 코드 통과 |', '|---|---:|---:|---:|---:|---:|']
    for name,ct in sorted(group.items()):
        lines.append(f'| {name} | {ct["tasks"]} | {ct["candidates"]} | {ct["confirmed"]} | {ct["asked"]} | {ct["pass"]} |')
    lines += ['', '## 문제별 질문', '', '| 문제 | 통과 | 후보 | 확인 결과 | 질문 |', '|---|---|---|---|---|']
    for c in cases:
        cand='있음' if c['conflict'].get('conflict') else '없음'
        verification=c['verification'].get('confirmed')
        verdict='수용' if verification is True else '기각' if verification is False else '없음'
        q=str(c['question'] or '없음').replace('\n',' ').replace('|','\\|')
        lines.append(f'| {c["task_id"]} | {"통과" if c["success"] else "실패"} | {cand} | {verdict} | {q} |')
    (run/'SPECTRACE_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='cases'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Summarize v1's five-viewpoint logs and code-comparison availability."""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path

STAGES = ('SIMPLE','STRUCTURE','STRUCTURED','INSTRUCTION_EXAMPLE','PROPERTIES',
          'CODE_OBSERVATIONS','CODE_COMPARISON','FINAL')


def read(path: Path) -> list[dict]:
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def main() -> None:
    run=Path(sys.argv[1]).resolve()
    rows=read(run/'results.jsonl')
    task_hash={hashlib.sha256(r['prompt'].encode('utf-8')).hexdigest():r for r in rows}
    records=collections.defaultdict(dict)
    diagnostics=collections.Counter()
    for log in sorted(run.glob('*-generate.log')):
        output=log.with_name(log.name.replace('-generate.log','-output.jsonl'))
        if not output.exists():
            diagnostics['missing_segment_output']+=1
            continue
        valid={hashlib.sha256(r['prompt'].encode('utf-8')).hexdigest() for r in read(output)}
        for line in log.read_text(encoding='utf-8',errors='replace').splitlines():
            for stage in STAGES:
                token=f'V1_{stage}_JSON '
                if token not in line:continue
                try:event=json.loads(line.split(token,1)[1]); h=event['prompt_sha256']
                except (ValueError,KeyError):diagnostics['malformed_event']+=1;continue
                if h not in valid:
                    diagnostics['unfinished_event_ignored']+=1;continue
                if stage in records[h]:raise ValueError(f'duplicate completed log event: {h} {stage}')
                records[h][stage]=event['data']
    metrics=collections.Counter();views={s:collections.Counter() for s in ('SIMPLE','STRUCTURED','INSTRUCTION_EXAMPLE','PROPERTIES','CODE_COMPARISON')}; sources=collections.Counter();cases=[]
    for row in rows:
        h=hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest();rec=records.get(h,{})
        metrics['tasks']+=1;metrics['log_matched']+=bool(rec);metrics['passed']+=row['success'];metrics['asked']+=bool(row['clarification_history'])
        for stage in views:
            data=rec.get(stage,{})
            status=data.get('status','missing')
            views[stage][status]+=1
            if status=='ok':views[stage]['conflict_true']+=data.get('has_conflict') is True
        structure=rec.get('STRUCTURE',{});metrics['tasks_with_grounded_examples']+=bool(structure.get('examples'))
        code=rec.get('CODE_OBSERVATIONS',{});a=code.get('instruction_execution',{});b=code.get('example_execution',{})
        if a.get('status')=='ok' and b.get('status')=='ok':
            metrics['both_code_executed']+=1
            x=a.get('observations',[]);y=b.get('observations',[])
            if len(x)==len(y) and any((u.get('kind'),u.get('value'))!=(v.get('kind'),v.get('value')) for u,v in zip(x,y)):
                metrics['runtime_observations_differ']+=1
        elif code.get('status')!='unavailable_no_instruction_or_example':
            metrics['code_comparison_unavailable_or_incomplete']+=1
        final=rec.get('FINAL',{})
        for src in final.get('sources',[]):
            if isinstance(src,str):sources[src]+=1
        hist=row.get('clarification_history') or []
        cases.append({'task_id':row['task_id'],'success':row['success'],
                      'question':hist[0][0] if hist else None,'answer':hist[0][3] if hist else None,
                      'reports':rec})
    payload={'metrics':dict(metrics),'views':{k:dict(v) for k,v in views.items()},
             'final_sources_as_reported':dict(sources),'diagnostics':dict(diagnostics),'cases':cases}
    (run/'V1_ANALYSIS.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# v1_multi_judge 다섯 관점 분석','',f'- 완료 문제 / 로그 연결: {len(rows)} / {metrics["log_matched"]}',
           f'- 코드 통과: {metrics["passed"]}; 질문: {metrics["asked"]}',
           f'- 원문 예시가 추출된 문제: {metrics["tasks_with_grounded_examples"]}',
           f'- 두 후보 코드를 예시 입력에서 모두 실행: {metrics["both_code_executed"]}',
           f'- 두 코드의 관찰 결과가 다른 문제: {metrics["runtime_observations_differ"]}',
           f'- 코드 비교가 준비됐으나 실행이 불완전하거나 불가: {metrics["code_comparison_unavailable_or_incomplete"]}',
           f'- 추적 진단: {dict(diagnostics)}',
           '- 모델 판단과 후보 코드 실행 결과는 가설이다. 서로 다른 결과가 실제 명세 충돌을 증명하지 않는다.',
           '- 예시 입력은 모델이 원문에서 추출했으므로 부정확할 수 있고, 후보 코드가 자체적으로 틀릴 수 있다.', '',
           '## 관점별 결과', '', '| 관점 | 정상 판정 | 충돌 후보 | 사용 불가·형식 오류 등 |', '|---|---:|---:|---|']
    for stage,c in views.items():
        remainder={k:v for k,v in c.items() if k not in {'ok','conflict_true'} and v}
        lines.append(f'| {stage} | {c["ok"]} | {c["conflict_true"]} | {remainder or "없음"} |')
    lines += ['', f'최종 모델이 스스로 표기한 선택 출처: {dict(sources)}. 검증된 인과관계는 아니다.', '',
              '## 문제별 질문', '', '| 문제 | 통과 | 질문 |', '|---|---|---|']
    for c in cases:
        q=str(c['question'] or '없음').replace('\n',' ').replace('|','\\|')
        lines.append(f'| {c["task_id"]} | {"통과" if c["success"] else "실패"} | {q} |')
    (run/'V1_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='cases'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

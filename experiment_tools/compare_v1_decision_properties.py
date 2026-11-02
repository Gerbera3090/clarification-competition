#!/usr/bin/env python3
"""Compare logged v1/v1_1 reports without claiming causal attribution."""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
B=ROOT/'.local/train100-v1'
OLD=B/'v1-multi-judge-v2-20261101'
NEW=B/'v1_1-decision-properties-20261101'


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main()->None:
    a=load(OLD/'V1_ANALYSIS.json')['cases'];b=load(NEW/'V1_ANALYSIS.json')['cases']
    old={x['task_id']:x for x in a}
    if len(old)!=100 or len(b)!=100 or set(old)!={x['task_id'] for x in b}:
        raise ValueError('Expected the same 100 task IDs')
    flags=collections.Counter();choices=collections.Counter();totals=collections.Counter();cited=collections.Counter();pairs=[]
    for item in b:
        prev=old[item['task_id']];x=prev['reports'].get('PROPERTIES',{});y=item['reports'].get('PROPERTIES',{})
        old_flag=x.get('has_conflict') if x.get('status')=='ok' else 'unavailable'
        new_flag=y.get('has_conflict') if y.get('status')=='ok' else 'unavailable'
        flags[(str(old_flag),str(new_flag))]+=1
        prop=y.get('properties',[]);decisions=y.get('pair_decisions',[])
        totals['properties']+=len(prop);totals['discarded']+=y.get('discarded',0);totals['pairs']+=len(decisions)
        totals['decision_batches']+=(len(decisions)+63)//64
        choices.update(str(z.get('choice')) for z in decisions)
        sources=item['reports'].get('FINAL',{}).get('sources') or []
        if item['question'] and 'properties' in sources:cited[str(new_flag)]+=1
        pairs.append({'task_id':item['task_id'],'v1_property_conflict':old_flag,'v1_1_property_conflict':new_flag,
                      'v1_pass':prev['success'],'v1_1_pass':item['success'],
                      'v1_question':prev['question'],'v1_1_question':item['question'],
                      'properties':prop,'pair_decisions':decisions,'final_sources':sources})
    outcomes=collections.Counter((x['v1_pass'],x['v1_1_pass']) for x in pairs)
    (NEW/'DECISION_COMPARISON.json').write_text(json.dumps({'cross':{f'{x} -> {y}':n for (x,y),n in flags.items()},
        'totals':dict(totals),'pair_choices':dict(choices),'question_property_citations':dict(cited),
        'paired_outcomes':{str(k):v for k,v in outcomes.items()},'cases':pairs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# v1과 v1_1 — 속성 판정 비교', '',
           '- 동일한 100개 문제와 GPT-4.1 mini, 같은 SDK를 사용한 두 개의 독립 실행이다.',
           '- v1_1은 자유 텍스트 속성 추출에는 GPT를 쓰고 각 속성 쌍의 충돌 여부에 GPT-6 Luna Decisions를 사용한다.',
           '- v1_1에서는 속성 추출 프롬프트와 최종 모델에 전달되는 속성 결과 형식도 바뀌었으므로 모델 교체만의 순수 효과는 아니다.',
           '- 속성 목록 자체가 서로 다르므로 같은 문제의 충돌 여부 비교는 동일한 속성 쌍에 대한 정확도 비교가 아니다.',
           f'- v1_1 검증 통과 속성 {totals["properties"]}개, 인용이나 필수 필드 검증으로 제외 {totals["discarded"]}개, decision 요청 {totals["decision_batches"]}회, 속성 쌍 {totals["pairs"]}개.',
           f'- 속성 쌍 분류: {dict(choices)}. 실제 정답 라벨은 없다.',
           f'- 같은 문제에서 속성 관점의 충돌 유무: {dict((str(k),v) for k,v in flags.items())}',
           f'- 최종 질문에서 properties를 출처로 자기표시한 건의 속성 판정: {dict(cited)}. 표기는 인과 효과가 아니다.',
           f'- 짝지은 코드 결과 (v1 통과, v1_1 통과): {dict((str(k),v) for k,v in outcomes.items())}', '',
           '| 문제 | v1 속성 충돌 | v1_1 속성 충돌 | v1 결과 | v1_1 결과 | v1_1 질문 |', '|---|---|---|---|---|---|']
    for x in pairs:
        q=str(x['v1_1_question'] or '없음').replace('\n',' ').replace('|','\\|')
        lines.append(f"| {x['task_id']} | {x['v1_property_conflict']} | {x['v1_1_property_conflict']} | {'통과' if x['v1_pass'] else '실패'} | {'통과' if x['v1_1_pass'] else '실패'} | {q} |")
    (NEW/'DECISION_COMPARISON.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Property comparison written:',NEW/'DECISION_COMPARISON.md')


if __name__=='__main__':main()

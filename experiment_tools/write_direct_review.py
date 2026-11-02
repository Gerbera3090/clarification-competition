#!/usr/bin/env python3
"""Render explicit human-readable review opinions with actual saved outcomes.

Review opinions are manually authored and are neither benchmark ground truth nor
blinded judgments. No model calls are made. A later run can be added when ready.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BENCH=ROOT/'.local/train100-v1'
REVIEW=BENCH/'v1_1-decision-properties-20261101/direct-review'


def read(p:Path)->list[dict]:
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]


def main()->None:
    annotations=read(REVIEW/'annotations.jsonl')
    opinions=read(REVIEW/'v1-question-review.jsonl')
    by_id={r['id']:r for r in annotations};opinions_by={r['id']:r for r in opinions}
    manifest=json.loads((BENCH/'manifest.json').read_text()); expected={m['task_id']:m for m in manifest['tasks']}
    if len(by_id)!=100 or len(opinions_by)!=100 or set(by_id)!=set(expected) or set(opinions_by)!=set(expected):
        raise ValueError('Manual reviews do not cover the 100 frozen tasks uniquely')
    run1=BENCH/'v1-multi-judge-v2-20261101';rows=read(run1/'results.jsonl');v1={r['task_id']:r for r in rows}
    cases={x['task_id']:x for x in json.loads((run1/'V1_ANALYSIS.json').read_text())['cases']}
    run2=BENCH/'v1_1-decision-properties-20261101';path2=run2/'results.jsonl';v11={r['task_id']:r for r in read(path2)} if path2.exists() else {}
    v11_analysis_path=run2/'V1_ANALYSIS.json'
    v11_cases={c['task_id']:c for c in json.loads(v11_analysis_path.read_text(encoding='utf-8'))['cases']} if v11_analysis_path.exists() else {}
    v11_opinion_path=REVIEW/'v1_1-question-review.jsonl'
    v11_opinions={r['id']:r for r in read(v11_opinion_path)} if v11_opinion_path.exists() else {}
    if v11_opinions and (len(v11_opinions)!=100 or set(v11_opinions)!=set(expected)):
        raise ValueError('v1_1 question reviews do not cover the frozen 100 tasks uniquely')
    kinds=collections.Counter(r['kind'] for r in annotations);statuses=collections.Counter(r['assessment'] for r in opinions)
    v11_statuses=collections.Counter(r['assessment'] for r in v11_opinions.values())
    revised=sum(bool(r.get('revised_after_result_review')) for r in annotations)
    failures=collections.Counter();arity=[]
    for r in rows:
        if r['success']:continue
        err=r.get('test_result','');m=re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*(?:Error|Exception))(?::|$)',err)
        failures[m[-1] if m else ('timeout' if 'timeout' in err.lower() else 'unknown')]+=1
        if re.search(r'(?m)^TypeError: .*(?:positional argument|keyword argument).*',err):arity.append(r['task_id'])
    v11_failures=collections.Counter();v11_arity=[]
    for r in v11.values():
        if r['success']:continue
        err=r.get('test_result','');m=re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*(?:Error|Exception))(?::|$)',err)
        v11_failures[m[-1] if m else ('timeout' if 'timeout' in err.lower() else 'unknown')]+=1
        if re.search(r'(?m)^TypeError: .*(?:positional argument|keyword argument).*',err):v11_arity.append(r['task_id'])
    lines=['# v1·v1_1 고정 train 100문제 직접 검토', '',
           '- 문제 원문을 직접 읽고 우선 확인할 요구를 한 항목씩 적었다. 단일 검토자의 의견이며 정답 라벨이 아니다.',
           f'- 대화와 이전 실험 내용을 이미 알고 있었으므로 맹검 평가가 아니다. {revised}건은 실행 결과를 확인한 뒤 원문 의견을 수정했으며 해당 항목에 표시했다.',
           '- v1·v1_1 질문 평가는 하나의 우선 쟁점에 대한 의견이다. 서로 다른 타당한 질문이 있을 수 있어 다른 쟁점을 질문했다는 사실만으로 오답이라 할 수 없다.',
           '- 실패 유형은 채점 로그의 마지막 예외 형식을 기계적으로 나눈 것이며, 근본 원인을 증명하는 분류는 아니다.',
           f'- 원문 검토 분류: {dict(kinds)}', f'- v1 질문 검토 의견: {dict(statuses)}',
           f'- v1_1 질문 검토 의견: {dict(v11_statuses)}',
           f'- v1 실패 로그 47개: {dict(failures)}. 인자 개수 불일치 TypeError {len(arity)}건: {", ".join(arity)}.',
           f'- v1_1 실패 로그 {sum(v11_failures.values())}개: {dict(v11_failures)}. 인자 개수 불일치 TypeError {len(v11_arity)}건: {", ".join(v11_arity)}.',
           '- 고정 표본은 원본과 모순 변형만 포함한다. 별도 ambiguous/incomplete 변형 성능을 의미하지 않는다.', '',
           '| 문제 | 원문 분류 | 직접 짚은 핵심 | v1 질문 검토 | v1 결과 | v1_1 질문 검토 | v1_1 결과 |',
           '|---|---|---|---|---|---|---|']
    for row in rows:
        tid=row['task_id'];a=by_id[tid];q=opinions_by[tid];other=v11.get(tid)
        v11_review=v11_opinions.get(tid,{}).get('assessment','미검토')
        lines.append(f"| {tid} | {a['kind']} | {a['focus'].replace('|','/')} | {q['assessment']} | {'통과' if row['success'] else '실패'} | {v11_review} | {'통과' if other and other['success'] else '실패' if other else '미완료'} |")
    lines += ['', '# 문제별 상세', '']
    for row in rows:
        tid=row['task_id'];a=by_id[tid];op=opinions_by[tid];h=row.get('clarification_history') or [];other=v11.get(tid);h2=(other.get('clarification_history') or []) if other else [];sources=cases[tid]['reports'].get('FINAL',{}).get('sources',[])
        lines += [f'## {tid}', '',f'- 데이터 출처: {expected[tid]["dataset"]} / {expected[tid]["source"]}',
                  f'- 직접 본 분류: **{a["kind"]}**',f'- 우선 쟁점: {a["focus"]}',f'- 판단 근거: {a["evidence"]}',f'- 제안 질문: {a["question"]}',
                  f'- 질문 검토 의견: **{op["assessment"]}** — {op["reason"]}',
                  f'- 원문 판단 수정: {"결과 검토 후 수정함" if a.get("revised_after_result_review") else "원문 검토 후 유지"}',
                  f'- v1 최종 질문: {h[0][0] if h else "없음"}',f'- v1 가상 사용자 답: {h[0][3] if h else "없음"}',f'- v1 참고 관점 자기표시: {sources}',f'- v1 코드: {"통과" if row["success"] else "실패"}']
        if not row['success']:
            lines += ['', 'v1 채점 로그 발췌:', '', '````text',str(row.get('test_result',''))[:1800], '````']
        if other:
            lines += ['',f'- v1_1 최종 질문: {h2[0][0] if h2 else "없음"}',f'- v1_1 가상 사용자 답: {h2[0][3] if h2 else "없음"}',f'- v1_1 코드: {"통과" if other["success"] else "실패"}']
            if tid in v11_opinions:
                lines.append(f'- v1_1 질문 검토 의견: **{v11_opinions[tid]["assessment"]}** — {v11_opinions[tid]["reason"]}')
            if tid in v11_cases:
                reports=v11_cases[tid]['reports'];prop=reports.get('PROPERTIES',{});final=reports.get('FINAL',{})
                names=prop.get('properties',[]);flagged=[]
                for pair in prop.get('pair_decisions',[]):
                    if pair.get('choice')=='conflict' and pair.get('a',-1)<len(names) and pair.get('b',-1)<len(names):
                        flagged.append({'속성A':names[pair['a']].get('name'), '속성B':names[pair['b']].get('name'), 'confidence':pair.get('confidence')})
                lines += [f'- v1_1 추출 속성: {len(names)}개; decision 속성 쌍: {len(prop.get("pair_decisions",[]))}개',
                          f'- v1_1 decision이 충돌로 선택한 속성 쌍: {json.dumps(flagged,ensure_ascii=False)}',
                          f'- v1_1 최종 LLM의 참고 관점 자기표시: {final.get("sources",[])}']
            if not other['success']:
                lines += ['', 'v1_1 채점 로그 발췌:', '', '````text',str(other.get('test_result',''))[:1800], '````']
        lines += ['', '### 사용자 원문', '', '````text',row['prompt'].rstrip(), '````','']
    (REVIEW/'100문제_직접검토.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (REVIEW/'summary.json').write_text(json.dumps({'kinds':dict(kinds),'question_assessments':dict(statuses),
        'v1_1_question_assessments':dict(v11_statuses),'v1_failure_last_exception':dict(failures),
        'v1_arity_mismatch':arity,'v1_1_failure_last_exception':dict(v11_failures),
        'v1_1_arity_mismatch':v11_arity,'v11_completed':len(v11)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Direct review written:',REVIEW/'100문제_직접검토.md','v1_1 rows:',len(v11))


if __name__=='__main__':main()

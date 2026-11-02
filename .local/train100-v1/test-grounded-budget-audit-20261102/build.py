from pathlib import Path
import json,hashlib,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];TRAIN=ROOT/'.local/train100-v1'
def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
A={r['task_id']:r for r in read(ROOT/'.local/single-question-audit-20261030/audit100.jsonl')}
M={r['task_id']:r for r in read(ROOT/'.local/minimum-q3-audit-20261101/minimum_q3_100.jsonl')}
D=read(TRAIN/'runs/direct-gpt41mini/results.jsonl');P={r['task_id']:r for r in read(TRAIN/'PBT4-PropertyConflictGate-v2-20261030/results.jsonl')}
E=json.loads((HERE/'test-evidence.json').read_text());V=json.loads((HERE/'verification-summary.json').read_text())
T={r['task_id']:r for r in json.loads((TRAIN/'PBT4-PropertyConflictGate-v2-20261030/PBT4_TRACE_SUMMARY.json').read_text())['cases']}
BOTH={r['task_id']:r for r in read(TRAIN/'PBT4-PropertyConflictGate-v2-20261030/both-candidates-audit-20261101/audit.jsonl')}
GROUP={0:'inferred_without_question',1:'one_atomic_fact',2:'multiple_atomic_facts',None:'route_unestablished'}
LABEL={0:'추론으로 해결 가능',1:'한 사실 확인',2:'두 사실 확인',None:'평가·답변 근거 미확정'}
rows=[];widget=[]
for i,d in enumerate(D,1):
 task=d['task_id'];a=A[task];m=M[task];p=P[task];e=E[task]
 assert d['prompt']==p['prompt']==a['prompt']==m['prompt']
 assert hashlib.sha256(d['prompt'].encode()).hexdigest()==m['prompt_sha256']
 assert e['test_text'] and e['assertion_count']>0
 if e['authority']=='official_evalplus':assert e['reference_verification']['base_assertions_passed']
 n=m['minimum_q3_estimate'];assert n in (0,1,2,None)
 selected=(T[task].get('selection_observed')or{}).get('source','property_fallback')
 history=p['clarification_history'][0] if p['clarification_history'] else ['', '', '', '']
 qs=[{'fact_id':q['fact_id'],'question':q['question_ko'],'expected_answer':q['expected_answer_ko'],'support':q['hidden_support']} for q in m['optimal_questions']]
 row=dict(task_id=task,prompt_sha256=m['prompt_sha256'],join_key=m['join_key'],source_line=i,dataset=m['dataset'],source=m['source'],
  marking_profile='test-grounded-inference-aware-v2-20261102',test_grounded_review_status='reviewed',
  category=GROUP[n],category_label=LABEL[n],additional_atomic_facts_estimate=n,more_than_one_fact=n is not None and n>1,
  route_unestablished=n is None,formal_minimum_proven=False,confidence=m['confidence'],
  questions=qs,inferred_without_question=m['inferred_without_question'],reason=m['minimality_argument_ko'],
  remaining_gaps=m['after_answers_remaining_gaps'],resolution_status=m['resolution_status'],
  test_evidence=a['test_evidence_ko'],test_source=e,reference_base_assertions_checked=e['authority']=='official_evalplus',
  annotation_origin='Existing full-100 minimum-Q3 semantic judgments reviewed with current exact test sources and authoritative reference base checks; no new model/scorer calls.',
  pbt4_pass=p['success'],direct_pass=d['success'],pbt4_selected_source=selected,pbt4_question=history[0],pbt4_answer=history[3],
  prompt=d['prompt'],observed_pbt4_test_result=p['test_result'])
 if task in BOTH:row['previous_selected_question_audit']=BOTH[task]['audit']
 rows.append(row)
 # Compact detail payload: all values are from checked source records.
 testlines=[s.strip() for s in e['test_text'].splitlines() if s.strip().startswith('assert ')]
 if task=='HumanEval/149':testlines=[testlines[0],testlines[3],testlines[-1]]
 if task=='HumanEval/95':testlines=[s for s in testlines if 'STATE' in s or 'candidate({})' in s]
 widget.append(dict(id=task,short=task.replace('HumanEval/','HE').replace('Mbpp/','MB'),group='unknown' if n is None else str(n),n=n,
  label=LABEL[n],confidence=m['confidence'],reason=m['minimality_argument_ko'],facts=qs,
  gaps=m['after_answers_remaining_gaps'],inferred=m['inferred_without_question'],evidence=a['test_evidence_ko'],
  checks=testlines[:3],targets=e.get('reference_verification',{}).get('representative_targets',[]),
  source=e['authority'],testVerified=True,pass_=p['success'],question=history[0],answer=history[3],selected=selected))
assert len(rows)==len(widget)==100
summary={'population':100,'profile':'test-grounded-inference-aware-v2-20261102','reviewed':100,'verification':V,'groups':[],
 'source_distribution':dict(collections.Counter(r['test_source']['authority'] for r in rows)),
 'confidence':dict(collections.Counter(r['confidence'] for r in rows)),
 'overall_pbt4':{'pass':sum(r['pbt4_pass'] for r in rows),'n':100},'overall_direct':{'pass':sum(r['direct_pass'] for r in rows),'n':100},
 'no_new_llm_or_simulator_calls':True,'new_generated_code_benchmark_run':False,
 'semantic_labels_are_estimates':True,'all_plus_inputs_reexecuted':False}
for n in (0,1,2,None):
 g=[r for r in rows if r['additional_atomic_facts_estimate']==n]
 summary['groups'].append(dict(key='unknown' if n is None else str(n),label=LABEL[n],n=len(g),pbt4_pass=sum(r['pbt4_pass'] for r in g),direct_pass=sum(r['direct_pass'] for r in g),task_ids=[r['task_id'] for r in g]))
summary['multi_fact_task_ids']=[r['task_id'] for r in rows if r['more_than_one_fact']]
summary['route_unestablished_task_ids']=[r['task_id'] for r in rows if r['route_unestablished']]
(HERE/'labels.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
(HERE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(HERE/'visual-data.json').write_text(json.dumps({'rows':widget,'summary':summary},ensure_ascii=False)+'\n')
provenance={'date':'2026-11-02','source_files':{str(p):sha(p) for p in [ROOT/'.local/single-question-audit-20261030/audit100.jsonl',ROOT/'.local/minimum-q3-audit-20261101/minimum_q3_100.jsonl',TRAIN/'runs/direct-gpt41mini/results.jsonl',TRAIN/'PBT4-PropertyConflictGate-v2-20261030/results.jsonl',HERE/'test-evidence.json']},'script':str(Path(__file__).resolve()),'new_model_calls':0,'new_simulator_calls':0,'reference_checks':82,'fallback_test_sources_checked':18}
(HERE/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
# Update all 100 previous rows with an explicitly separate test-grounded profile.
oldpath=TRAIN/'question-budget-audit-20261101/labels.jsonl';old=read(oldpath);newmap={r['join_key']:r for r in rows}
for r in old:
 key=r['task_id']+'::'+r['prompt_sha256'];new=newmap[key]
 r.update(test_grounded_review_status='reviewed',test_grounded_budget_flag=new['category'],
  test_grounded_budget_risk=None if new['route_unestablished'] else new['more_than_one_fact'],
  test_grounded_fact_axes_estimate=new['additional_atomic_facts_estimate'],test_grounded_evidence_file=str(HERE/'labels.jsonl'),
  test_grounded_marking_profile=new['marking_profile'])
oldpath.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in old))
lines=['# 100문제 전체 테스트 기준 재마킹 — 2026-11-02','',
'현재 산출물은 train100-v1의 정확히 같은 프롬프트 100건 전체를 대상으로 한다. 기존의 프롬프트 기준 3/7/14/76 분류와 149 한 건만 테스트 기준으로 보완했던 중간 결과를 대체하는 별도 프로파일이다.','',
'## 확인 범위','',
'- task_id와 프롬프트 SHA-256을 기존 실행 및 두 기존 감사 자료와 100/100 대조했다.',
'- 실제 평가 테스트의 출처는 EvalPlus 82건, 데이터셋 fallback assert 18건이다. 테스트·canonical·참조 설명의 동일성을 확인했다.',
'- 공식 참조 함수 82개를 각 캐시의 기본 assert에 실행해 82/82 통과를 확인했다. fallback 18개는 별도 canonical이 없어 실제 assert와 기대값을 확인했다.',
'- plus 전체 입력을 이번에 모두 재실행하지 않았다. 계약과 canonical 및 분류를 구분하는 대표 plus 사례, 기존 테스트 검토 근거를 활용했다.',
'- 분류별 성공률은 기존 PBT4 실행의 48/100을 연결했다. 새 모델·가상 사용자 호출, 생성 코드의 새 벤치마크 실행은 하지 않았다. 현재 runtime의 함수명 수정 이후 재채점 결과도 아니다.','',
'## 마킹 기준','',
'세려는 것은 원문·예시·수학·Python 관례를 활용한 뒤, 실제 테스트가 구분하는 외부 행동 결정을 추가로 확인할 필요가 있는지다. 기존 100건 minimum-Q3 감사의 판단을 현재 테스트 원본과 대조해 재검토했다. 수학적 최소 질문 수 증명이나 실제 가상 사용자의 질문 품질 점수 측정은 아니다. 명시적 실행 제약이라도 실제 출력 판정과 구별되지 않는 조건을 별도 필수 질문으로 자동 가산하지 않았다.','',
'- **추론으로 해결 가능:** 이름·예시·정의·호환 입력 처리 등으로 별도 사용자 사실 없이 구현할 수 있다고 추정한다. 무조건 통과 또는 원문의 완전한 무모순을 뜻하지 않는다.',
'- **한 사실 확인:** 하나의 원자적 행동 결정을 확인하면 남은 명세를 추론할 수 있다고 추정한다.',
'- **두 사실 확인:** 답변 하나 뒤에도 독립적으로 테스트 결과를 바꾸는 결정이 남는다.',
'- **평가·답변 근거 미확정:** 테스트와 정상 과업이 어긋나거나, 필요한 선택을 가상 사용자의 참조 자료에서 식별할 수 없어 유효한 질문 경로를 확정하지 못했다. 무한 질문 필요 또는 수학적 불가능으로 해석하면 안 된다.','',
'이 추정은 추론 정책에 조건부다. 예를 들어 MD5 digest 문자열이라는 계약을 확인하면 표준 digest의 순서도 따라온다고 보아 정렬을 별도 질문으로 세지 않았다. 정수 1과 bool True를 ==로 비교해 같은 결과가 되는 실제 oracle도 반영했다. 이전처럼 텍스트상 충돌을 독립 결정으로 그대로 세는 기준과 다르다.','',
'## 분포와 기존 코드 통과','',
'| 분류 | 문제 수 | PBT4 통과 | Direct 통과 |','|---|---:|---:|---:|']
for g in summary['groups']:
 lines.append(f"| {g['label']} | {g['n']} | {g['pbt4_pass']}/{g['n']} ({100*g['pbt4_pass']/g['n']:.1f}%) | {g['direct_pass']}/{g['n']} ({100*g['direct_pass']/g['n']:.1f}%) |")
lines+=['',
'0~1 사실 그룹은 90건이며 PBT4 48/90, Direct 44/90이다. 이를 전체 점수 대신 제시하지 않는다. 원래 전체 100건의 결과와 분류별 결과를 함께 유지한다. 선택된 문제의 난이도와 판정 기준이 달라 분류별 통과율은 인과 효과가 아니다.','',
'## 두 사실이 남는 4건','',
'| 문제 | 사실 1 | 사실 2 |','|---|---|---|']
for r in rows:
 if r['more_than_one_fact']:
  lines.append(f"| {r['task_id']} | {r['questions'][0]['question']} → {r['questions'][0]['expected_answer']} | {r['questions'][1]['question']} → {r['questions'][1]['expected_answer']} |")
lines+=['','## 평가·답변 근거 미확정 6건','']
for r in rows:
 if r['route_unestablished']:lines.append(f"- **{r['task_id']}**: {r['reason']}")
lines+=['','## 전체 100건','',
'| 문제 | 테스트 기준 표시 | PBT4 | 테스트 출처 |','|---|---|---|---|']
for r in rows:lines.append(f"| [{r['task_id']}](#{r['task_id'].lower().replace('/','-')}) | {r['category_label']} | {'통과' if r['pbt4_pass'] else '실패'} | {r['test_source']['authority']} |")
for r in rows:
 lines+=['',f"## {r['task_id']}",'',f"**{r['category_label']}** · 확신 {r['confidence']} · [기존 PBT4 결과]({TRAIN}/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:{r['source_line']})",'',r['reason'],'','테스트 근거:']
 lines += [f'- {x}' for x in r['test_evidence']]
 if r['questions']:
  lines+=['','확인할 사실:']+[f"- {q['question']} → **{q['expected_answer']}** (참조 근거: {q['support']})" for q in r['questions']]
 if r['inferred_without_question']:lines+=['','추론한 부분:']+[f'- {x}' for x in r['inferred_without_question']]
 if r['remaining_gaps']:lines+=['','남은 근거 부족:']+[f'- {x}' for x in r['remaining_gaps']]
 lines+=['','<details><summary>실제 기본 테스트·assert 원문</summary>','','```python',r['test_source']['test_text'].strip(),'```','','</details>']
lines+=['','## 파일','',f'- [100건 라벨]({HERE}/labels.jsonl)',f'- [검증 집계]({HERE}/verification-summary.json)',f'- [실제 테스트·참조 실행 근거]({HERE}/test-evidence.json)',f'- [집계]({HERE}/summary.json)',f'- [출처 해시]({HERE}/provenance.json)']
(HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
# Clearly supersede the older report; keep its analysis as historical context.
oldreport=TRAIN/'question-budget-audit-20261101/REPORT.md'
text=oldreport.read_text();banner=f'> **2026-11-02 갱신:** 전체 100건을 테스트 기준으로 재마킹했다. [최신 전체 보고서]({HERE}/REPORT.md)를 기준으로 읽는다. 아래 집계는 이전 프롬프트 기준이며, 기존 labels.jsonl에도 100건 모두 최신 test_grounded 필드를 연결했다.\n\n'
if banner not in text:oldreport.write_text(banner+text)
assert len(rows)==100 and sum(g['n'] for g in summary['groups'])==100
assert summary['overall_pbt4']['pass']==48 and summary['overall_direct']['pass']==44
assert len([r for r in old if r['test_grounded_review_status']=='reviewed'])==100
print(json.dumps({k:summary[k] for k in ['population','reviewed','groups','source_distribution','overall_pbt4']},ensure_ascii=False,indent=2))

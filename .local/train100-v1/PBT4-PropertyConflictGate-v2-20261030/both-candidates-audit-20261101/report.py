import json,collections,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows=[json.loads(s) for s in (OUT/'audit.jsonl').read_text().splitlines()]
S=json.loads((OUT/'summary.json').read_text());P=json.loads((OUT/'provenance.json').read_text())
SRC={'direct':'Simple judge','property_pair':'Property'}
V={'valid':'유효','partial':'부분 유효','invalid':'부적절·불필요'}
A={'full':'명시 답변 반영','partial':'부분 반영·미확정','not_followed':'미반영','unassessable':'판단 불가'}
R={'resolved':'질문한 사실 해소','partial':'부분 해소','not_resolved':'해소 안 됨'}
F={'pass':'통과','answer_oracle_mismatch':'답변·평가 불일치','public_spec_oracle_mismatch':'공개 지시·평가 불일치','implementation_error':'알고리즘·구현 오류','unresolved_spec':'다른 명세 미해결','interface_mismatch':'호출 인터페이스 불일치','evaluation_interface_mismatch':'공개 함수명·평가 호출 불일치','answer_not_followed':'답변 미반영'}
def pct(n,d):return f'{n}/{d} ({n/d*100:.1f}%)'
def link(r):return f"[결과 {r['source_line']}행]({P['results_path']}:{r['source_line']})"
def safe(s):return str(s).replace('|','\\|').replace('\n',' ')
lines=['# PBT4: 양쪽 후보가 있는 51문제의 질문·답변·코드 감사','',
'분석일: 2026-11-01 KST. 대상은 train100-v1의 PBT4-PropertyConflictGate-v2-20261030 단일 실행이다.','',
'## 범위와 판정 기준','',
'- Simple judge와 Property pair 양쪽에 후보가 남아 최종 선택기에 전달된 51문제를 모두 검토했다. 후보 존재는 형식 검증 이후의 선택 프롬프트에서 읽었다. Rich 로그를 원문과 다시 대조하며 후보를 재검증하면 줄바꿈·공백 차이로 잘못 탈락할 수 있어 그 방법은 사용하지 않았다.',
'- 질문 유효성은 공개 문제·선택 질문·답변을 읽고, 실제 미해결 행동 결정인지, 원문에서 이미 추론되는지, 잘못된 전제나 범위 확장인지, 독립된 사실을 여러 개 묶는지 검토한 수동 판단이다. 독립적인 정답 라벨이나 다수 평가자의 합의는 아니다.',
'- 유효: 원문만으로 확정할 수 없는 구체적이고 관련 있는 행동 결정 하나. 부분 유효: 관련 충돌은 있지만 선택지 왜곡·복수 결정 결합 등이 있음. 부적절·불필요: 이미 주어진 사실 재확인, 가짜 충돌, 범위 밖 요구, 알고리즘 자체 요청.',
'- 답변 해소 여부는 질문한 사실만 본다. 과제의 전체 명세 해소와 다르다.',
'- 코드 반영은 질문에서 실제 받은 명시적 사실의 실행 코드 반영을 정적으로 검토했다. 주석만의 반영은 인정하지 않았다. 다른 알고리즘 오류·반환 계약·성능 요구를 모두 만족한다는 의미가 아니다. 불명확하거나 실질 답변이 없는 경우 판단 불가로 구분했다.',
'- 성공은 저장된 최종 테스트 결과의 success=True이다. 실패 주분류는 관찰된 대표 문제이며 유일한 인과 원인을 증명하지 않는다. 별도 결함·남은 명세는 사례별로 적었다.',
'- 원본 결과·프롬프트·가상 사용자 답변·생성 코드·채점 로그·탐지 후보를 사용했다. 숨은 참조 명세를 판정에 공급하지 않았고 새 API 호출·코드 생성·테스트 재실행은 하지 않았다. 함수명 불일치 확인에는 공개 entry_point 필드만 추가로 확인했다.','',
'## 출처별 결과','',
'| 지표 | Simple judge 선택 | Property 선택 |','|---|---:|---:|']
for label,fn in [
('선택 비중',lambda x:pct(x['n'],51)),
('최종 통과율',lambda x:pct(x['pass'],x['n'])),
('가상 사용자 QUALITY=3',lambda x:pct(x['quality'].get('3',0),x['n'])),
('재검토: 유효한 질문',lambda x:pct(x['question_validity'].get('valid',0),x['n'])),
('재검토: 부분 유효 질문',lambda x:pct(x['question_validity'].get('partial',0),x['n'])),
('재검토: 부적절·불필요 질문',lambda x:pct(x['question_validity'].get('invalid',0),x['n'])),
('질문한 사실의 답변 해소',lambda x:pct(x['answer_resolution'].get('resolved',0),x['n'])),
('명시 답변을 코드에 반영',lambda x:pct(x['code_adherence'].get('full',0),x['n'])),
('부분 반영·미확정',lambda x:pct(x['code_adherence'].get('partial',0),x['n'])),
('답변 미반영',lambda x:pct(x['code_adherence'].get('not_followed',0),x['n'])),
('코드 반영 판단 불가',lambda x:pct(x['code_adherence'].get('unassessable',0),x['n'])),
('유효 질문에서 최종 통과',lambda x:pct(x['valid_questions']['pass'],x['valid_questions']['n'])),
('유효 질문에서 답변 반영',lambda x:pct(x['valid_questions']['full_adherence'],x['valid_questions']['n']))]:
 lines.append(f"| {label} | {fn(S['direct'])} | {fn(S['property_pair'])} |")
lines+=['',
'두 선택 출처의 통과율 차이는 2.9%p다. 서로 다른 문제에 선택했고 선택도 무작위가 아니므로 이 차이를 Property의 우월성으로 해석할 수 없다. 유효 질문으로 제한하면 Simple judge 8/25=32.0%, Property 4/13=30.8%다. 이 조건부 비교도 인과 효과는 아니다.','',
'QUALITY=3은 49/51인데 재검토에서 유효는 38/51이다. 부적절 질문 뒤에도 통과한 사례가 있어 통과와 질문 유효성을 동일시하면 안 된다.','',
'## 실패 34건의 주분류','',
'| 주분류 | Simple judge 실패 23건 | Property 실패 11건 | 합계 |','|---|---:|---:|---:|']
for keys,title in [(['answer_oracle_mismatch'],'답변·평가 불일치'),(['public_spec_oracle_mismatch'],'공개 지시·평가 불일치'),(['implementation_error'],'알고리즘·구현 오류'),(['unresolved_spec'],'다른 명세 미해결'),(['interface_mismatch','evaluation_interface_mismatch'],'호출 인터페이스 불일치'),(['answer_not_followed'],'답변 미반영')]:
 a=sum(S['direct']['failure_category'].get(k,0) for k in keys);b=sum(S['property_pair']['failure_category'].get(k,0) for k in keys)
 lines.append(f'| {title} | {a} | {b} | {a+b} |')
lines+=['',
'답변과 평가의 직접 불일치 9건과 공개 지시와 평가 불일치 5건은 분리했다. 전자는 질문에 받은 답과 평가 기대값의 직접 충돌, 후자는 질문한 사실 외의 공개 지시와 평가 기대값의 충돌이다. 둘을 질문 후 코드 미반영으로 집계하지 않았다. 호출 불일치 6건 중 Mbpp/770은 공개 entry_point 자체와 평가자의 호출명이 달랐고, 나머지 5건은 제공된 함수명은 맞지만 평가 호출 인자 수와 코드가 맞지 않았다. 후자의 책임 소재는 공개 함수 시그니처가 충분하지 않아 여기서 단정하지 않는다.','',
'명시 답변 반영 42건 중 통과는 15건, 실패는 27건이다. 부분 반영·미확정 4건 중 1건, 판단 불가 3건 중 1건도 통과했다. 따라서 통과했다고 답변 반영·명세 해소가 입증되는 것도 아니고, 답변을 반영했다고 전체 테스트 통과가 보장되는 것도 아니다.','',
'## 어떤 질문을 골랐는가','',
'51건 중 19건은 선택하지 않은 출처에도 같은 핵심 결정을 묻는 후보가 있었다. source=direct/property_pair는 후보 출처이지 항상 다른 질문 내용이라는 뜻이 아니다. 최종 선택기는 후보 질문을 다시 써서 실제 질문과 원래 후보 문구가 다를 수도 있다. 아래 사례에는 실제 질문과 양쪽 후보를 모두 보존했다.','',
'선택하지 않은 질문을 실제로 물어 다시 코드를 생성하지 않았으므로 그 질문의 성공률은 계산할 수 없다. 더 직접적인 질문으로 보인다는 평가는 후보 내용에 대한 정성 판단이며 대안 실행의 통과율이 아니다.','',
'## 51문제 전체 색인','',
'| 문제 | 선택 | 질문 유효성 | 답변 해소 | 코드 반영 | 테스트 | 주분류 |','|---|---|---|---|---|---|---|']
for r in rows:
 a=r['audit'];task=r['task_id'];anchor=task.lower().replace('/','-')
 lines.append(f"| [{task}](#{anchor}) | {SRC[r['selected_source']]} | {V[a['question_validity']]} | {R[a['answer_resolution']]} | {A[a['code_adherence']]} | {'통과' if r['success'] else '실패'} | {F[a['failure_category']]} |")
for r in rows:
 a=r['audit'];task=r['task_id'];q,req,quality,ans=r['clarification_history'][0]
 lines+=['',f'## {task}','',f"선택: **{SRC[r['selected_source']]}** · 테스트: **{'통과' if r['success'] else '실패'}** · 기록 QUALITY={quality} · {link(r)}",'',
'### 실제 질문과 답변','',f'> {q}','',f'> 답변: {ans}','',
'### 재검토','',
f"- 질문: **{V[a['question_validity']]}** — {a['question_reason']}",
f"- 답변 해소: **{R[a['answer_resolution']]}**.",
f"- 코드: **{A[a['code_adherence']]}** — {a['code_reason']}",
f"- 결과 해석: **{F[a['failure_category']]}** — {a['failure_reason']}",
f"- 다른 후보와 비교: {a['alternative_reason']}",'',
'### 양쪽 탐지 후보','',f"- Simple judge: {r['direct_candidate']['question']}"]
 for i,c in enumerate(r['property_candidates']):lines.append(f"- Property {i} (ID {c['property_a']}·{c['property_b']}, {c['kind']}): {c['question']}")
 lines+=['','<details><summary>공개 문제·생성 코드·채점 로그</summary>','', '공개 문제:', '', '```text',r['prompt'].strip(),'```','', '생성 코드:', '', '```python',r['prompt_result'].strip(),'```','', '채점 로그:', '', '```text',r['test_result'].replace('```','').strip(),'```','', '</details>']
lines+=['','## 파일과 재현','',
f"- [원본 결과]({P['results_path']}) · SHA-256 `{P['results_sha256']}`",
f'- [후보·원문·코드 전체 추출]({OUT}/cases.json)',
f'- [사례별 판정 JSONL]({OUT}/audit.jsonl)',
f'- [집계 JSON]({OUT}/summary.json)',
f'- [후보 추출 스크립트]({OUT}/extract.py)',
f'- [수동 판정과 집계 스크립트]({OUT}/review.py)',
f'- [보고서 생성 스크립트]({OUT}/report.py)','',
'원본 결과·로그를 유지한 채 extract.py → review.py → report.py를 실행하면 같은 판정 집계를 재생성한다. 질문 유효성·답변 반영의 정성 판정을 새로 독립 평가하는 절차는 아니다.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
assert len(rows)==51 and sum(r['success'] for r in rows)==17
assert hashlib.sha256(Path(P['results_path']).read_bytes()).hexdigest()==P['results_sha256']
assert len([r for r in rows if r['audit']['code_adherence']=='full'])==42
assert len([r for r in rows if r['audit']['code_adherence']=='full' and r['success']])==15
print('Report:',OUT/'REPORT.md')
print('51 cases, 17 passes; both source totals and source result hash verified.')

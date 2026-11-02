import json,collections,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows=[json.loads(s) for s in (OUT/'labels.jsonl').read_text().splitlines()]
summary=json.loads((OUT/'summary.json').read_text());prov=json.loads((OUT/'provenance.json').read_text())
F='multiple_functional_decisions';L='functional_plus_resource_constraint';C='conditional_or_uncertain';N='no_multiple_decision_evidence'
LABEL={F:'기능상 독립 결정 복수',L:'기능 결정 + 실행 제약',C:'조건부·판단 보류',N:'복수 질문 근거 미확인'}
E={'none_recorded':'별도 불일치 태그 없음','answer_test_conflict':'답변·채점 충돌','public_spec_test_conflict':'공개 지시·채점 충돌','provided_entrypoint_test_name_mismatch':'공개 함수명·평가 호출명 불일치','call_arity_mismatch':'호출 인자 수 불일치'}
def pct(n,d):return f'{n}/{d} ({n/d*100:.1f}%)'
def result_link(r):return f"[문제·Direct 결과]({prov['source_results']}:{r['source_line']})"
def pbt_link(r):return f"[PBT4 결과]({prov['pbt4_results']}:{r['source_line']})"
lines=['# 단일 질문 예산 위험: train100-v1의 100문제 마킹','',
'분석일: 2026-11-01 KST. 한 메시지에 독립적인 구현 사실 하나만 확인할 수 있다는 가정으로 공개 프롬프트를 재검토했다.','',
'## 라벨의 의미','',
'이 마킹은 문제의 최소 질문 횟수를 수학적으로 증명한 정답 라벨이 아니다. 프롬프트에서 독립적으로 남는 행동 결정과 실행 계약을 식별한 수동 진단이다. 검토자는 이전 실행 결과를 이미 보았으므로 완전한 블라인드 평가는 아니다. 다만 실패했다는 이유, 여러 알고리즘이 실패했다는 이유, 평가자만 아는 기대값을 기준으로 필요한 질문 수를 역산하지 않았다.','',
'- **기능상 독립 결정 복수:** 입출력 동작에 영향을 주는 서로 다른 결정이 둘 이상 남는다. `functional_only_budget_risk=true`로 표시한다.',
'- **기능 결정 + 실행 제약:** 입출력 결정 외 자원 제한·입력 상한·허용 연산의 해석을 별도로 정해야 한다. 비용 모델과 문자 그대로의 제약을 따를 때의 위험이다. 이를 곧바로 입출력 채점 불가능 또는 엄밀한 불가능성 증명으로 읽으면 안 된다.',
'- **조건부·판단 보류:** 두 결정처럼 보이나 하나의 답이 다른 결정을 비관찰적으로 만들거나, 포괄 지원·합리적인 관례로 흡수할 수 있다. 자동 제외 대상으로 사용하지 않는다.',
'- **복수 질문 근거 미확인:** 0~1개의 확인으로 충분할 여지가 있거나 공개 프롬프트에서 2개가 꼭 필요하다는 근거를 확인하지 못했다. 한 질문으로 반드시 통과한다는 라벨은 아니다.','',
'원문에 여러 지시가 있다는 사실만으로 여러 질문을 요구한다고 세지 않았다. 예를 들어 리스트 길이만 반환한다면 리스트의 정렬 방향은 출력에 영향을 주지 않는다. int와 float가 예시에서 섞여도 둘 다 처리하는 확장 구현으로 해결할 수 있다. 반면 같은 정수 입력의 수치 XOR와 숫자 모양을 이진수로 읽는 XOR는 입력 타입의 포괄 지원만으로 해결되지 않는다.','',
'## 결과 요약','',
'| 분류 | 문제 수 | Direct 통과 | PBT4 통과 |','|---|---:|---:|---:|']
for flag in (F,L,C,N):
 s=summary[flag];lines.append(f"| {LABEL[flag]} | {s['n']} | {pct(s['direct_pass'],s['n'])} | {pct(s['pbt4_pass'],s['n'])} |")
lines+=['',
'기능 동작만 보는 보수적 위험 표시는 3문제, 실행 제약까지 포함한 표시는 10문제다. 후자의 10개를 자동으로 제외한 점수를 새로운 주점수로 제시하지 않는다. 전체 100문제의 결과를 유지하고 라벨별 성능을 병기하는 개발 분석용이다. 현재 PBT4는 48/100, Direct는 44/100이며 라벨링으로 원본 점수를 바꾸지 않았다.','',
'## 먼저 표시한 3문제','',
'| 문제 | 별도로 남는 결정 |','|---|---|']
for r in rows:
 if r['budget_flag']==F:lines.append(f"| [{r['task_id']}](#{r['task_id'].lower().replace('/','-')}) | {' / '.join(a['name'] for a in r['axes'] if a['kind']=='functional')} |")
lines+=['',
'## 실행 제약까지 포함하면 추가되는 7문제','',
', '.join(summary[L]['task_ids']), '',
'예를 들어 derivative의 반환 타입을 확인해도 임의 길이 입력·출력에서 O(1)을 어떻게 지킬지 남고, 반대로 시간 제약을 완화해도 기본 반환 타입 충돌이 저절로 정해지는 것은 아니다. 실제 채점이 모든 자연어 실행 제약을 검사했는지는 저장된 통과 여부만으로 확인할 수 없다.','',
'## 보류한 14문제','',', '.join(summary[C]['task_ids']),'',
'HumanEval/18은 발생 횟수 대신 부분문자열 길이만 반환하는 계약을 고르면 O(1) 문제가 사라질 수 있어 독립 두 축으로 확정하지 않았다. HumanEval/111은 O(1) 요구가 없고 Counter/map/filter 등으로 명시적인 loop·재귀 없이 구현할 여지가 있어 반복 금지만을 필수 두 번째 질문으로 세지 않았다.','',
'## 질문 예산과 별도의 평가 관찰','',
'| 관찰한 불일치 | 문제 수 |','|---|---:|']
for key,count in summary['evaluation_observations'].items():lines.append(f'| {E[key]} | {count} |')
lines+=['',
'답변·채점 충돌 11건, 공개 지시·채점 충돌 6건을 별도 표시했다. 공개 entry_point와 평가 호출명 차이 3건, 호출 인자 수 차이 5건도 분리했다. 이는 PBT4의 저장된 실행에서 관찰한 특정 불일치이며 모든 가능한 문제·답변에서 항상 발생한다는 뜻은 아니다. 함수명 오류 3건은 공개 entry_point와 생성 함수명을 대조했다. 인자 수 문제의 책임 소재는 충분한 공개 시그니처가 없어 일괄 판정하지 않았다. 태그가 없는 75건도 평가가 완전히 건전하다는 증명은 아니다.','',
'## 전체 100문제 색인','',
'| 문제 | 질문 예산 라벨 | 별도 평가 관찰 | Direct | PBT4 |','|---|---|---|---|---|']
for r in rows:
 anchor=r['task_id'].lower().replace('/','-')
 lines.append(f"| [{r['task_id']}](#{anchor}) | {LABEL[r['budget_flag']]} | {E[r['evaluation_observation']]} | {'통과' if r['direct_pass'] else '실패'} | {'통과' if r['pbt4_pass'] else '실패'} |")
for r in rows:
 lines+=['',f"## {r['task_id']}",'',f"**{LABEL[r['budget_flag']]}** · {result_link(r)} · {pbt_link(r)}",'',r['reason']]
 for i,a in enumerate(r['axes'],1):
  lines+=['',f"### 후보 결정 {i}: {a['name']}",'',f"- 종류: {'입출력 행동' if a['kind']=='functional' else '실행·자원 계약'}",f"- 대안: {' / '.join(a['alternatives'])}",f"- 차이를 확인할 입력·효과: {a['distinguishing_input_or_effect']}",'- 원문 근거:']
  for quote in a['evidence']:lines.append('  - '+json.dumps(quote,ensure_ascii=False))
 if r['conditional_axes']:
  lines+=['','추가 의존성·보류 이유:']+[f'- {x}' for x in r['conditional_axes']]
 if r['evaluation_observation']!='none_recorded':lines+=['',f"별도 평가 관찰: **{E[r['evaluation_observation']]}** — {r['evaluation_evidence']}"]
 lines+=['','<details><summary>공개 문제 원문</summary>','','```text',r['prompt'].strip(),'```','','</details>']
lines+=['','## 파일·재현·사용','',
f'- [100문제 라벨 JSONL]({OUT}/labels.jsonl)',f'- [집계 JSON]({OUT}/summary.json)',f'- [수동 판단과 마킹 스크립트]({OUT}/mark.py)',f'- [출처와 해시]({OUT}/provenance.json)','',
'`functional_only_budget_risk`는 보수적인 기능 위험 표시, `one_atomic_question_budget_risk`는 실행 제약을 포함한 표시, `requires_manual_review`는 보류 표시다. `formal_impossibility_proven`은 모든 항목에서 false다. 같은 task_id라도 변형 프롬프트가 다르면 라벨을 재사용하면 안 되므로 prompt_sha256과 원문을 함께 기록했다.','',
'추가 모델 호출·새 코드 생성·후보 코드 재실행 없이 저장된 자료만 분석했다. 라벨 파일은 원본 데이터·제출 알고리즘과 분리해 저장했다. 학습·검증 점수를 비교할 때는 동일하고 고정된 라벨 기준을 사용하고, 성공·실패를 본 뒤 유리한 제외 기준으로 조정하지 않아야 한다.']
correction=[
 '## 2026-11-02 정정: HumanEval/149의 실제 테스트 기준', '',
 '**실제 테스트를 보면 반환이 리스트라는 점과 동점 정렬이 알파벳 오름차순이라는 점이 모두 확정된다.** 기존의 보류 표시는 프롬프트만 보고 정수 길이 반환이 가능하다고 가정한 판정이었다. 이번 사후 분석에서는 실제 평가가 요구하는 리스트 반환을 기준으로 동점 정렬도 관찰 가능한 별도 결정으로 표시해야 한다.', '',
 '```python',
 'assert candidate(["aa", "a", "aaa"]) == ["aa"]',
 'assert candidate(["d", "dcba", "abcd", "a"]) == ["abcd", "dcba"]',
 '```', '',
 '따라서 149에 `test_grounded_budget_flag=multiple_functional_decisions`, `test_grounded_fact_axes_estimate=2`를 추가했다. 가상 사용자의 역알파벳순 답변도 실제 테스트의 오름차순 요구와 충돌하므로 `evaluation_observation_secondary=answer_test_conflict`로 추가했다. 두 질문을 하면 반드시 성공한다는 의미는 아니며, 답변 자체와 테스트가 불일치하는 문제도 함께 있다.', '',
 '아래 3/7/14/76 집계는 기존 **프롬프트 기준**을 유지한 표다. 이 후속 작업에서 테스트 기준으로 직접 재검토한 것은 149 한 문제이므로 전체 100개를 테스트 기준으로 재분류했다고 주장하지 않는다. 실제 테스트를 근거로 한 마킹과 프롬프트만으로 판단한 마킹을 구분해 읽어야 한다.', '',
 f'- [149의 테스트 근거·정정 기록]({OUT}/evaluation-grounded-149.json)', ''
]
lines[4:4]=correction
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
assert sum(summary[k]['n'] for k in (F,L,C,N))==100
assert sum(summary[k]['pbt4_pass'] for k in (F,L,C,N))==48
assert sum(summary[k]['direct_pass'] for k in (F,L,C,N))==44
for file,key in [(prov['source_results'],'source_sha256'),(prov['pbt4_results'],'pbt4_sha256')]:assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==prov[key]
print(OUT/'REPORT.md')
print('Verified 100 records, 100 prompt hashes, exact evidence quotes, 44/100 and 48/100 totals, unchanged source result hashes.')

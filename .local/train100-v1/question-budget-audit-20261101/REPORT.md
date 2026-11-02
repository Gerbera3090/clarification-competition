> **2026-11-02 갱신:** 전체 100건을 테스트 기준으로 재마킹했다. [최신 전체 보고서](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/test-grounded-budget-audit-20261102/REPORT.md)를 기준으로 읽는다. 아래 집계는 이전 프롬프트 기준이며, 기존 labels.jsonl에도 100건 모두 최신 test_grounded 필드를 연결했다.

# 단일 질문 예산 위험: train100-v1의 100문제 마킹

분석일: 2026-11-01 KST. 한 메시지에 독립적인 구현 사실 하나만 확인할 수 있다는 가정으로 공개 프롬프트를 재검토했다.

## 2026-11-02 정정: HumanEval/149의 실제 테스트 기준

**실제 테스트를 보면 반환이 리스트라는 점과 동점 정렬이 알파벳 오름차순이라는 점이 모두 확정된다.** 기존의 보류 표시는 프롬프트만 보고 정수 길이 반환이 가능하다고 가정한 판정이었다. 이번 사후 분석에서는 실제 평가가 요구하는 리스트 반환을 기준으로 동점 정렬도 관찰 가능한 별도 결정으로 표시해야 한다.

```python
assert candidate(["aa", "a", "aaa"]) == ["aa"]
assert candidate(["d", "dcba", "abcd", "a"]) == ["abcd", "dcba"]
```

따라서 149에 `test_grounded_budget_flag=multiple_functional_decisions`, `test_grounded_fact_axes_estimate=2`를 추가했다. 가상 사용자의 역알파벳순 답변도 실제 테스트의 오름차순 요구와 충돌하므로 `evaluation_observation_secondary=answer_test_conflict`로 추가했다. 두 질문을 하면 반드시 성공한다는 의미는 아니며, 답변 자체와 테스트가 불일치하는 문제도 함께 있다.

아래 3/7/14/76 집계는 기존 **프롬프트 기준**을 유지한 표다. 이 후속 작업에서 테스트 기준으로 직접 재검토한 것은 149 한 문제이므로 전체 100개를 테스트 기준으로 재분류했다고 주장하지 않는다. 실제 테스트를 근거로 한 마킹과 프롬프트만으로 판단한 마킹을 구분해 읽어야 한다.

- [149의 테스트 근거·정정 기록](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/question-budget-audit-20261101/evaluation-grounded-149.json)

## 라벨의 의미

이 마킹은 문제의 최소 질문 횟수를 수학적으로 증명한 정답 라벨이 아니다. 프롬프트에서 독립적으로 남는 행동 결정과 실행 계약을 식별한 수동 진단이다. 검토자는 이전 실행 결과를 이미 보았으므로 완전한 블라인드 평가는 아니다. 다만 실패했다는 이유, 여러 알고리즘이 실패했다는 이유, 평가자만 아는 기대값을 기준으로 필요한 질문 수를 역산하지 않았다.

- **기능상 독립 결정 복수:** 입출력 동작에 영향을 주는 서로 다른 결정이 둘 이상 남는다. `functional_only_budget_risk=true`로 표시한다.
- **기능 결정 + 실행 제약:** 입출력 결정 외 자원 제한·입력 상한·허용 연산의 해석을 별도로 정해야 한다. 비용 모델과 문자 그대로의 제약을 따를 때의 위험이다. 이를 곧바로 입출력 채점 불가능 또는 엄밀한 불가능성 증명으로 읽으면 안 된다.
- **조건부·판단 보류:** 두 결정처럼 보이나 하나의 답이 다른 결정을 비관찰적으로 만들거나, 포괄 지원·합리적인 관례로 흡수할 수 있다. 자동 제외 대상으로 사용하지 않는다.
- **복수 질문 근거 미확인:** 0~1개의 확인으로 충분할 여지가 있거나 공개 프롬프트에서 2개가 꼭 필요하다는 근거를 확인하지 못했다. 한 질문으로 반드시 통과한다는 라벨은 아니다.

원문에 여러 지시가 있다는 사실만으로 여러 질문을 요구한다고 세지 않았다. 예를 들어 리스트 길이만 반환한다면 리스트의 정렬 방향은 출력에 영향을 주지 않는다. int와 float가 예시에서 섞여도 둘 다 처리하는 확장 구현으로 해결할 수 있다. 반면 같은 정수 입력의 수치 XOR와 숫자 모양을 이진수로 읽는 XOR는 입력 타입의 포괄 지원만으로 해결되지 않는다.

## 결과 요약

| 분류 | 문제 수 | Direct 통과 | PBT4 통과 |
|---|---:|---:|---:|
| 기능상 독립 결정 복수 | 3 | 1/3 (33.3%) | 0/3 (0.0%) |
| 기능 결정 + 실행 제약 | 7 | 0/7 (0.0%) | 0/7 (0.0%) |
| 조건부·판단 보류 | 14 | 1/14 (7.1%) | 3/14 (21.4%) |
| 복수 질문 근거 미확인 | 76 | 42/76 (55.3%) | 45/76 (59.2%) |

기능 동작만 보는 보수적 위험 표시는 3문제, 실행 제약까지 포함한 표시는 10문제다. 후자의 10개를 자동으로 제외한 점수를 새로운 주점수로 제시하지 않는다. 전체 100문제의 결과를 유지하고 라벨별 성능을 병기하는 개발 분석용이다. 현재 PBT4는 48/100, Direct는 44/100이며 라벨링으로 원본 점수를 바꾸지 않았다.

## 먼저 표시한 3문제

| 문제 | 별도로 남는 결정 |
|---|---|
| [HumanEval/162](#humaneval-162) | 해시 출력 타입 / 해시 순서 보존 |
| [HumanEval/137](#humaneval-137) | 입력 타입 허용 / 더 큰 값의 반환 타입 |
| [HumanEval/11](#humaneval-11) | 입력 숫자의 표현 / 반환 타입 |

## 실행 제약까지 포함하면 추가되는 7문제

HumanEval/62, HumanEval/55, HumanEval/105, HumanEval/59, HumanEval/47, HumanEval/127, HumanEval/54

예를 들어 derivative의 반환 타입을 확인해도 임의 길이 입력·출력에서 O(1)을 어떻게 지킬지 남고, 반대로 시간 제약을 완화해도 기본 반환 타입 충돌이 저절로 정해지는 것은 아니다. 실제 채점이 모든 자연어 실행 제약을 검사했는지는 저장된 통과 여부만으로 확인할 수 없다.

## 보류한 14문제

HumanEval/75, HumanEval/156, HumanEval/116, HumanEval/149, HumanEval/111, HumanEval/7, HumanEval/95, HumanEval/18, HumanEval/84, HumanEval/0, Mbpp/144, Mbpp/698, Mbpp/378, Mbpp/753

HumanEval/18은 발생 횟수 대신 부분문자열 길이만 반환하는 계약을 고르면 O(1) 문제가 사라질 수 있어 독립 두 축으로 확정하지 않았다. HumanEval/111은 O(1) 요구가 없고 Counter/map/filter 등으로 명시적인 loop·재귀 없이 구현할 여지가 있어 반복 금지만을 필수 두 번째 질문으로 세지 않았다.

## 질문 예산과 별도의 평가 관찰

| 관찰한 불일치 | 문제 수 |
|---|---:|
| 별도 불일치 태그 없음 | 75 |
| 답변·채점 충돌 | 11 |
| 공개 지시·채점 충돌 | 6 |
| 공개 함수명·평가 호출명 불일치 | 3 |
| 호출 인자 수 불일치 | 5 |

답변·채점 충돌 11건, 공개 지시·채점 충돌 6건을 별도 표시했다. 공개 entry_point와 평가 호출명 차이 3건, 호출 인자 수 차이 5건도 분리했다. 이는 PBT4의 저장된 실행에서 관찰한 특정 불일치이며 모든 가능한 문제·답변에서 항상 발생한다는 뜻은 아니다. 함수명 오류 3건은 공개 entry_point와 생성 함수명을 대조했다. 인자 수 문제의 책임 소재는 충분한 공개 시그니처가 없어 일괄 판정하지 않았다. 태그가 없는 75건도 평가가 완전히 건전하다는 증명은 아니다.

## 전체 100문제 색인

| 문제 | 질문 예산 라벨 | 별도 평가 관찰 | Direct | PBT4 |
|---|---|---|---|---|
| [HumanEval/107](#humaneval-107) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/87](#humaneval-87) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/33](#humaneval-33) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/62](#humaneval-62) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/75](#humaneval-75) | 조건부·판단 보류 | 답변·채점 충돌 | 실패 | 실패 |
| [HumanEval/55](#humaneval-55) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/156](#humaneval-156) | 조건부·판단 보류 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/43](#humaneval-43) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/90](#humaneval-90) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/116](#humaneval-116) | 조건부·판단 보류 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [HumanEval/21](#humaneval-21) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/100](#humaneval-100) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/143](#humaneval-143) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/106](#humaneval-106) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/149](#humaneval-149) | 조건부·판단 보류 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/42](#humaneval-42) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/111](#humaneval-111) | 조건부·판단 보류 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/105](#humaneval-105) | 기능 결정 + 실행 제약 | 답변·채점 충돌 | 실패 | 실패 |
| [HumanEval/162](#humaneval-162) | 기능상 독립 결정 복수 | 답변·채점 충돌 | 실패 | 실패 |
| [HumanEval/119](#humaneval-119) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/123](#humaneval-123) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/59](#humaneval-59) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/47](#humaneval-47) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/88](#humaneval-88) | 복수 질문 근거 미확인 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/14](#humaneval-14) | 복수 질문 근거 미확인 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/127](#humaneval-127) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/137](#humaneval-137) | 기능상 독립 결정 복수 | 별도 불일치 태그 없음 | 통과 | 실패 |
| [HumanEval/144](#humaneval-144) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/89](#humaneval-89) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/13](#humaneval-13) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/93](#humaneval-93) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/136](#humaneval-136) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/52](#humaneval-52) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/7](#humaneval-7) | 조건부·판단 보류 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/24](#humaneval-24) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/31](#humaneval-31) | 복수 질문 근거 미확인 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/28](#humaneval-28) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [HumanEval/44](#humaneval-44) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/140](#humaneval-140) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/95](#humaneval-95) | 조건부·판단 보류 | 답변·채점 충돌 | 실패 | 실패 |
| [HumanEval/157](#humaneval-157) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/99](#humaneval-99) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/153](#humaneval-153) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/18](#humaneval-18) | 조건부·판단 보류 | 답변·채점 충돌 | 실패 | 실패 |
| [HumanEval/84](#humaneval-84) | 조건부·판단 보류 | 공개 지시·채점 충돌 | 실패 | 실패 |
| [HumanEval/154](#humaneval-154) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [HumanEval/54](#humaneval-54) | 기능 결정 + 실행 제약 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/0](#humaneval-0) | 조건부·판단 보류 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [HumanEval/11](#humaneval-11) | 기능상 독립 결정 복수 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [HumanEval/67](#humaneval-67) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/770](#mbpp-770) | 복수 질문 근거 미확인 | 공개 함수명·평가 호출명 불일치 | 실패 | 실패 |
| [Mbpp/268](#mbpp-268) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/38](#mbpp-38) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/306](#mbpp-306) | 복수 질문 근거 미확인 | 호출 인자 수 불일치 | 실패 | 실패 |
| [Mbpp/232](#mbpp-232) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/641](#mbpp-641) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/762](#mbpp-762) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/382](#mbpp-382) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 실패 |
| [Mbpp/135](#mbpp-135) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 실패 |
| [Mbpp/589](#mbpp-589) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/183](#mbpp-183) | 복수 질문 근거 미확인 | 호출 인자 수 불일치 | 실패 | 실패 |
| [Mbpp/736](#mbpp-736) | 복수 질문 근거 미확인 | 답변·채점 충돌 | 실패 | 실패 |
| [Mbpp/577](#mbpp-577) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/645](#mbpp-645) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [Mbpp/144](#mbpp-144) | 조건부·판단 보류 | 호출 인자 수 불일치 | 실패 | 실패 |
| [Mbpp/772](#mbpp-772) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/423](#mbpp-423) | 복수 질문 근거 미확인 | 호출 인자 수 불일치 | 실패 | 실패 |
| [Mbpp/600](#mbpp-600) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/958](#mbpp-958) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/328](#mbpp-328) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/84](#mbpp-84) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 실패 |
| [Mbpp/698](#mbpp-698) | 조건부·판단 보류 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/628](#mbpp-628) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/461](#mbpp-461) | 복수 질문 근거 미확인 | 답변·채점 충돌 | 실패 | 실패 |
| [Mbpp/378](#mbpp-378) | 조건부·판단 보류 | 답변·채점 충돌 | 실패 | 실패 |
| [Mbpp/941](#mbpp-941) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/199](#mbpp-199) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [Mbpp/18](#mbpp-18) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/611](#mbpp-611) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/414](#mbpp-414) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/308](#mbpp-308) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/409](#mbpp-409) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/753](#mbpp-753) | 조건부·판단 보류 | 답변·채점 충돌 | 실패 | 실패 |
| [Mbpp/311](#mbpp-311) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/361](#mbpp-361) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [Mbpp/627](#mbpp-627) | 복수 질문 근거 미확인 | 호출 인자 수 불일치 | 실패 | 실패 |
| [Mbpp/253](#mbpp-253) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/723](#mbpp-723) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [Mbpp/763](#mbpp-763) | 복수 질문 근거 미확인 | 공개 함수명·평가 호출명 불일치 | 실패 | 실패 |
| [Mbpp/227](#mbpp-227) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/7](#mbpp-7) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/222](#mbpp-222) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/70](#mbpp-70) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/165](#mbpp-165) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/247](#mbpp-247) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 실패 |
| [Mbpp/874](#mbpp-874) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 실패 | 통과 |
| [Mbpp/166](#mbpp-166) | 복수 질문 근거 미확인 | 공개 함수명·평가 호출명 불일치 | 실패 | 실패 |
| [Mbpp/90](#mbpp-90) | 복수 질문 근거 미확인 | 별도 불일치 태그 없음 | 통과 | 통과 |
| [Mbpp/936](#mbpp-936) | 복수 질문 근거 미확인 | 답변·채점 충돌 | 실패 | 실패 |
| [Mbpp/373](#mbpp-373) | 복수 질문 근거 미확인 | 답변·채점 충돌 | 실패 | 실패 |

## HumanEval/107

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:1) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:1)

range(1,n)과 inclusive 사이 끝점 해석은 한 축이다. 회문 예시의 개수와 목록 자체는 일관된다.

<details><summary>공개 문제 원문</summary>

```text
def even_odd_palindrome(n):
    """
    Given a positive integer n, return a tuple that has the number of even and odd
    integer palindromes that fall within the range(1, n), inclusive.

    Example 1:

        Input: 3
        Output: (1, 2)
        Explanation:
        Integer palindrome are 1, 2, 3. one of them is even, and two of them are odd.

    Example 2:

        Input: 12
        Output: (4, 6)
        Explanation:
        Integer palindrome are 1, 2, 3, 4, 5, 6, 7, 8, 9, 11. four of them are even, and 6 of them are odd.

    Note:
        1. 1 <= n <= 10^3
        2. returned tuple has the number of even and odd integer palindromes respectively.
    """
```

</details>

## HumanEval/87

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:2) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:2)

행 오름차순·같은 행 열 내림차순이 명시되며 예시도 이를 따른다.

<details><summary>공개 문제 원문</summary>

```text
def get_row(lst, x):
    """
    You are given a 2 dimensional data, as a nested lists,
    which is similar to matrix, however, unlike matrices,
    each row may contain a different number of columns.
    Given lst, and integer x, find integers x in the list,
    and return list of tuples, [(x1, y1), (x2, y2) ...] such that
    each tuple is a coordinate - (row, columns), starting with 0.
    Sort coordinates initially by rows in ascending order.
    Also, sort coordinates of the row by columns in descending order.
    
    Examples:
    get_row([
      [1,2,3,4,5,6],
      [1,2,3,4,1,6],
      [1,2,3,4,5,1]
    ], 1) == [(0, 0), (1, 4), (1, 0), (2, 5), (2, 0)]
    get_row([], 1) == []
    get_row([[], [1], [1, 2, 3]], 3) == [(2, 2)]
    """
```

</details>

## HumanEval/33

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:3) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:3)

반환 타입·ascending 모드의 계약 충돌은 있으나 별도의 필수 사실 2개라는 근거는 약하다. 반복 금지는 재귀 등과 곧바로 모순되지 않는다.

<details><summary>공개 문제 원문</summary>

```text
def sort_third(l: list, ascending: bool = True):
    """This function takes a list l and a boolean ascending and returns an integer. If ascending is True, it returns a 
    list l' such that l' is identical to l in the indicies that are not divisible by three, while its values at the indicies 
    that are divisible by three are equal to the values of the corresponding indicies of l, but sorted in ascending order. If 
    ascending is False, it returns the sum of all elements in the list. The implementation should not use any loops.

    >>> sort_third([1, 2, 3])
    1
    >>> sort_third([5, 6, 3, 4, 8, 9, 2])
    10
    >>> sort_third([1, 2, 3], False)
    6
    """
    return 0
```

</details>

## HumanEval/62

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:4) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:4)

출력 정책을 확정해도 임의 길이 계수에서 미분 결과를 만드는 비용과 O(1) 조건은 남는다.

### 후보 결정 1: 출력 타입과 기본 반환 정책

- 종류: 입출력 행동
- 대안: 기본 리스트·선택적 문자열 / 문자열 또는 정수 우선
- 차이를 확인할 입력·효과: 동일 기본 호출에서 list/str/int가 달라진다.
- 원문 근거:
  - "The output should be a string. However, the function is also expected to return an integer."
  - "format: str = 'string'"
  - "[1, 4, 12, 20]"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "time complexity should be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def derivative(xs: list, format: str = 'string'):
    """ xs represent coefficients of a polynomial.
    xs[0] + xs[1] * x + xs[2] * x^2 + ....
    Return derivative of this polynomial in the same form and ensure that the original ordering of the elements in the list is maintained. 
    The output should be a string. However, the function is also expected to return an integer.
    This function should work without using any loops and the time complexity should be O(1).
    
    >>> derivative([3, 1, 2, 4, 5])
    [1, 4, 12, 20]
    >>> derivative([1, 2, 3])
    [2, 6]
    >>> derivative([1, 2, 3], format='string')
    '2, 6'
    """
```

</details>

## HumanEval/75

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:5) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:5)

반환 구조 외 비수치 입력의 정확한 의미도 불명확하지만 False·빈 목록 등 자연스러운 해석으로 함께 정해질 수 있어 필수 2질문으로 확정하지 않았다.

### 후보 결정 1: 반환 구조

- 종류: 입출력 행동
- 대안: bool만 / bool과 소수 목록
- 차이를 확인할 입력·효과: 반환 객체가 달라진다.
- 원문 근거:
  - "returns true"
  - "return the list of these 3 prime numbers"

추가 의존성·보류 이유:
- 숫자 문자열의 변환, 일반 비수치 입력의 허용·오류 정책.
- a<100이 명시되어 있어 O(1) 자체는 무제한 입력 문제와 다르게 취급했다.

별도 평가 관찰: **답변·채점 충돌** — 입력 5에서 평가자는 False를 기대하지만 답변을 따른 코드는 (False,[])를 반환한다. 목록 생성의 전체 정확성은 이 판정과 별개다.

<details><summary>공개 문제 원문</summary>

```text
def is_multiply_prime(a):
    """Write a function that returns true if the given number is the multiplication of 3 prime numbers
    and false otherwise.
    And also, this function should return the list of these 3 prime numbers. 
    Knowing that (a) is less than 100. 
    Moreover, the function should not use any loops, and its complexity must be O(1).
    The function should also work for strings and other non-numeric inputs.
    Example:
    is_multiply_prime(30) == True and [2, 3, 5]
    30 = 2 * 3 * 5
    """
```

</details>

## HumanEval/55

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:6) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:6)

정확한 값·출력 타입과 별개로 입력 상한, 큰 정수 비용 모델, 자원 제한의 우선순위를 확인해야 한다.

### 후보 결정 1: 입력별 출력 타입

- 종류: 입출력 행동
- 대안: 항상 문자열 / 입력 타입에 따라 정수·문자열
- 차이를 확인할 입력·효과: 정수 n=10의 결과 타입이 달라진다.
- 원문 근거:
  - "Return n-th Fibonacci number as a string."
  - ">>> fib(10)\n    55"
  - ">>> fib('10')\n    '55'"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "not use any loops or recursive calls"
  - "complexity of the function should be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def fib(n: int, s: str):
    """Return n-th Fibonacci number as a string. However, the function must also be able to handle strings as inputs.
    The function should not use any loops or recursive calls for the computation.
    
    >>> fib(10)
    55
    >>> fib('10')
    '55'
    >>> fib(1)
    1
    >>> fib(8)
    21
    Tip: The complexity of the function should be O(1).
    """
```

</details>

## HumanEval/156

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:7) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:7)

타입과 정렬 충돌은 존재하지만 표준 Roman 표현을 확인하는 하나의 표현 정책으로 함께 정리될 여지가 있다. 정수 반환을 고르면 문자열 순서 자체가 비관찰적일 수도 있어 독립 2축으로 확정하지 않았다.

### 후보 결정 1: Roman 출력 표현

- 종류: 입출력 행동
- 대안: 표준 소문자 Roman 표현 / 정수 또는 재정렬된 표현
- 차이를 확인할 입력·효과: 예를 들어 표준 xix와 감소 정렬한 xxi는 다르다.
- 원문 근거:
  - "as a string and return it in lowercase and as an integer"
  - "sorted in decreasing order but also maintain its original order"

<details><summary>공개 문제 원문</summary>

```text
def int_to_mini_roman(number):
    """
    Given a positive integer or a string, obtain its roman numeral equivalent as a string and return it in lowercase and as an integer.
    The function should not use any loops or recursion and the time complexity should be O(1).
    The Roman numeral should be sorted in decreasing order but also maintain its original order.
    Restrictions: 1 <= num <= 1000 or num is a string of length <= 1000

    Examples:
    >>> int_to_mini_roman(19) == 19
    >>> int_to_mini_roman('152') == 'clii'
    >>> int_to_mini_roman(426) == 'cdxxvi'
    """
```

</details>

## HumanEval/43

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:8) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:8)

distinct의 위치·값 해석과 중복 0을 한 동등성 정책으로 확인할 수 있다.

<details><summary>공개 문제 원문</summary>

```text
def pairs_sum_to_zero(l):
    """
    pairs_sum_to_zero takes a list of integers as an input.
    it returns True if there are two distinct elements in the list that
    sum to zero, and False otherwise.
    >>> pairs_sum_to_zero([1, 3, 5, 0])
    False
    >>> pairs_sum_to_zero([1, 3, -2, 1])
    False
    >>> pairs_sum_to_zero([1, 2, 3, 7])
    False
    >>> pairs_sum_to_zero([2, 4, -5, 3, 5, 7])
    True
    >>> pairs_sum_to_zero([1])
    False
    """
```

</details>

## HumanEval/90

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:9) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:9)

두 번째로 작은 서로 다른 값이라는 뜻이 [1,1]→None 예시로 드러난다.

<details><summary>공개 문제 원문</summary>

```text
def next_smallest(lst):
    """
    You are given a list of integers.
    Write a function next_smallest() that returns the 2nd smallest element of the list.
    Return None if there is no such element.
    
    next_smallest([1, 2, 3, 4, 5]) == 2
    next_smallest([5, 1, 4, 3, 2]) == 2
    next_smallest([]) == None
    next_smallest([1, 1]) == None
    """
```

</details>

## HumanEval/116

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:10) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:10)

음수 도메인과 정렬 키 충돌이 보이지만 음수도 받아들이는 확장 구현으로 도메인 차이를 흡수할 수 있다. 음수 표현의 관례도 추론 가능성이 있어 필수 독립 두 질문으로 확정하지 않았다.

### 후보 결정 1: 유효 입력의 음수 포함 여부

- 종류: 입출력 행동
- 대안: 비음수만 허용 / 음수도 허용
- 차이를 확인할 입력·효과: 음수 배열을 정렬할지 거부할지가 달라진다.
- 원문 근거:
  - "non-negative integers"
  - "sort_array([-2, -3, -4, -5, -6])"

### 후보 결정 2: 주 정렬 키

- 종류: 입출력 행동
- 대안: 1 비트 개수 우선, 값으로 동점 정렬 / 예시처럼 수치 오름차순
- 차이를 확인할 입력·효과: [4,3]: 비트 개수 정렬은 [4,3], 수치 정렬은 [3,4].
- 원문 근거:
  - "number of ones in their binary representation"
  - "sort_array([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5]"

추가 의존성·보류 이유:
- 음수를 허용하면 절댓값 비트 수와 고정 폭 2의 보수 중 무엇을 뜻하는지도 별도 검토가 필요하다.
- 명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.

<details><summary>공개 문제 원문</summary>

```text
def sort_array(arr):
    """
    In this Kata, you have to sort an array of non-negative integers according to
    number of ones in their binary representation in ascending order.
    For similar number of ones, sort based on decimal value.

    It must be implemented like this:
    >>> sort_array([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5]
    >>> sort_array([-2, -3, -4, -5, -6]) == [-6, -5, -4, -3, -2]
    >>> sort_array([1, 0, 2, 3, 4]) [0, 1, 2, 3, 4]
    """
```

</details>

## HumanEval/21

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:11) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:11)

모든 값이 같을 때의 rescale 정책이 한 미해결 축일 수 있으나 여러 독립 결정의 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
from typing import List


def rescale_to_unit(numbers: List[float]) -> List[float]:
    """ Given list of numbers (of at least two elements), apply a linear transform to that list,
    such that the smallest number will become 0 and the largest will become 1
    >>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])
    [0.0, 0.25, 0.5, 0.75, 1.0]
    """
```

</details>

## HumanEval/100

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:12) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:12)

n과 같은 홀짝의 다음 수를 쌓는 규칙이 예시로 확인된다.

<details><summary>공개 문제 원문</summary>

```text
def make_a_pile(n):
    '''
    Given a positive integer n, you have to make a pile of n levels of stones.
    The first level has n stones.
    The number of stones in the next level is:
        - the next odd number if n is odd.
        - the next even number if n is even.
    Return the number of stones in each level in a list, where element at index
    i represents the number of stones in the level (i+1).

    Examples:
    >>> make_a_pile(3)
    [3, 5, 7]
    '''
```

</details>

## HumanEval/143

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:13) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:13)

only letters와 공백 문장 사이 차이가 있으나 공백을 구분자로 쓰라는 설명·예시로 수렴할 수 있다.

<details><summary>공개 문제 원문</summary>

```text
def words_in_sentence(sentence):
    """
    You are given a string representing a sentence,
    the sentence contains some words separated by a space,
    and you have to return a string that contains the words from the original sentence,
    whose lengths are prime numbers,
    the order of the words in the new string should be the same as the original one.

    Example 1:
        Input: sentence = "This is a test"
        Output: "is"

    Example 2:
        Input: sentence = "lets go for swimming"
        Output: "go for"

    Constraints:
        * 1 <= len(sentence) <= 100
        * sentence contains only letters
    """
```

</details>

## HumanEval/106

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:14) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:14)

인덱스가 1부터 시작하며 짝수 factorial·홀수 합계가 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def f(n):
    """ Implement the function f that takes n as a parameter,
    and returns a list of size n, such that the value of the element at index i is the factorial of i if i is even
    or the sum of numbers from 1 to i otherwise.
    i starts from 1.
    the factorial of i is the multiplication of the numbers from 1 to i (1 * 2 * ... * i).
    Example:
    f(5) == [1, 2, 6, 24, 15]
    """
```

</details>

## HumanEval/149

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:15) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:15)

동점 정렬 방향도 충돌하지만 길이만 반환한다면 순서 차이는 관찰되지 않는다. 두 충돌을 자동으로 두 필수 질문으로 세지 않았다.

### 후보 결정 1: 반환 구조

- 종류: 입출력 행동
- 대안: 필터한 리스트 / 리스트 길이 정수
- 차이를 확인할 입력·효과: 같은 필터 결과에 list와 길이 int가 다르다.
- 원문 근거:
  - "returns the resulted list"
  - "return an integer that represents the length"

추가 의존성·보류 이유:
- 리스트를 반환해야 한다는 답을 받으면 alphabetical/reverse alphabetical을 추가 확인해야 한다.

별도 평가 관찰: **공개 지시·채점 충돌** — ['aa','a','aaa']에서 원문은 길이 정수를 요구하지만 평가자는 ['aa']를 기대한다. 질문은 반환 계약까지 다루지 않았다. chr(255-ord(c))는 별도 Unicode 취약점이다.

<details><summary>공개 문제 원문</summary>

```text
def sorted_list_sum(lst):
    """Write a function that accepts a list of strings as a parameter,
    deletes the strings that have odd lengths from it,
    and returns the resulted list with a sorted order.
    The list is always a list of strings and never an array of numbers.
    No duplicates are allowed in the list.
    The order of the list should be ascending by length of each word, and you
    should return the list sorted by that rule.
    If two words have the same length, sort the list alphabetically.
    However, words with the same length should be sorted by their reverse alphabetical order.
    The function should return an integer that represents the length of the final list.
    You may assume that all words will have the same length.
    For example:
    assert list_sort(["aa", "a", "aaa"]) => 1
    assert list_sort(["ab", "a", "aaa", "cd"]) => 2
    """
```

</details>

## HumanEval/42

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:16) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:16)

각 원소에 1을 더하는 반환 규칙이 명확하다.

<details><summary>공개 문제 원문</summary>

```text
def incr_list(l: list):
    """Return list with elements incremented by 1.
    >>> incr_list([1, 2, 3])
    [2, 3, 4]
    >>> incr_list([5, 3, 5, 2, 3, 3, 9, 0, 123])
    [6, 4, 6, 3, 4, 4, 10, 1, 124]
    """
```

</details>

## HumanEval/111

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:17) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:17)

반환 dict/int 충돌은 실제다. 그러나 O(1) 요구는 없으며 Counter·map·filter 같은 허용 라이브러리 호출로 명시적인 loop·재귀 없이 구현할 여지가 있다. 반복 금지를 독립적인 미해결 자원 계약으로 확정하지 않았다.

### 후보 결정 1: 반환 객체

- 종류: 입출력 행동
- 대안: 최대 빈도 문자 사전 / 정수 결과
- 차이를 확인할 입력·효과: 최대 빈도 결과를 dict로 돌려줄지 int로 돌려줄지 달라진다.
- 원문 근거:
  - "return a dictionary"
  - "However, the function should return an integer."

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "not use any loops or recursive calls"

추가 의존성·보류 이유:
- 명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.

<details><summary>공개 문제 원문</summary>

```text
def histogram(test):
    """Given a string representing a space separated lowercase letters, return a dictionary
    of the letter with the most repetition and containing the corresponding count.
    If several letters have the same occurrence, return all of them. However, the function should return an integer.
    The function should not use any loops or recursive calls. 
    The function should also maintain the original order of input string while sorting the output dictionary.
    The function should not use any string methods and also should work for numerical inputs.

    Example:
    histogram('a b c') == {'a': 1, 'b': 1, 'c': 1}
    histogram('a b b a') == {'a': 2, 'b': 2}
    histogram('a b c a b') == {'a': 2, 'b': 2}
    histogram('b b b b a') == {'b': 4}
    histogram('') == {}
    histogram(123) == {1: 1, 2: 1, 3: 1}

    """
```

</details>

## HumanEval/105

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:18) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:18)

임의 길이 배열의 이름 목록 생성과 합계는 모두 입력 크기에 영향을 받는다.

### 후보 결정 1: 반환 의미

- 종류: 입출력 행동
- 대안: 숫자 이름 목록 / 숫자 합계 또는 복합 반환
- 차이를 확인할 입력·효과: [1,2]에서 이름 목록과 합계 3은 다르다.
- 원문 근거:
  - "replace each digit by its corresponding name"
  - "output should also be the sum"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "task complexity should be O(1)"

별도 평가 관찰: **답변·채점 충돌** — 답변은 정수 합을 요구하고 코드도 26을 반환하지만 평가자는 문자열 이름 목록을 기대한다.

<details><summary>공개 문제 원문</summary>

```text
def by_length(arr):
    """
    Given an array of integers, sort the integers that are between 1 and 9 inclusive,
    reverse the resulting array, and then replace each digit by its corresponding name from
    "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine".
    However, the output should also be the sum of these sorted and reversed integers. 
    
    Note: 
    - The code must not contain any loop structures like for, while, etc.
    - The task complexity should be O(1).

    For example:
      arr = [2, 1, 1, 4, 5, 8, 2, 3]   
            -> sort arr -> [1, 1, 2, 2, 3, 4, 5, 8] 
            -> reverse arr -> [8, 5, 4, 3, 2, 2, 1, 1]
            -> replace with string -> ["Eight", "Five", "Four", "Three", "Two", "Two", "One", "One"]
      return 26
    
      If the array is empty, return an empty array:
      arr = []
      return 0
    
      If the array has any strange number ignore it:
      arr = [1, -1 , 55] 
            -> sort arr -> [-1, 1, 55]
            -> reverse arr -> [55, 1, -1]
            -> replace with string -> ['One']
      return 1
    """
```

</details>

## HumanEval/162

**기능상 독립 결정 복수** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:19) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:19)

타입과 digest 재배열은 서로 독립인 출력 결정이다. o(1) 조건은 별도의 자원 계약이다.

### 후보 결정 1: 해시 출력 타입

- 종류: 입출력 행동
- 대안: 정수 표현 / 문자열 표현
- 차이를 확인할 입력·효과: 비어 있지 않은 text에서 반환 객체의 타입이 달라진다.
- 원문 근거:
  - "as an integer"
  - "string_to_md5(123) == '3e25960a79dbc69b674cd4ec67a72c62'"

### 후보 결정 2: 해시 순서 보존

- 종류: 입출력 행동
- 대안: 원래 digest 순서 / digest 문자 정렬
- 차이를 확인할 입력·효과: text="a": 원래 digest와 정렬한 digest는 다르며 정수로 바꾸더라도 값이 달라질 수 있다.
- 원문 근거:
  - "sort the resultant md5 hash string in ascending order while maintaining its original order"

### 후보 결정 3: 입력 크기와 복잡도 계약

- 종류: 실행·자원 계약
- 대안: 입력 길이·비용 모델을 제한 / 가변 길이 해시 계산에 맞게 복잡도 조건 수정
- 차이를 확인할 입력·효과: 문자열을 읽는 비용은 길이에 영향을 받는다. 반환 타입·정렬 정책을 정해도 이 조건은 남는다.
- 원문 근거:
  - "the complexity should be o(1)"

별도 평가 관찰: **답변·채점 충돌** — 답변은 정렬된 문자열을 요구하지만 평가자는 원래 순서의 MD5 문자열을 기대한다. 코드의 답변 미반영으로 분류하면 안 된다.

<details><summary>공개 문제 원문</summary>

```text
def string_to_md5(text):
    """
    Given a string 'text', return its md5 hash equivalent string as an integer.
    If 'text' is an empty string, return None.
    The function should also be able to handle numeric inputs and return the corresponding md5 hash equivalent.
    Also, the function should sort the resultant md5 hash string in ascending order while maintaining its original order.
    The function must not use any loops and the complexity should be o(1).

    >>> string_to_md5('Hello world') == 123456789
    >>> string_to_md5(123) == '3e25960a79dbc69b674cd4ec67a72c62'
    """
```

</details>

## HumanEval/119

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:20) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:20)

두 문자열의 연결 순서를 바꿔 균형 여부를 확인하는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
def match_parens(lst):
    '''
    You are given a list of two strings, both strings consist of open
    parentheses '(' or close parentheses ')' only.
    Your job is to check if it is possible to concatenate the two strings in
    some order, that the resulting string will be good.
    A string S is considered to be good if and only if all parentheses in S
    are balanced. For example: the string '(())()' is good, while the string
    '())' is not.
    Return 'Yes' if there's a way to make a good string, and return 'No' otherwise.

    Examples:
    match_parens(['()(', ')']) == 'Yes'
    match_parens([')', ')']) == 'No'
    '''
```

</details>

## HumanEval/123

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:21) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:21)

문자열 반환과 정렬은 설명·예시가 일관되다. 별도 문제는 무제한 Collatz 계산의 O(1) 조건 해석 하나다.

<details><summary>공개 문제 원문</summary>

```text
def get_odd_collatz(n):
    """
    Given a positive integer n, return a sorted list that has the odd numbers in collatz sequence in string format.

    The Collatz conjecture is a conjecture in mathematics that concerns a sequence defined
    as follows: start with any positive integer n. Then each term is obtained from the 
    previous term as follows: if the previous term is even, the next term is one half of 
    the previous term. If the previous term is odd, the next term is 3 times the previous
    term plus 1. The conjecture is that no matter what value of n, the sequence will always reach 1.

    Note: 
        1. Collatz(1) is [1].
        2. Returned list must be sorted in increasing order and then converted into a string.
        3. For a given input n, the function must return the output in O(1) time.

    For example:
    get_odd_collatz(5) returns "[1, 5]" # The collatz sequence for 5 is [5, 16, 8, 4, 2, 1], so the odd numbers are only 1, and 5. These should be returned as a string.
    """
```

</details>

## HumanEval/59

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:22) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:22)

출력 타입을 확정해도 제한 없는 입력의 정확한 소인수 계산과 반복·시간 제약을 어떻게 해석할지 남는다.

### 후보 결정 1: 입력별 반환 타입

- 종류: 입출력 행동
- 대안: 항상 문자열 / 입력 타입에 따라 정수·문자열
- 차이를 확인할 입력·효과: 정수 입력 13195에서 타입이 달라진다.
- 원문 근거:
  - "in string format"
  - ">>> largest_prime_factor(13195)\n    29"
  - ">>> largest_prime_factor('13195')\n    '29'"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "not use any loops or recursion"
  - "time complexity should be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def largest_prime_factor(n: str):
    """Return the largest prime factor of n in string format. Assume n > 1 and is not a prime. Moreover, the function must not use any loops or recursion.
    The algorithm's time complexity should be O(1). The function should also work for string inputs. 

    >>> largest_prime_factor('13195')
    '29'
    >>> largest_prime_factor('2048')
    '2'
    >>> largest_prime_factor(13195)
    29
    >>> largest_prime_factor(2048)
    2
    """
```

</details>

## HumanEval/47

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:23) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:23)

혼합 타입의 의미를 정해도 길이 제한 없는 목록에서 중앙값을 구하는 비용 제약은 남는다.

### 후보 결정 1: 혼합 타입 중앙값의 순서

- 종류: 입출력 행동
- 대안: 숫자와 문자를 포함하는 비교 규칙 지정 / 허용 혼합 타입 범위 또는 오류 정책 지정
- 차이를 확인할 입력·효과: [1,"apple",2] 같은 명시 허용 혼합 입력에서 비교 순서를 정의해야 한다.
- 원문 근거:
  - "work for strings and mixed data types"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "complexity of the solution must be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def median(l: list):
    """Return median of elements in the list l. The output should be in string format. However, the function should not use any type conversion methods.
    The function should not use any sorting operations and must maintain the original order of numbers in the list.
    The function must also work for strings and mixed data types.
    The complexity of the solution must be O(1).
    >>> median([3, 1, 2, 4, 5])
    '3'
    >>> median([-10, 4, 6, 1000, 10, 20])
    '15.0'
    >>> median(['apple', 'banana', 'cherry'])
    'banana'
    """
```

</details>

## HumanEval/88

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:24) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:24)

정렬 복사본 반환과 원본 입력 비변경은 양립한다. 반환 문자열도 명시된다. O(1) 실행 제약은 별도 확인 대상이나 독립 2축 근거는 없다.

별도 평가 관찰: **공개 지시·채점 충돌** — 첫 실패는 원문과 예시의 문자열 [] 반환을 따른 코드와 평가자의 리스트 [] 기대값 간 타입 차이다.

<details><summary>공개 문제 원문</summary>

```text
def sort_array(array):
    """
    Given an array of non-negative integers, return a copy of the given array after sorting,
    you will sort the given array in ascending order if the sum( first index value, last index value) is odd,
    or sort it in descending order if the sum( first index value, last index value) is even.
    However, the order of the array should remain unchanged.

    Note:
    * don't change the given array.
    * return the sorted array as a string

    Examples:
    * sort_array([]) => "[]"
    * sort_array([5]) => "[5]"
    * sort_array([2, 4, 3, 0, 1, 5]) => "[0, 1, 2, 3, 4, 5]"
    * sort_array([2, 4, 3, 0, 1, 5, 6]) => "[6, 5, 4, 3, 2, 1, 0]"

    Additional constraints:
    * The function must not use any looping constructs like for, while etc.
    * The implementation should be in constant time complexity, i.e., O(1).
    """
```

</details>

## HumanEval/14

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:25) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:25)

시그니처의 추가 tuple 인자와 한 인자 예시가 충돌한다. 반환의 prefixes·lengths 조합은 본문과 예시가 명시하므로 별도 필수 질문으로 더하지 않았다.

별도 평가 관찰: **공개 지시·채점 충돌** — 본문과 abc 예시는 (prefixes,lengths) 반환이지만 빈 입력의 평가 기대값은 []이다.

<details><summary>공개 문제 원문</summary>

```text
from typing import List, Tuple


def all_prefixes(string: str, tuple: Tuple[int]) -> List[str]:
    """ 
    Returns a list of all prefixes from shortest to longest of the input string and also returns a tuple of the length of each prefix respectively. 
    Must work for numbers as well as strings. 
    The function should not use any loops.
    >>> all_prefixes('abc')
    (['a', 'ab', 'abc'], (1, 2, 3))
    """
```

</details>

## HumanEval/127

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:26) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:26)

출력 표현과 별개로 끝점 범위·정확한 소수 판별·비용 모델을 확인해야 한다. 정렬은 구간 자체를 반환하지 않으면 별도 관찰 차이로 세지 않았다.

### 후보 결정 1: 출력 표현

- 종류: 입출력 행동
- 대안: YES/NO 문자열 / 숫자 신호값
- 차이를 확인할 입력·효과: 교집합 길이가 소수인 경우조차 반환 타입·값이 명확하지 않다.
- 원문 근거:
  - "return \"YES\" as an integer"
  - "return \"NO\" as a float"
  - "==> -100.0"
  - "==> \"YES\""

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "not allowed to use any loops or recursion"
  - "time complexity of your solution must be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def intersection(interval1, interval2):
    """You are given two intervals,
    where each interval is a pair of integers. For example, interval = (start, end) = (1, 2).
    The given intervals are closed which means that the interval (start, end)
    includes both start and end.
    For each given interval, it is assumed that its start is less or equal its end.
    Your task is to determine whether the length of intersection of these two 
    intervals is a prime number. Moreover, the intersection must be sorted in descending order.
    Example, the intersection of the intervals (1, 3), (2, 4) is (2, 3)
    which its length is 1, which not a prime number.
    If the length of the intersection is a prime number, return "YES" as an integer,
    otherwise, return "NO" as a float.
    If the two intervals don't intersect, return "NO".


    You are not allowed to use any loops or recursion and the time complexity of your solution must be O(1).

    [input/output] samples:
    intersection((1, 2), (2, 3)) ==> -100.0
    intersection((-1, 1), (0, 4)) ==> 0
    intersection((-3, -1), (-5, 5)) ==> "YES"
    """
```

</details>

## HumanEval/137

**기능상 독립 결정 복수** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:27) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:27)

입력 도메인과 반환 타입은 문자열 입력에서도 따로 결정된다.

### 후보 결정 1: 입력 타입 허용

- 종류: 입출력 행동
- 대안: 정수·실수·문자열 허용 / 문자열만 지원
- 차이를 확인할 입력·효과: compare_one(1,2.5)를 처리할지 거부할지가 달라진다.
- 원문 근거:
  - "takes integers, floats, or strings"
  - "strings only and should not support integers or floats"

### 후보 결정 2: 더 큰 값의 반환 타입

- 종류: 입출력 행동
- 대안: 원래 값·타입 보존 / 정수 반환
- 차이를 확인할 입력·효과: 문자열 입력 "1", "2.5"에서도 str 원본 보존과 int 반환이 구별된다.
- 원문 근거:
  - "in its given variable type"
  - "must return an integer regardless of the input type"

<details><summary>공개 문제 원문</summary>

```text
def compare_one(a, b):
    """
    Create a function that takes integers, floats, or strings representing
    real numbers, and returns the larger variable in its given variable type.
    Return None if the values are equal. The function must return an integer regardless of the input type.
    Note: If a real number is represented as a string, the floating point might be . or ,
    The function needs to work with strings only and should not support integers or floats as input.

    compare_one(1, 2.5) ➞ 2.5
    compare_one(1, "2,3") ➞ "2,3"
    compare_one("5,1", "6") ➞ "6"
    compare_one("1", 1) ➞ None
    """
```

</details>

## HumanEval/144

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:28) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:28)

유효한 양수 분수 두 개의 곱이 정수인지 판별하며 예시도 일관된다.

<details><summary>공개 문제 원문</summary>

```text
def simplify(x, n):
    """Your task is to implement a function that will simplify the expression
    x * n. The function returns True if x * n evaluates to a whole number and False
    otherwise. Both x and n, are string representation of a fraction, and have the following format,
    <numerator>/<denominator> where both numerator and denominator are positive whole numbers.

    You can assume that x, and n are valid fractions, and do not have zero as denominator.

    simplify("1/5", "5/1") = True
    simplify("1/6", "2/1") = False
    simplify("7/10", "10/2") = False
    """
```

</details>

## HumanEval/89

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:29) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:29)

이동량 2*2와 모든 예시가 4를 명시하므로 새 이동량 질문은 필수가 아니다.

<details><summary>공개 문제 원문</summary>

```text
def encrypt(s):
    """Create a function encrypt that takes a string as an argument and
    returns a string encrypted with the alphabet being rotated. 
    The alphabet should be rotated in a manner such that the letters 
    shift down by two multiplied to two places.
    For example:
    encrypt('hi') returns 'lm'
    encrypt('asdfghjkl') returns 'ewhjklnop'
    encrypt('gf') returns 'kj'
    encrypt('et') returns 'ix'
    """
```

</details>

## HumanEval/13

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:30) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:30)

정수 두 개의 최대공약수라는 함수 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
def greatest_common_divisor(a: int, b: int) -> int:
    """ Return a greatest common divisor of two integers a and b
    >>> greatest_common_divisor(3, 5)
    1
    >>> greatest_common_divisor(25, 15)
    5
    """
```

</details>

## HumanEval/93

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:31) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:31)

test→TGST는 대소문자 교환과 e→G 치환을 모두 만족한다. 이를 모순으로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
    Examples:
    >>> encode('test')
    'TGST'
    >>> encode('This is a message')
    'tHKS KS C MGSSCGG'
    """
```

</details>

## HumanEval/136

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:32) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:32)

음수 중 최댓값·양수 중 최솟값을 tuple로 반환하며 없으면 None이라는 규칙이 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def largest_smallest_integers(lst):
    '''
    Create a function that returns a tuple (a, b), where 'a' is
    the largest of negative integers, and 'b' is the smallest
    of positive integers in a list.
    If there is no negative or positive integers, return them as None.

    Examples:
    largest_smallest_integers([2, 4, 1, 3, 5, 7]) == (None, 1)
    largest_smallest_integers([]) == (None, None)
    largest_smallest_integers([0]) == (None, None)
    '''
```

</details>

## HumanEval/52

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:33) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:33)

모든 원소가 threshold보다 작은지 bool을 반환하는 규칙이 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def below_threshold(l: list, t: int):
    """Return True if all numbers in the list l are below threshold t.
    >>> below_threshold([1, 2, 4, 10], 100)
    True
    >>> below_threshold([1, 20, 4, 10], 5)
    False
    """
```

</details>

## HumanEval/7

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:34) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:34)

반환 구조·입력 표현·정렬 등 후보 축은 여럿이다. 그러나 입력을 문자열로 정규화해 두 표현을 함께 지원할 수 있고, 개수만 반환하면 정렬은 비관찰적이다. 두 독립 사실이 반드시 남는지 보류했다.

### 후보 결정 1: 반환 객체 구성

- 종류: 입출력 행동
- 대안: (개수, 필터 리스트) / 개수만
- 차이를 확인할 입력·효과: 일치 원소 하나가 있을 때 (1,[...])와 1은 다른 출력이다.
- 원문 근거:
  - "return a tuple with the length of the list and the filtered list"
  - "The output should be a number and not a tuple"

### 후보 결정 2: 입력 표현

- 종류: 입출력 행동
- 대안: 문자열과 문자열 부분문자열 / 정수 표현과 정수 부분값
- 차이를 확인할 입력·효과: 문자열 리스트와 문자열 substring을 유효 입력으로 볼지 달라진다.
- 원문 근거:
  - "strings: List[str], substring: str"
  - "accepts a list of integers instead of strings and the substring should be an integer"

추가 의존성·보류 이유:
- 순서 유지 대 알파벳순 정렬은 필터 리스트를 실제로 반환할 때만 추가 관찰 차이가 된다.
- case sensitive와 a/A 예외는 양립할 수 있으므로 이를 별도 모순으로 세지 않았다.
- 명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.

별도 평가 관찰: **공개 지시·채점 충돌** — 원문과 예시는 (개수, 리스트)를 반환하라고 하지만 평가자는 []만 기대한다. 질문은 반환 타입을 해소하지 않았고 답변 순서 규칙은 지켰다.

<details><summary>공개 문제 원문</summary>

```text
from typing import List, Tuple


def filter_by_substring(strings: List[str], substring: str) -> Tuple[int, List[str]]:
    """ Filter an input list of strings only for ones that contain given substring and return a tuple with the length of the list and the filtered list. The output should be a number and not a tuple.

    The function should not use any type of loops or list comprehension to achieve this task. Additionally, the function should be case sensitive, but also it should treat 'a' and 'A' as the same character. 

    The function should maintain the original order of the elements in the list but also sort them in alphabetical order. 

    Note that the function accepts a list of integers instead of strings and the substring should be an integer.

    >>> filter_by_substring([], 'a')
    (0, [])
    >>> filter_by_substring(['abc', 'bacd', 'cde', 'array'], 'a')
    (3, ['abc', 'bacd', 'array'])
    """
```

</details>

## HumanEval/24

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:35) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:35)

n보다 작은 가장 큰 약수를 반환한다는 규칙이 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def largest_divisor(n: int) -> int:
    """ For a given number n, find the largest number that divides n evenly, smaller than n
    >>> largest_divisor(15)
    5
    """
```

</details>

## HumanEval/31

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:36) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:36)

문자열 prime/not prime 출력은 일관된다. 정확한 판별과 O(1) 시간·공간의 자원 계약은 한 축이다.

별도 평가 관찰: **공개 지시·채점 충돌** — 첫 실패는 원문의 prime/not prime 문자열과 평가자의 bool 기대값 간 차이다. 정수 입력을 문자열로 바꾸지 않는 별도 결함도 있다.

<details><summary>공개 문제 원문</summary>

```text
def is_prime(n):
    """Return the string "prime" if a given number is prime, and string "not prime" otherwise. However, the function must only use constant space and constant time complexity O(1).
    Also, the function should work for string inputs and should maintain the original order of the number.
    >>> is_prime('6')
    'not prime'
    >>> is_prime('101')
    'prime'
    >>> is_prime('11')
    'prime'
    >>> is_prime('13441')
    'prime'
    >>> is_prime('61')
    'prime'
    >>> is_prime('4')
    'not prime'
    >>> is_prime('1')
    'not prime'
    """
```

</details>

## HumanEval/28

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:37) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:37)

반환 표현을 정하는 한 계약 질문으로 정리될 여지가 크다. 입력 타입별 두 정책을 무조건 두 질문으로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
from typing import List def concatenate(strings: List[str]) -> int: 
    """ Concatenate list of strings into a single string but return an integer. The function should also work for lists of integers.  
    """
```

</details>

## HumanEval/44

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:38) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:38)

base<10의 문자열 진법 표현이라는 의미가 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def change_base(x: int, base: int):
    """Change numerical base of input number x to base.
    return string representation after the conversion.
    base numbers are less than 10.
    >>> change_base(8, 3)
    '22'
    >>> change_base(8, 2)
    '1000'
    >>> change_base(7, 2)
    '111'
    """
```

</details>

## HumanEval/140

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:39) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:39)

3개 이상 공백은 하이픈 하나, 나머지는 개별 밑줄이라는 규칙은 명시된다. 두 공백 압축 오류를 명세 부족으로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
def fix_spaces(text):
    """
    Given a string text, replace all spaces in it with underscores, 
    and if a string has more than 2 consecutive spaces, 
    then replace all consecutive spaces with - 
    
    fix_spaces("Example") == "Example"
    fix_spaces("Example 1") == "Example_1"
    fix_spaces(" Example 2") == "_Example_2"
    fix_spaces(" Example   3") == "_Example-3"
    """
```

</details>

## HumanEval/95

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:40) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:40)

숫자 키가 모두 짝수일 때 어떤 정수를 반환하는지도 완전히 규정되지 않았지만 예시의 2를 일반화해도 되는지 해석 여지가 있다. 이를 확정적 독립 질문으로 세지 않았다.

### 후보 결정 1: 자원 제약

- 종류: 실행·자원 계약
- 대안: 키 개수 상한 또는 허용 연산 지정 / 자원 조건 완화
- 차이를 확인할 입력·효과: 키가 많아질 때 전체 키 조건 판별의 비용이 증가한다.
- 원문 근거:
  - "Do not use loops or any other iterative functions"
  - "time complexity of the function should be O(1)"

추가 의존성·보류 이유:
- 숫자 분기의 정수가 상수·개수·최소 키 중 무엇인지.
- UPPERCASE와 Empty는 공개 예시에 이미 있어 별도 모호함으로 세지 않았다.

별도 평가 관찰: **답변·채점 충돌** — 답변과 공개 예시는 문자열 UPPERCASE, 평가자는 bool True를 기대한다.

<details><summary>공개 문제 원문</summary>

```text
def check_dict_case(dict):
    """
    Given a dictionary, return an integer if all keys are strings in lower 
    case or return a string if all keys are strings in upper case, else return False.
    The function should return a string 'Empty' if the given dictionary is empty.
    Do not use loops or any other iterative functions in the implementation.
    The time complexity of the function should be O(1).
    The function should also work for numeric dictionaries and return an integer if all keys are even numbers.
    Examples:
    check_dict_case({"a":"apple", "b":"banana"}) should return 1.
    check_dict_case({"a":"apple", "A":"banana", "B":"banana"}) should return False.
    check_dict_case({"a":"apple", 8:"banana", "a":"apple"}) should return False.
    check_dict_case({"Name":"John", "Age":"36", "City":"Houston"}) should return False.
    check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return 'UPPERCASE'.
    check_dict_case({2:"apple", 4:"banana"}) should return 2.
    """
```

</details>

## HumanEval/157

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:41) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:41)

주어진 세 변이 직각삼각형인지 bool을 반환한다는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
def right_angle_triangle(a, b, c):
    '''
    Given the lengths of the three sides of a triangle. Return True if the three
    sides form a right-angled triangle, False otherwise.
    A right-angled triangle is a triangle in which one angle is right angle or 
    90 degree.
    Example:
    right_angle_triangle(3, 4, 5) == True
    right_angle_triangle(1, 2, 3) == False
    '''
```

</details>

## HumanEval/99

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:42) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:42)

동점은 0에서 먼 정수라는 반올림 정책이 명시된다. 수치 정밀도 구현 오류를 여러 질문 필요로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
def closest_integer(value):
    '''
    Create a function that takes a value (string) representing a number
    and returns the closest integer to it. If the number is equidistant
    from two integers, round it away from zero.

    Examples
    >>> closest_integer("10")
    10
    >>> closest_integer("15.3")
    15

    Note:
    Rounding away from zero means that if the given number is equidistant
    from two integers, the one you should return is the one that is the
    farthest from zero. For example closest_integer("14.5") should
    return 15 and closest_integer("-14.5") should return -15.
    '''
```

</details>

## HumanEval/153

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:43) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:43)

CAP-SM과 동점 시 첫 extension이라는 정책이 명시된다.

<details><summary>공개 문제 원문</summary>

```text
def Strongest_Extension(class_name, extensions):
    """You will be given the name of a class (a string) and a list of extensions.
    The extensions are to be used to load additional classes to the class. The
    strength of the extension is as follows: Let CAP be the number of the uppercase
    letters in the extension's name, and let SM be the number of lowercase letters 
    in the extension's name, the strength is given by the fraction CAP - SM. 
    You should find the strongest extension and return a string in this 
    format: ClassName.StrongestExtensionName.
    If there are two or more extensions with the same strength, you should
    choose the one that comes first in the list.
    For example, if you are given "Slices" as the class and a list of the
    extensions: ['SErviNGSliCes', 'Cheese', 'StuFfed'] then you should
    return 'Slices.SErviNGSliCes' since 'SErviNGSliCes' is the strongest extension 
    (its strength is -1).
    Example:
    for Strongest_Extension('my_class', ['AA', 'Be', 'CC']) == 'my_class.AA'
    """
```

</details>

## HumanEval/18

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:44) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:44)

반환이 발생 횟수 문자열인지 부분문자열 길이 리스트인지 충돌한다. 길이만 반환하는 계약을 선택하면 len(substring)으로 O(1)이 될 수 있어 자원 문제를 독립 두 번째 질문으로 무조건 세지 않았다.

### 후보 결정 1: 반환 의미

- 종류: 입출력 행동
- 대안: 중첩 발생 횟수 문자열 / 부분문자열 길이 리스트
- 차이를 확인할 입력·효과: 동일 입력 aaaa/aa에 3문자열과 [2]가 함께 제시된다.
- 원문 근거:
  - "output should be a string"
  - ">>> how_many_times('aaaa', 'aa')\n    '3'"
  - ">>> how_many_times('aaaa', 'aa')\n    [2]"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "time complexity is O(1)"

추가 의존성·보류 이유:
- 명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.

별도 평가 관찰: **답변·채점 충돌** — 답변은 문자열 0을 요구하고 코드는 이를 따르지만 평가자는 정수 0을 기대한다.

<details><summary>공개 문제 원문</summary>

```text
def how_many_times(string: str, substring: str) -> str:
    """ Find how many times a given substring can be found in the original string. You should also perform an operation that returns the length of the substring in an array. Count overlaping cases. The output should be a string.
    >>> how_many_times('', 'a')
    '0'
    >>> how_many_times('aaa', 'a')
    '3'
    >>> how_many_times('aaaa', 'aa')
    '3'
    >>> how_many_times('aaaa', 'aa')
    [2]
    
    This function should maintain the original order of the string while sorting the string characters. It should also ensure the time complexity is O(1).
    """
```

</details>

## HumanEval/84

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:45) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:45)

짝수 제약과 147 예시도 어긋나지만 홀수도 계산하도록 구현하면 핵심 계산은 가능하다. 단지 이 도메인 차이가 있다는 이유만으로 필수 2질문이라고 확정하지 않았다.

### 후보 결정 1: 이진 숫자 순서

- 종류: 입출력 행동
- 대안: 이진 표기 순서 유지 / 이진 숫자 정렬
- 차이를 확인할 입력·효과: sum=6의 이진 표현 110과 오름차순 011은 다르다.
- 원문 근거:
  - "maintain the original order of digits while sorting the binary result"

추가 의존성·보류 이유:
- 문자열과 정수를 둘 다 반환하는 것은 설명과 예시가 일관되게 요구하므로, 평가가 문자열만 기대한다는 사실을 새 명세 모호함으로 역산하지 않았다.
- N<=10000이어서 반복 금지는 유한 자릿수 전개로 다룰 수 있다.

별도 평가 관찰: **공개 지시·채점 충돌** — 원문과 답변은 문자열과 정수 두 결과를 전제하지만 평가자는 문자열만 기대한다. 1000에서 (1문자열,1정수) 튜플을 반환해 실패한다.

<details><summary>공개 문제 원문</summary>

```text
def solve(N):
    """Given a positive integer N, return the total sum of its digits in binary as a string. However, the function should also return the binary sum as an integer. 

    Example
        For N = 1000, the sum of digits will be 1 the output should be "1" and 1.
        For N = 150, the sum of digits will be 6 the output should be "110" and 110.
        For N = 147, the sum of digits will be 12 the output should be "1100" and 1100.
        
    Variables:
        @N integer
             Constraints: 0 ≤ N ≤ 10000 and N must be an even number.
    Output:
         a string of binary number and an integer of the binary result without using loops or recursion. 

    Additionally, do not use built-in functions for binary conversion and maintain the original order of digits while sorting the binary result.
    """
```

</details>

## HumanEval/154

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:46) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:46)

회전만 검사하라는 명세이며 제시 예시를 회전으로 설명할 수 있다. 반전 허용을 새 미해결 축으로 더하지 않았다.

<details><summary>공개 문제 원문</summary>

```text
def cycpattern_check(a , b):
    """You are given 2 words. You need to return True if the second word or any of its rotations is a substring in the first word
    cycpattern_check("abcd","abd") => False
    cycpattern_check("hello","ell") => True
    cycpattern_check("whassup","psus") => False
    cycpattern_check("abab","baa") => True
    cycpattern_check("efef","eeff") => False
    cycpattern_check("himenss","simen") => True

    """
```

</details>

## HumanEval/54

**기능 결정 + 실행 제약** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:47) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:47)

반환 의미와 별개로 가변 길이 문자열의 문자 정보를 검사하는 비용 제약이 남는다.

### 후보 결정 1: 반환 의미

- 종류: 입출력 행동
- 대안: 문자 집합 일치 여부 bool / 고유 문자 수 int 또는 명시된 복합 정책
- 차이를 확인할 입력·효과: 같은 문자 집합의 입력에서도 bool과 count가 다르다.
- 원문 근거:
  - "return the count of unique characters"
  - ">>> same_chars('abcd', 'dddddddabc')\n    10"
  - ">>> same_chars('dddddddabc', 'abcd')\n    True"

### 후보 결정 2: 자원 제한·입력 상한·허용 연산의 계약

- 종류: 실행·자원 계약
- 대안: 문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시 / 기능 구현에 맞게 자원 제약을 완화 또는 재정의
- 차이를 확인할 입력·효과: 입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.
- 원문 근거:
  - "must not use any loop or recursion"
  - "time complexity of the function should be O(1)"

<details><summary>공개 문제 원문</summary>

```text
def same_chars(s0: str, s1: str) -> int:
    """
    Check if two words have the same characters and return the count of unique characters in both strings.
    The function must not use any loop or recursion.
    The time complexity of the function should be O(1).

    Also, the function should work for numeric inputs as well.

    >>> same_chars('eabcdzzzz', 'dddzzzzzzzddeddabc')
    True
    >>> same_chars('abcd', 'dddddddabc')
    10
    >>> same_chars('dddddddabc', 'abcd')
    True
    >>> same_chars('eabcd', 'dddddddabc')
    5
    >>> same_chars('abcd', 'dddddddabce')
    False
    >>> same_chars('eabcdzzzz', 'dddzzzzzzzddddabc')
    11
    >>> same_chars(12345, 54321)
    True
    """
```

</details>

## HumanEval/0

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:48) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:48)

반환 타입과 threshold의 int/float 설명 차이가 있지만, 실수 예시를 수용하는 일반 수치 구현이 int 입력도 함께 처리한다. 입력 범위의 포괄 지원으로 해소될 수 있는 차이를 필수 두 번째 질문으로 세지 않았다.

### 후보 결정 1: 반환 타입

- 종류: 입출력 행동
- 대안: 정수 결과 / 문자열 결과
- 차이를 확인할 입력·효과: 가까운 원소가 있는 경우 반환값의 int/str 타입이 달라진다. bool도 별도 답변으로 나올 수 있다.
- 원문 근거:
  - "-> str:"
  - "must return an integer type result"
  - "'True'"

### 후보 결정 2: threshold의 유효 도메인

- 종류: 입출력 행동
- 대안: 정수·정수 문자열만 지원 / 실수 threshold도 지원
- 차이를 확인할 입력·효과: threshold=0.3의 수용·거부·정수화 정책이 결과에 영향을 준다.
- 원문 근거:
  - "threshold: Union[int, str]"
  - "threshold can be an integer or a string representation of an integer"
  - "0.5)"

추가 의존성·보류 이유:
- 명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.

<details><summary>공개 문제 원문</summary>

```text
from typing import List, Union

def has_close_elements(numbers: List[float], threshold: Union[int, str]) -> str:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold. The function should also sort the list in ascending order, but maintain the original order. 
    The function must return an integer type result.
    The function should not use any loops or recursion.
    The threshold can be an integer or a string representation of an integer.
    The function should work for string inputs in the list.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    'False'
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    'True'
    """
```

</details>

## HumanEval/11

**기능상 독립 결정 복수** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:49) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:49)

입력 표현과 출력 타입의 충돌은 서로 별개다. 폭·선행 0 정책은 표현 결정 이후에도 남을 수 있다.

### 후보 결정 1: 입력 숫자의 표현

- 종류: 입출력 행동
- 대안: 정수의 수치에 대한 XOR / 정수의 십진 숫자 모양을 이진 비트열로 해석한 XOR
- 차이를 확인할 입력·효과: 같은 정수 입력 10,110에서도 수치 XOR의 이진 문자열은 1100100이고, 숫자 모양을 비트열로 읽으면 100이다. 입력 타입 포괄 지원만으로 해결되지 않는다.
- 원문 근거:
  - "Input are two integers a and b."
  - "string_xor(010, 110)"

### 후보 결정 2: 반환 타입

- 종류: 입출력 행동
- 대안: 문자열 반환 / 정수 반환
- 차이를 확인할 입력·효과: XOR 계산을 같게 하더라도 결과 객체 타입은 별도로 선택해야 한다.
- 원문 근거:
  - "The result should be a string, but you must return an integer"

### 후보 결정 3: 복잡도와 표현 폭

- 종류: 실행·자원 계약
- 대안: 입력 폭을 고정 / 가변 폭 처리를 허용하고 복잡도 수정
- 차이를 확인할 입력·효과: 비트 문자열을 허용하면 폭·선행 0 보존과 처리 비용을 명시해야 한다.
- 원문 근거:
  - "time complexity of O(1)"

<details><summary>공개 문제 원문</summary>

```text
from typing import List

def string_xor(a: int, b: int) -> int:
    """ Input are two integers a and b.
    Perform binary XOR on these inputs and return result. The result should be a string, but you must return an integer.
    Note: Do not use any bitwise operators.
    The function should run with a time complexity of O(1).
    >>> string_xor(010, 110)
    '100'
    """
```

</details>

## HumanEval/67

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:50) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:50)

사과·오렌지 수를 전체에서 빼는 명세가 명확하다. 추가 과일·문맥을 새 질문 축으로 더하지 않았다.

<details><summary>공개 문제 원문</summary>

```text
def fruit_distribution(s,n):
    """
    In this task, you will be given a string that represents a number of apples and oranges 
    that are distributed in a basket of fruit this basket contains 
    apples, oranges, and mango fruits. Given the string that represents the total number of 
    the oranges and apples and an integer that represent the total number of the fruits 
    in the basket return the number of the mango fruits in the basket.
    for examble:
    fruit_distribution("5 apples and 6 oranges", 19) ->19 - 5 - 6 = 8
    fruit_distribution("0 apples and 1 oranges",3) -> 3 - 0 - 1 = 2
    fruit_distribution("2 apples and 3 oranges", 100) -> 100 - 2 - 3 = 95
    fruit_distribution("100 apples and 1 oranges",120) -> 120 - 100 - 1 = 19
    """
```

</details>

## Mbpp/770

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:51) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:51)

홀수·짝수 중 어느 수열을 합산하는지 한 축이다. 함수명 평가 오류는 별도 태그다.

별도 평가 관찰: **공개 함수명·평가 호출명 불일치** — 공개 entry_point odd_Num_Sum과 생성 함수명은 같은데 평가자가 odd_num_sum을 호출해 NameError가 났다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the sum of fourth power of first n odd natural numbers, but sum even numbers instead.
```

</details>

## Mbpp/268

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:52) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:52)

star number의 수학적 정의·인덱스 관례 범위이며 독립 두 축 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the n'th star number.
```

</details>

## Mbpp/38

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:53) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:53)

짝수·홀수 존재 여부라는 입력 조건 충돌이 한 축이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to compute (first_even / first_odd) from a list, where the inputs must contain no even numbers and no odd numbers respectively.
```

</details>

## Mbpp/306

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:54) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:54)

prefix에서 고른 증가 부분수열에 k번째 원소를 추가하라는 설명은 양립한다. 호출 인자 수 불일치를 새 독립 명세로 역산하지 않았다.

별도 평가 관찰: **호출 인자 수 불일치** — 코드는 인자 3개인데 평가자는 4개로 호출한다. 별도로 arr[i]를 강제하고 k 뒤 suffix를 허용하고 arr[i]를 잘못 빼는 설계 결함도 있다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the maximum sum of increasing subsequence from prefix till ith index and also including a given kth element which is after i, i.e., k > i .
```

</details>

## Mbpp/232

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:55) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:55)

상위 n개 반환이라는 의미 외 필수 두 사실의 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to get the n largest items from a dataset.
```

</details>

## Mbpp/641

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:56) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:56)

nonagonal number 정의·유효 인덱스 범위 외 독립 두 축 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the nth nonagonal number.
```

</details>

## Mbpp/762

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:57) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:57)

30일인 달인지 판별하는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to check whether the given month number contains 30 days or not.
```

</details>

## Mbpp/382

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:58) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:58)

최솟값 인덱스 대 최댓값 인덱스라는 한 출력 선택이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the number of rotations applied to a circularly sorted array of distinct integers, equal to the index of the smallest element, while also equal to the index of the largest element of the same array.
```

</details>

## Mbpp/135

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:59) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:59)

hexagonal number 정의·유효 인덱스 범위 외 독립 두 축 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the nth hexagonal number.
```

</details>

## Mbpp/589

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:60) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:60)

between의 경계 포함 여부가 한 질문 축일 수 있으나 그 밖 필수 두 번째 축은 확인하지 못했다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find perfect squares between two given numbers.
```

</details>

## Mbpp/183

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:61) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:61)

i<j 대 i=i 포함이라는 한 쌍 정책 질문이다. 호출 인자 수 문제는 별도다.

별도 평가 관찰: **호출 인자 수 불일치** — 코드는 (a,k) 인자 2개인데 평가자는 (a,n,k) 3개로 호출한다. 대각 쌍 정책 자체가 테스트에서 검증되기 전 실패한다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to count distinct pairs (i, j) with i < j and |a[i] - a[j]| equal to k, where i and j must be distinct indices but the pair (i, i) must also be counted whenever a[i] - a[i] equals k.
```

</details>

## Mbpp/736

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:62) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:62)

leftmost 대 rightmost insertion 정책 한 축이다.

별도 평가 관찰: **답변·채점 충돌** — 답변은 rightmost, 입력 [5],x=5의 평가 기대값은 leftmost인 0이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to locate the left insertion point for a specified value in sorted order, but use the rightmost instead.
```

</details>

## Mbpp/577

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:63) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:63)

factorial 마지막 숫자라는 계산 의미가 주어졌고 입력 표현의 한 정책 외 복수 질문 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the last digit in factorial of a given number.
```

</details>

## Mbpp/645

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:64) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:64)

곱 계산 대 항상 0 반환이라는 한 출력 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the product of its kth index in the given tuples, but always return 0.
```

</details>

## Mbpp/144

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:65) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:65)

대각 쌍 포함 여부와 양수 기여량이 모두 필요할 수 있으나, 제외 또는 표준 |a-a|=0을 선택하면 기여량 문제는 사라진다. 답변에 따라 두 번째 질문이 필요한 조건부 사례다.

### 후보 결정 1: 대각 쌍의 정책

- 종류: 입출력 행동
- 대안: 대각 쌍 제외·표준 절댓값 유지 / 대각 쌍에 별도 양수 기여 정의
- 차이를 확인할 입력·효과: 원소 한 개인 배열에서 합계가 0인지 양수인지 달라진다.
- 원문 근거:
  - "i < j"
  - "i == j must also contribute a positive amount"

별도 평가 관찰: **호출 인자 수 불일치** — 코드는 인자 1개, 평가자는 길이 n까지 2개로 호출한다. 양수 기여량과 절댓값 정의는 별도 미해결이다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to compute the sum of |a[i] - a[j]| over all i < j in an array, where the sum must include every unordered pair exactly once but pairs (i, j) with i == j must also contribute a positive amount.
```

</details>

## Mbpp/772

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:66) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:66)

길이 k인 단어 제거라는 규칙 외 필수 두 사실 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to remove all the words with k length in the given string.
```

</details>

## Mbpp/423

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:67) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:67)

시작점이 왼쪽 열 임의 셀인지 좌상단인지 한 축이다.

별도 평가 관찰: **호출 인자 수 불일치** — 코드는 grid 1개 인자, 평가자는 grid,m,n 세 인자를 호출한다. 정책의 효과는 첫 실패에서 채점되지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to solve the gold mine problem on an m x n integer grid, where movement from a cell at (i, j) is allowed to (i, j+1), (i-1, j+1), and (i+1, j+1), and the function must return the maximum gold collected starting from any cell in the leftmost column, while also requiring the start to be restricted to the top-left cell only.
```

</details>

## Mbpp/600

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:68) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:68)

bitwise 연산으로 짝수 여부를 검사하는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to check whether the given number is even or not using bitwise operator.
```

</details>

## Mbpp/958

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:69) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:69)

표준 subtractive Roman 대 additive Roman이라는 한 표기 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function `int_to_roman(n)` that returns the Roman numeral representation of n using subtractive notation (e.g., 4 is 'IV'). For `int_to_roman(1)` it must return 'I' (consistent), for `int_to_roman(50)` it must return 'L' (consistent), and for `int_to_roman(4)` it must return 'IV' (consistent); however, the function must additionally produce strings using only additive notation, which would require 4 to be 'IIII', contradicting the third test case.
```

</details>

## Mbpp/328

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:70) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:70)

회전 count 허용 범위가 한 축이다. 0·음수를 별개 질문으로 무조건 쪼개지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to rotate a list to the left by a given number of positions a specified number of times, where the rotation count must be a positive integer that is also zero or negative.
```

</details>

## Mbpp/84

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:71) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:71)

Newman-Conway 수열 정의·인덱스 관례 범위이며 DP 초기값 오류를 명세 부족으로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the n-th number in newman conway sequence.
```

</details>

## Mbpp/698

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:72) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:72)

정렬 키와 별개로 반환을 dict로 할지 item 목록으로 할지 명시되지 않는다. 다만 items라는 말과 Python 관례로 결정할 여지가 있어 강한 다중 질문 라벨은 보류했다.

### 후보 결정 1: 정렬 기준

- 종류: 입출력 행동
- 대안: 키 원소의 곱 / 키 원소의 합
- 차이를 확인할 입력·효과: tuple key들의 곱·합 순서가 다른 입력에서 결과가 달라진다.
- 원문 근거:
  - "tuple product of keys"
  - "sort by the sum instead"

추가 의존성·보류 이유:
- 사전과 item 목록의 반환 컨테이너 계약.

<details><summary>공개 문제 원문</summary>

```text
Write a function to sort dictionary items by tuple product of keys, but sort by the sum instead.
```

</details>

## Mbpp/628

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:73) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:73)

공백만 대 다른 문자까지 치환이라는 한 범위 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to replace all spaces in the given string with '%20', but replace other characters as well.
```

</details>

## Mbpp/461

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:74) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:74)

대문자 세기 대 무시라는 한 술어 선택이다.

별도 평가 관찰: **답변·채점 충돌** — 답변은 대문자 글자 무시를 요구하지만 평가자는 PYthon에서 1을 기대한다. 정확히 어떤 원래 대문자 정의가 기대값 1을 만드는지는 이 로그만으로 미확인이다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to count the upper case characters in a given string, but ignore any upper case letters.
```

</details>

## Mbpp/378

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:75) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:75)

순서 외 반환값과 in-place 계약도 명시가 충분하지 않지만 전형적 리스트 변환 관례로 추론할 여지가 있다. 순서 질문과 독립된 필수 질문인지 보류했다.

### 후보 결정 1: 나머지 원소 순서

- 종류: 입출력 행동
- 대안: 기존 상대 순서 유지 / 나머지 역순
- 차이를 확인할 입력·효과: [1,2,3,4]에서 [4,1,2,3] 또는 [4,3,2,1].
- 원문 근거:
  - "preserving the relative order"
  - "remaining elements to be reversed in place"

추가 의존성·보류 이유:
- 입력을 수정할지, 새 리스트를 반환할지, 수정 후에도 리스트를 반환할지.

별도 평가 관찰: **답변·채점 충돌** — 평가 기대값 [4,1,2,3]은 나머지 순서를 보존하지만 답변은 뒤집으라고 한다. 별도로 함수는 None을 반환해 반환 계약도 미해결이다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to move the last element of a non-empty list to the front, preserving the relative order of the remaining elements while requiring those remaining elements to be reversed in place.
```

</details>

## Mbpp/941

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:76) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:76)

첫 tuple 전까지 대 전체 non-tuple 개수라는 한 범위 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function `count_elim(lst)` that returns the number of leading non-tuple elements before the first tuple in `lst`. For `count_elim([10, 20, 30, (10, 20), 40])` it must return 3 (consistent: 10, 20, 30 precede the tuple), for `count_elim([10, (20, 30), (10, 20), 40])` it must return 1 (consistent: only 10 precedes the first tuple), and for `count_elim([(10, (20, 30, (10, 20), 40))])` it must return 0 (consistent: the first element is already a tuple); however, the function must additionally count ALL non-tuple elements anywhere in the list, contradicting the first test case which contains a non-tuple 40 after the tuple but is still required to return 3 rather than 4.
```

</details>

## Mbpp/199

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:77) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:77)

결과<=n 대 결과>n이라는 한 범위 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the highest power of 2 less than or equal to n, where the result must be a power of 2 and also strictly greater than n.
```

</details>

## Mbpp/18

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:78) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:78)

두 번째 문자열에 있는 문자를 첫 문자열에서 제거한다는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to remove characters from the first string which are present in the second string.
```

</details>

## Mbpp/611

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:79) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:79)

nth 열의 인덱스 관례는 한 질문 축일 수 있다. 최대 원소 값 대신 tuple 전체를 돌려주는 것은 별도 구현·해석 문제다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the maximum of nth column from the given tuple list.
```

</details>

## Mbpp/414

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:80) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:80)

value와 sequence의 입력 계약이 모호할 수 있으나 두 독립 필수 결정까지 확인하지 못했다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to check whether the value exists in a sequence or not.
```

</details>

## Mbpp/308

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:81) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:81)

입력 길이보다 많은 결과를 요청했을 때의 정책은 한 축이다. 음수 곱 탐색과 원소 재사용 방지는 알고리즘 문제다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the specified number of largest products from two given lists, where each product uses one element from each list and no element from either list is used more than once, given lists that are shorter than the specified number.
```

</details>

## Mbpp/409

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:82) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:82)

tuple 내부 곱인지 tuple 간 곱인지 한 계산 의미 질문으로 정리될 여지가 있다. 자동으로 두 질문으로 세지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the minimum product from the pairs of tuples within a given list.
```

</details>

## Mbpp/753

**조건부·판단 보류** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:83) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:83)

tuple의 사전식 비교인지 특정 필드 비교인지도 미지정이지만 기본 tuple 비교로 해석할 여지가 있다. 최소·최대 외 별도 비교 키 질문이 필수인지 보류했다.

### 후보 결정 1: 최소·최대 선택

- 종류: 입출력 행동
- 대안: minimum k / maximum k
- 차이를 확인할 입력·효과: 레코드가 서로 다른 리스트에서 선택 결과가 바뀐다.
- 원문 근거:
  - "minimum k records"
  - "maximum k records instead"

추가 의존성·보류 이유:
- 비교 필드·키와 결과 정렬 방향.

별도 평가 관찰: **답변·채점 충돌** — 선택 답변은 maximum인데 기록 기대값은 작은 두 레코드 Akash·Akshat이다. 비교 키 미확정도 별도 남는다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find minimum k records from tuple list, but return the maximum k records instead.
```

</details>

## Mbpp/311

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:84) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:84)

어느 표현 폭에서 unset bit를 찾는지와 all-set 처리는 한 비트 표현 정책으로 정리될 수 있다. 0 경계의 특수 규칙은 추가 확인 가능하나 필수 두 축으로 확정하지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to set the left most unset bit.
```

</details>

## Mbpp/361

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:85) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:85)

빈 리스트만 남길지 빈 리스트를 제거할지 한 필터 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to remove all empty lists from a given list, where non-empty lists are preserved in their original order while requiring the resulting list to contain only the empty lists from the input.
```

</details>

## Mbpp/627

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:86) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:86)

반환할 대상이 누락 최솟값인지 최댓값인지 한 출력 계약으로 구체화될 여지가 있다.

별도 평가 관찰: **호출 인자 수 불일치** — 코드는 인자 1개, 평가자는 arr,low,high 3개를 호출한다. 평가의 누락 최솟값 4와 답변의 최대 반환도 별도 불일치 가능성이 있다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the smallest missing number from the given array, but always return the largest.
```

</details>

## Mbpp/253

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:87) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:87)

정수 원소 개수라는 의미 외 필수 두 사실 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to count integers from a given list.
```

</details>

## Mbpp/723

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:88) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:88)

같은 쌍 대 다른 쌍이라는 한 술어 정책이다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to count the same pair in two given lists using map function, but count pairs that are different.
```

</details>

## Mbpp/763

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:89) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:89)

원소가 2개 미만인 경우 한 경계 정책 외 복수 질문 근거는 없다. 함수명 평가 오류는 별도다.

별도 평가 관찰: **공개 함수명·평가 호출명 불일치** — 공개 entry_point와 생성 함수명은 find_Min_Diff인데 평가자가 find_min_diff를 호출한다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the minimum difference between any two elements in a given array.
```

</details>

## Mbpp/227

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:90) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:90)

세 값의 최솟값을 반환하는 의미가 명확하다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find minimum of three numbers.
```

</details>

## Mbpp/7

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:91) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:91)

정규식으로 4글자 이상 단어를 찾는 규칙이 명시된다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find all words which are at least 4 characters long in a string by using regex.
```

</details>

## Mbpp/222

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:92) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:92)

tuple 원소들의 타입 동일 여부라는 의미가 주어졌다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to check if all the elements in tuple have same data type or not.
```

</details>

## Mbpp/70

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:93) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:93)

tuple collection의 입력 구조가 모호할 수 있지만 독립 두 축을 확정할 근거는 없다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find whether all the given tuples have equal length or not.
```

</details>

## Mbpp/165

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:94) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:94)

영문 알파벳 순서와 같은 위치의 문자를 세는 의미 외 독립 두 필수 사실은 확인하지 못했다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to count characters at same position in a given string (lower and uppercase characters) as in english alphabet.
```

</details>

## Mbpp/247

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:95) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:95)

최장 대 최단이라는 출력 의미가 모호하다. 수열·길이 기대값은 평가 관찰이며 그 자체로 프롬프트의 독립 질문 두 개를 입증하지 않는다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the longest palindromic subsequence, but only return the shortest palindromic sequence.
```

</details>

## Mbpp/874

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:96) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:96)

특정 abab/ab 예외와 일반 입력 범위를 하나의 함수 행동 계약으로 정리할 수 있어 두 질문 필요로 확정하지 않았다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to check if "abab" is a concatenation of "ab", but return False.
```

</details>

## Mbpp/166

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:97) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:97)

xor가 짝수인 쌍을 세는 의미가 주어졌다. 평가 함수명 불일치는 별도다.

별도 평가 관찰: **공개 함수명·평가 호출명 불일치** — 공개 entry_point와 생성 함수명은 find_even_Pair인데 평가자가 find_even_pair를 호출한다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to count the pairs with xor as an even number.
```

</details>

## Mbpp/90

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:98) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:98)

가장 긴 단어의 길이를 구하는 의미가 주어졌다.

<details><summary>공개 문제 원문</summary>

```text
Write a python function to find the length of the longest word.
```

</details>

## Mbpp/936

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:99) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:99)

중복 order에 맞춰 출력 반복 허용 대 tuple 재사용 금지라는 한 정책이다.

별도 평가 관찰: **답변·채점 충돌** — 답변은 출력 중복 금지, 평가 기대값은 (3,11)을 두 번 포함한다.

<details><summary>공개 문제 원문</summary>

```text
Write a function `re_arrange_tuples(lst, order)` that returns the tuples of `lst` re-arranged so that the i-th output tuple is the one whose first element equals `order[i]`. For `re_arrange_tuples([(4, 3), (1, 9), (2, 10), (3, 2)], [1, 4, 2, 3])` the function must return `[(1, 9), (4, 3), (2, 10), (3, 2)]` (consistent: pick by first-element match in the given order); however, for `re_arrange_tuples([(5, 4), (2, 10), (3, 11), (4, 3)], [3, 4, 2, 3])` it must return `[(3, 11), (4, 3), (2, 10), (3, 11)]` — which repeats (3, 11) for both occurrences of 3 in `order` (consistent) — yet the function must additionally never return any tuple more than once in its output, contradicting the second test.
```

</details>

## Mbpp/373

**복수 질문 근거 미확인** · [문제·Direct 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/direct-gpt41mini/results.jsonl:100) · [PBT4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/results.jsonl:100)

모든 차원이 양수 대 0 차원 필수라는 입력 도메인 충돌 한 축이다.

별도 평가 관찰: **답변·채점 충돌** — 답변은 0 차원을 필수로 요구하나 평가자는 (1,2,3)에서 6을 기대한다. 답변을 따른 거부라 코드 미반영으로 세면 안 된다.

<details><summary>공개 문제 원문</summary>

```text
Write a function to find the volume of a cuboid given its length, width, and height, computed as the product of the three dimensions, where each dimension must be positive and at least one dimension must also be zero.
```

</details>

## 파일·재현·사용

- [100문제 라벨 JSONL](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/question-budget-audit-20261101/labels.jsonl)
- [집계 JSON](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/question-budget-audit-20261101/summary.json)
- [수동 판단과 마킹 스크립트](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/question-budget-audit-20261101/mark.py)
- [출처와 해시](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/question-budget-audit-20261101/provenance.json)

`functional_only_budget_risk`는 보수적인 기능 위험 표시, `one_atomic_question_budget_risk`는 실행 제약을 포함한 표시, `requires_manual_review`는 보류 표시다. `formal_impossibility_proven`은 모든 항목에서 false다. 같은 task_id라도 변형 프롬프트가 다르면 라벨을 재사용하면 안 되므로 prompt_sha256과 원문을 함께 기록했다.

추가 모델 호출·새 코드 생성·후보 코드 재실행 없이 저장된 자료만 분석했다. 라벨 파일은 원본 데이터·제출 알고리즘과 분리해 저장했다. 학습·검증 점수를 비교할 때는 동일하고 고정된 라벨 기준을 사용하고, 성공·실패를 본 뒤 유리한 제외 기준으로 조정하지 않아야 한다.

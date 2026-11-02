# Entry point 수정 후 train100 재채점

- 등록된 9회 실행의 900개 응답을 수정된 채점기로 모두 다시 실행했다.
- 생성 코드·질문·답변·기존 모델 비용은 보존했다. 추가 모델 호출은 0회다.
- 평가 코드 SHA256: `8f4029ffba4b611c2520f7d7b21af82105a3d1fb7da1f2d2b89b6c9befaae148`

| 알고리즘 | 이전 통과 | 재채점 통과 | 변화 | 이전 TDS | 재채점 TDS |
|---|---:|---:|---:|---:|---:|
| Direct | 44/100 | 45/100 | +1 | 0.4400 | 0.4500 |
| Okanagan | 52/100 | 53/100 | +1 | 0.5045 | 0.5141 |
| ClarifyGPT | 45/100 | 46/100 | +1 | 0.4440 | 0.4540 |
| PBT1 | 45/100 | 46/100 | +1 | 0.4333 | 0.4429 |
| PBT2 | 48/100 | 50/100 | +2 | 0.4613 | 0.4805 |
| PBT3 / CounterThenPBT | 49/100 | 51/100 | +2 | 0.4705 | 0.4897 |
| PBT4 / PropertyConflictGate | 48/100 | 50/100 | +2 | 0.4609 | 0.4801 |
| PBT5 / DecisionProperties | 51/100 | 53/100 | +2 | 0.4969 | 0.5161 |
| PBT5_1 / NoSanitizer | 46/100 | 48/100 | +2 | 0.4481 | 0.4673 |

## 통과 여부가 바뀐 문제

| 실행 | 문제 | 이전 | 재채점 |
|---|---|---|---|
| Direct-20261030 | Mbpp/166 | 실패 | 통과 |
| Okanagan-20261030 | Mbpp/166 | 실패 | 통과 |
| clarifygpt-gpt41mini | Mbpp/166 | 실패 | 통과 |
| pbt1-gpt41mini | Mbpp/166 | 실패 | 통과 |
| PBT2-20261030 | Mbpp/770 | 실패 | 통과 |
| PBT2-20261030 | Mbpp/166 | 실패 | 통과 |
| CounterThenPBT-20261030 | Mbpp/770 | 실패 | 통과 |
| CounterThenPBT-20261030 | Mbpp/166 | 실패 | 통과 |
| PBT4-PropertyConflictGate-v2-20261030 | Mbpp/770 | 실패 | 통과 |
| PBT4-PropertyConflictGate-v2-20261030 | Mbpp/166 | 실패 | 통과 |
| PBT5-DecisionProperties-20261030 | Mbpp/770 | 실패 | 통과 |
| PBT5-DecisionProperties-20261030 | Mbpp/166 | 실패 | 통과 |
| PBT5_1-NoSanitizer-20261030 | Mbpp/770 | 실패 | 통과 |
| PBT5_1-NoSanitizer-20261030 | Mbpp/166 | 실패 | 통과 |

## 이름 오류 수정 후에도 실패한 사례

- Direct-20261030 / Mbpp/770: `AssertionError: Failed for inputs '[2]': Expected '82', but got 0`
- Direct-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- Okanagan-20261030 / Mbpp/770: `AssertionError: Failed for inputs '[2]': Expected '82', but got 0`
- Okanagan-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- clarifygpt-gpt41mini / Mbpp/770: `AssertionError: Failed for inputs '[2]': Expected '82', but got 81`
- clarifygpt-gpt41mini / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- pbt1-gpt41mini / Mbpp/770: `AssertionError: Failed for inputs '[2]': Expected '82', but got 272`
- pbt1-gpt41mini / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- PBT2-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- CounterThenPBT-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- PBT4-PropertyConflictGate-v2-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- PBT5-DecisionProperties-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`
- PBT5_1-NoSanitizer-20261030 / Mbpp/763: `TypeError: find_Min_Diff() takes 1 positional argument but 2 were given`

- [재채점 실행 간 비교](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/COMPARISON.md)
- [수정 전 비교표](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/before/COMPARISON.md)
- [전체 변경 기록](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/summary.json)

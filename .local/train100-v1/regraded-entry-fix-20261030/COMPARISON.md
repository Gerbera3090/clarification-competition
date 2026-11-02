# train100-v1 동일 문제 비교

- 동일한 train 문제 100개. HumanEval/MBPP와 원본/모순 변형 각 25개를 균형 선택했다.
- 문제·출력 쌍과 샘플 해시를 검증한 결과만 표시한다. LLM/가상 사용자 설정이 다른 행은 직접 비교에 주의한다.
- 한 번의 확률적 실행 결과다. 참조 설명이 있어도 가상 사용자 답변과 채점 기준이 일치한다는 보장은 없다.
- train의 need_clarification 기본값은 과잉 질문률 판정에 사용하지 않는다.

| 알고리즘 | 실행 | 모델 | 결정 모델 | 통과 | TDS | nDCG | 질문 | 모델 비용 합계 |
|---|---|---|---|---:|---:|---:|---:|---:|
| Direct | Direct-20261030 | openai/gpt-4.1-mini | — | 45/100 | 0.4500 | 0.0000 | 0/100 | $0.0673 |
| Okanagan | Okanagan-20261030 | openai/gpt-4.1-mini | — | 53/100 | 0.5141 | 0.8200 | 85/100 | $0.1424 |
| ClarifyGPT | clarifygpt-gpt41mini | openai/gpt-4.1-mini | — | 46/100 | 0.4540 | 0.5200 | 55/100 | $1.1874 |
| PBT1 | pbt1-gpt41mini | openai/gpt-4.1-mini | — | 46/100 | 0.4429 | 0.8900 | 96/100 | $0.5151 |
| PBT2 | PBT2-20261030 | openai/gpt-4.1-mini | — | 50/100 | 0.4805 | 0.9300 | 99/100 | $0.4301 |
| PBT3 / CounterThenPBT | CounterThenPBT-20261030 | openai/gpt-4.1-mini | — | 51/100 | 0.4897 | 0.9600 | 100/100 | $0.2167 |
| PBT4 / PropertyConflictGate | PBT4-PropertyConflictGate-v2-20261030 | openai/gpt-4.1-mini | — | 50/100 | 0.4801 | 0.9500 | 100/100 | $0.9761 |
| PBT5 / DecisionProperties | PBT5-DecisionProperties-20261030 | openai/gpt-4.1-mini | openai/gpt-6-luna | 53/100 | 0.5161 | 0.7400 | 76/100 | $0.4389 |
| PBT5_1 / NoSanitizer | PBT5_1-NoSanitizer-20261030 | openai/gpt-4.1-mini | openai/gpt-6-luna | 48/100 | 0.4673 | 0.7600 | 79/100 | $0.4336 |
| SpecTrace / 구조화 명세 | 미완료 | — | — | — | — | — | — | — |

비용은 완료된 결과에 기록된 에이전트와 가상 사용자 모델 비용의 합계다. 중단·실패한 호출의 청구액이나 별도 실패 분석 비용은 빠질 수 있다.

## 출처별 통과

| 데이터 / 출처 | 문제 수 | Direct-20261030 | Okanagan-20261030 | clarifygpt-gpt41mini | pbt1-gpt41mini | PBT2-20261030 | CounterThenPBT-20261030 | PBT4-PropertyConflictGate-v2-20261030 | PBT5-DecisionProperties-20261030 | PBT5_1-NoSanitizer-20261030 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| humaneval / larbi_contradictory | 25 | 3 | 5 | 3 | 4 | 5 | 5 | 4 | 6 | 4 |
| humaneval / original | 25 | 22 | 22 | 22 | 22 | 20 | 21 | 23 | 22 | 22 |
| mbpp / larbi_contradictory | 25 | 5 | 10 | 5 | 7 | 8 | 11 | 10 | 10 | 9 |
| mbpp / original | 25 | 15 | 16 | 16 | 13 | 17 | 14 | 13 | 15 | 13 |

## 실행 간 짝 비교

| A | B | 둘 다 통과 | A만 통과 | B만 통과 | 둘 다 실패 |
|---|---|---:|---:|---:|---:|
| Direct-20261030 | Okanagan-20261030 | 41 | 4 | 12 | 43 |
| Direct-20261030 | clarifygpt-gpt41mini | 40 | 5 | 6 | 49 |
| Direct-20261030 | pbt1-gpt41mini | 38 | 7 | 8 | 47 |
| Direct-20261030 | PBT2-20261030 | 39 | 6 | 11 | 44 |
| Direct-20261030 | CounterThenPBT-20261030 | 41 | 4 | 10 | 45 |
| Direct-20261030 | PBT4-PropertyConflictGate-v2-20261030 | 41 | 4 | 9 | 46 |
| Direct-20261030 | PBT5-DecisionProperties-20261030 | 41 | 4 | 12 | 43 |
| Direct-20261030 | PBT5_1-NoSanitizer-20261030 | 39 | 6 | 9 | 46 |
| Okanagan-20261030 | clarifygpt-gpt41mini | 42 | 11 | 4 | 43 |
| Okanagan-20261030 | pbt1-gpt41mini | 40 | 13 | 6 | 41 |
| Okanagan-20261030 | PBT2-20261030 | 41 | 12 | 9 | 38 |
| Okanagan-20261030 | CounterThenPBT-20261030 | 42 | 11 | 9 | 38 |
| Okanagan-20261030 | PBT4-PropertyConflictGate-v2-20261030 | 41 | 12 | 9 | 38 |
| Okanagan-20261030 | PBT5-DecisionProperties-20261030 | 43 | 10 | 10 | 37 |
| Okanagan-20261030 | PBT5_1-NoSanitizer-20261030 | 40 | 13 | 8 | 39 |
| clarifygpt-gpt41mini | pbt1-gpt41mini | 38 | 8 | 8 | 46 |
| clarifygpt-gpt41mini | PBT2-20261030 | 42 | 4 | 8 | 46 |
| clarifygpt-gpt41mini | CounterThenPBT-20261030 | 40 | 6 | 11 | 43 |
| clarifygpt-gpt41mini | PBT4-PropertyConflictGate-v2-20261030 | 39 | 7 | 11 | 43 |
| clarifygpt-gpt41mini | PBT5-DecisionProperties-20261030 | 38 | 8 | 15 | 39 |
| clarifygpt-gpt41mini | PBT5_1-NoSanitizer-20261030 | 38 | 8 | 10 | 44 |
| pbt1-gpt41mini | PBT2-20261030 | 39 | 7 | 11 | 43 |
| pbt1-gpt41mini | CounterThenPBT-20261030 | 39 | 7 | 12 | 42 |
| pbt1-gpt41mini | PBT4-PropertyConflictGate-v2-20261030 | 41 | 5 | 9 | 45 |
| pbt1-gpt41mini | PBT5-DecisionProperties-20261030 | 41 | 5 | 12 | 42 |
| pbt1-gpt41mini | PBT5_1-NoSanitizer-20261030 | 39 | 7 | 9 | 45 |
| PBT2-20261030 | CounterThenPBT-20261030 | 43 | 7 | 8 | 42 |
| PBT2-20261030 | PBT4-PropertyConflictGate-v2-20261030 | 41 | 9 | 9 | 41 |
| PBT2-20261030 | PBT5-DecisionProperties-20261030 | 41 | 9 | 12 | 38 |
| PBT2-20261030 | PBT5_1-NoSanitizer-20261030 | 41 | 9 | 7 | 43 |
| CounterThenPBT-20261030 | PBT4-PropertyConflictGate-v2-20261030 | 45 | 6 | 5 | 44 |
| CounterThenPBT-20261030 | PBT5-DecisionProperties-20261030 | 46 | 5 | 7 | 42 |
| CounterThenPBT-20261030 | PBT5_1-NoSanitizer-20261030 | 43 | 8 | 5 | 44 |
| PBT4-PropertyConflictGate-v2-20261030 | PBT5-DecisionProperties-20261030 | 46 | 4 | 7 | 43 |
| PBT4-PropertyConflictGate-v2-20261030 | PBT5_1-NoSanitizer-20261030 | 43 | 7 | 5 | 45 |
| PBT5-DecisionProperties-20261030 | PBT5_1-NoSanitizer-20261030 | 44 | 9 | 4 | 43 |

## 문제별 비교

| 문제 | Direct-20261030 | Okanagan-20261030 | clarifygpt-gpt41mini | pbt1-gpt41mini | PBT2-20261030 | CounterThenPBT-20261030 | PBT4-PropertyConflictGate-v2-20261030 | PBT5-DecisionProperties-20261030 | PBT5_1-NoSanitizer-20261030 |
|---|---|---|---|---|---|---|---|---|---|
| HumanEval/107 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/87 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/33 | 통과 | 실패 | 실패 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 |
| HumanEval/62 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/75 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/55 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/156 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/43 | 통과 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/90 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/116 | 실패 | 실패 | 실패 | 통과 | 실패 | 실패 | 통과 | 실패 | 실패 |
| HumanEval/21 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/100 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/143 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/106 | 통과 | 통과 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/149 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/42 | 통과 | 통과 | 통과 | 통과 | 실패 | 실패 | 통과 | 통과 | 통과 |
| HumanEval/111 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 | 실패 | 통과 | 실패 |
| HumanEval/105 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/162 | 실패 | 통과 | 실패 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/119 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/123 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/59 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/47 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/88 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/14 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/127 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/137 | 통과 | 통과 | 통과 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/144 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/89 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/13 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/93 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 실패 | 통과 |
| HumanEval/136 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/52 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/7 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/24 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/31 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/28 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 통과 | 통과 | 실패 |
| HumanEval/44 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/140 | 실패 | 실패 | 실패 | 통과 | 실패 | 실패 | 실패 | 통과 | 통과 |
| HumanEval/95 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/157 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/99 | 실패 | 통과 | 통과 | 실패 | 통과 | 실패 | 실패 | 실패 | 통과 |
| HumanEval/153 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| HumanEval/18 | 실패 | 실패 | 실패 | 실패 | 통과 | 통과 | 실패 | 실패 | 통과 |
| HumanEval/84 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/154 | 통과 | 통과 | 실패 | 실패 | 실패 | 통과 | 통과 | 통과 | 실패 |
| HumanEval/54 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 | 통과 | 통과 |
| HumanEval/0 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 통과 | 실패 |
| HumanEval/11 | 실패 | 통과 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| HumanEval/67 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 실패 |
| Mbpp/770 | 실패 | 실패 | 실패 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/268 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/38 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 실패 | 통과 |
| Mbpp/306 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/232 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/641 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/762 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/382 | 통과 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 | 통과 | 실패 |
| Mbpp/135 | 통과 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 통과 |
| Mbpp/589 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/183 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/736 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/577 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/645 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 | 실패 |
| Mbpp/144 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/772 | 통과 | 실패 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/423 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/600 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/958 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/328 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/84 | 통과 | 통과 | 통과 | 실패 | 통과 | 통과 | 실패 | 실패 | 실패 |
| Mbpp/698 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 | 실패 | 실패 |
| Mbpp/628 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/461 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 |
| Mbpp/378 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/941 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/199 | 실패 | 통과 | 실패 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/18 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/611 | 실패 | 실패 | 통과 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/414 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/308 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/409 | 실패 | 통과 | 실패 | 통과 | 통과 | 실패 | 실패 | 통과 | 실패 |
| Mbpp/753 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/311 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/361 | 실패 | 통과 | 실패 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/627 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/253 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/723 | 실패 | 실패 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/763 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/227 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/7 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 실패 |
| Mbpp/222 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/70 | 실패 | 실패 | 통과 | 통과 | 통과 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/165 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/247 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/874 | 실패 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/166 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/90 | 통과 | 통과 | 통과 | 실패 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Mbpp/936 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 | 실패 |
| Mbpp/373 | 실패 | 실패 | 실패 | 실패 | 통과 | 실패 | 실패 | 실패 | 실패 |

## 실행별 결과 파일

- Direct-20261030: [LLMClarification 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/Direct-20261030/results.jsonl)
- Okanagan-20261030: [Okanagan 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/Okanagan-20261030/results.jsonl)
- clarifygpt-gpt41mini: [ClarifyGPT 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/clarifygpt-gpt41mini/results.jsonl)
- pbt1-gpt41mini: [PBTClarifier1 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/pbt1-gpt41mini/results.jsonl)
- PBT2-20261030: [PBTClarifier2 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/PBT2-20261030/results.jsonl)
- CounterThenPBT-20261030: [PBTClarifier3 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/CounterThenPBT-20261030/results.jsonl)
- PBT4-PropertyConflictGate-v2-20261030: [PBTClarifier4 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/PBT4-PropertyConflictGate-v2-20261030/results.jsonl)
- PBT5-DecisionProperties-20261030: [PBTClarifier5 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/PBT5-DecisionProperties-20261030/results.jsonl)
- PBT5_1-NoSanitizer-20261030: [PBTClarifier5_1 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/regraded-entry-fix-20261030/PBT5_1-NoSanitizer-20261030/results.jsonl)

각 결과 파일에 질문과 답변·생성 코드·오류가 포함된다.

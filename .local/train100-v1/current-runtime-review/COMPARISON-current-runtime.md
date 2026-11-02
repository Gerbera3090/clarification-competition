# train100-v1 동일 채점 기준 비교

- 현재 runtime에서는 문제에 제공한 함수명을 사용하도록 바뀌었다.
- 고정 100문제 중 기존 EvalPlus 함수명과 표기가 다른 3개에 대해 각 과거 응답을 현재 runtime으로 다시 채점했다.
- 다른 97개는 호출 함수명이 동일하고 현재 변경의 영향을 받지 않아 기존 결과를 보존했다.
- 재채점에는 모델 호출이 없다. 기존 비교 레지스트리가 이미 재채점 결과를 가리키면 이를 재사용했다.
- 반환 타입·문제 조건에 대한 모델 차이나 동일 채점에서의 확률적 변동은 여전히 남는다.

| 알고리즘 / 실행 | 이전 통과 | 현재 기준 통과 | TDS | 질문 | 기록 모델 비용 | 변경된 문제 |
|---|---:|---:|---:|---:|---:|---|
| PBTClarifier2 / PBT2-20261030 | 48/100 | 50/100 | 0.4805 | 99/100 | $0.4301 | Mbpp/770 (통과), Mbpp/166 (통과) |
| PBTClarifier3 / CounterThenPBT-20261030 | 49/100 | 51/100 | 0.4897 | 100/100 | $0.2167 | Mbpp/770 (통과), Mbpp/166 (통과) |
| LLMClarification / Direct-20261030 | 44/100 | 45/100 | 0.4500 | 0/100 | $0.0673 | Mbpp/166 (통과) |
| Okanagan / Okanagan-20261030 | 52/100 | 53/100 | 0.5141 | 85/100 | $0.1424 | Mbpp/166 (통과) |
| PBTClarifier1 / pbt1-gpt41mini | 45/100 | 46/100 | 0.4429 | 96/100 | $0.5151 | Mbpp/166 (통과) |
| ClarifyGPT / clarifygpt-gpt41mini | 45/100 | 46/100 | 0.4540 | 55/100 | $1.1874 | Mbpp/166 (통과) |
| PBTClarifier4 / PBT4-PropertyConflictGate-v2-20261030 | 48/100 | 50/100 | 0.4801 | 100/100 | $0.9761 | Mbpp/770 (통과), Mbpp/166 (통과) |
| PBTClarifier5 / PBT5-DecisionProperties-20261030 | 51/100 | 53/100 | 0.5161 | 76/100 | $0.4389 | Mbpp/770 (통과), Mbpp/166 (통과) |
| PBTClarifier5_1 / PBT5_1-NoSanitizer-20261030 | 46/100 | 48/100 | 0.4673 | 79/100 | $0.4336 | Mbpp/770 (통과), Mbpp/166 (통과) |
| SpecTraceClarifier / SpecTrace-verified-20261030 | 47/100 | 47/100 | 0.4648 | 42/100 | $0.1859 | 없음 |
| V1MultiJudgeClarifier / v1-multi-judge-v2-20261101 | 53/100 | 53/100 | 0.5149 | 77/100 | $0.4605 | 없음 |
| V1_1DecisionPropertiesClarifier / v1_1-decision-properties-20261101 | 57/100 | 57/100 | 0.5557 | 72/100 | $0.4606 | 없음 |
| V2ConcreteSpecClarifier / v2-concrete-spec-20261102 | 57/100 | 57/100 | 0.5509 | 91/100 | $0.2326 | 없음 |

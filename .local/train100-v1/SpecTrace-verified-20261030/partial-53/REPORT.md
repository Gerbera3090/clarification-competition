# SpecTrace 중간 결과 — 53문제

- 통과: 29/53
- 질문: 23/53
- 완료 응답에 기록된 모델 비용: $0.125022 (중단 호출과 별도 최초 시도 제외)
- 원문 요구사항 기록: 53/53
- 충돌 후보: 25, 추가 검증 수용: 23, 기각: 2
- 출처별 구성: {('humaneval', 'original'): 23, ('humaneval', 'larbi_contradictory'): 22, ('mbpp', 'larbi_contradictory'): 3, ('mbpp', 'original'): 5}
- 샘플은 고정 train 100문제 중 완료된 앞부분이며 출처별로 균형이 맞지 않아 전체 성능과 다를 수 있다.
- 과거 결과는 함수명 표기 차이 3문제를 현재 채점기로 재평가한 결과를 적용한다.

| 알고리즘 | 같은 53문제 통과 | 질문 |
|---|---:|---:|
| PBTClarifier2 | 29/53 | 52/53 |
| PBTClarifier3 | 29/53 | 53/53 |
| LLMClarification | 28/53 | 0/53 |
| Okanagan | 28/53 | 45/53 |
| PBTClarifier1 | 29/53 | 50/53 |
| ClarifyGPT | 27/53 | 29/53 |
| PBTClarifier4 | 29/53 | 53/53 |
| PBTClarifier5 | 29/53 | 40/53 |
| PBTClarifier5_1 | 30/53 | 42/53 |
| SpecTraceClarifier | 29/53 | 23/53 |

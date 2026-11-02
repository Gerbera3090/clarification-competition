# SHW 팀 연구 공유 — hyukwon

2026-11-02에 혁원의 로컬 연구 자료를 복사한 브랜치다. 시현의 `load base structure`
커밋 `e78e5e9`를 기준으로 스켈레톤을 보존하고 코드·평가 표본·결과·분석·로그를 추가했다.
대회 제출 PR의 `submission/team-tbd`와 별도로 관리한다. 스켈레톤 형식으로의 리팩토링은 아직 하지 않았다.

## 먼저 읽을 자료

1. [전체 버전 비교](.local/train100-v1/COMPARISON.md): 같은 100문제의 통과·질문·비용과 문제별 결과.
2. [v1 질문 관점 분석](.local/train100-v1/v1-multi-judge-v2-20261101/deep-analysis/요약.md).
3. [v1·v1.1 결과 직접 분석](.local/train100-v1/v1_1-decision-properties-20261101/direct-review/결과_직접분석.md) 및 [100문제 상세 검토](.local/train100-v1/v1_1-decision-properties-20261101/direct-review/100문제_직접검토.md).
4. [v1·v1.1 속성 판정 비교](.local/train100-v1/v1_1-decision-properties-20261101/DECISION_COMPARISON.md).
5. [v2 실험 설명](.local/train100-v1/v2-concrete-spec-20261102/EXPERIMENT_NOTES.md).
6. [현재 runtime 기준 재채점 설명](.local/train100-v1/current-runtime-review/COMPARISON-current-runtime.md).

## 평가를 완료한 주요 버전

| 버전 | 접근 | 통과 | 질문한 문제 | 기록 모델 비용 | 해당 실행 코드 |
|---|---|---:|---:|---:|---|
| Direct | 바로 코드 생성 | 45/100 | 0/100 | $0.0673 | [snapshot](.local/train100-v1/runs/direct-gpt41mini/algorithm.py) |
| Okanagan | 기존 baseline | 53/100 | 85/100 | $0.1424 | [snapshot](.local/train100-v1/runs/okanagan-gpt41mini/algorithm.py) |
| v1 | 다섯 관점의 보고서를 최종 LLM이 종합 | 53/100 | 77/100 | $0.4605 | [snapshot](.local/train100-v1/v1-multi-judge-v2-20261101/algorithm.py) |
| v1.1 | 속성 쌍 판정에 decision model 사용 | 57/100 | 72/100 | $0.4606 | [snapshot](.local/train100-v1/v1_1-decision-properties-20261101/algorithm.py) |
| v2, 질문 최대 1회 | 입출력 명세 확인 게이트 추가 | 57/100 | 91/100 | $0.2326 | [snapshot](.local/train100-v1/v2-concrete-spec-20261102/algorithm.py) |

코드·가상 사용자 모델은 GPT-4.1 mini이며 v1.1과 v2는 GPT-6 Luna Decisions도 사용했다.
각 행은 단일 확률적 실행이다. 이 숫자로 모델 교체의 인과 효과나 전체 train 성능을 확정하지 않는다.
비용은 결과에 기록된 호출 비용이며 중단 호출·별도 분석·요금 계산 실패분이 빠질 수 있다.
PBT 초기 버전과 PBT4/5/5.1, SpecTrace 결과도 전체 비교표와 각 실행 폴더에 보존했다.

`clarify/algorithms/`는 편집 중이던 최신 소스이고, 각 실행 폴더의 `algorithm.py`는
그 실행에 사용한 코드다. **현재 `v2_concrete_spec.py`는 답변을 반영해 반복 질문하는 후속 버전**으로,
위 v2 57/100 결과의 코드와 다르다. `v2-loop-3turn-20261102/`는 복사 당시 진행 중인 기록이며,
완료된 평가로 취급하지 않는다. 각 실행의 `experiment.json`과 코드 해시를 함께 확인한다.

## 데이터와 분석의 범위

- [고정 표본 설명](.local/train100-v1/README.md), [선정 코드](.local/train100-v1/build_sample.py), [manifest](.local/train100-v1/manifest.json), [입력 배치](.local/train100-v1/batches/).
- 공개 **train 개발용** 100문제다. HumanEval/MBPP × 원본/모순 변형 각 25개, seed `20261030`.
  별도의 ambiguous·incomplete 변형은 포함하지 않는다. 모순 변형이라는 출처가 실제 모순의 정답 라벨은 아니다.
- 배치의 참조 설명과 테스트는 평가 환경용이다. 제출 알고리즘에는 SDK의 `prompt`, `entry_point`만 주며,
  분석에서 확인한 테스트·canonical·참조 답변을 실행 중 알고리즘에 공급하지 않는다.
- 각 `results.jsonl`에는 생성 코드, 질문·답변, 채점 결과가 있다. `all-output.jsonl`은 채점 전 출력이다.
  재채점 전후 결과를 구분한다. 원본·중단·재개·pilot·validation 실험은 서로 합산하지 않는다.
- [테스트 기준 질문 필요성 검토](.local/train100-v1/test-grounded-budget-audit-20261102/REPORT.md)는
  조건부 검토·추정 자료이며 공식 라벨이나 최소 질문 수 증명이 아니다. 이 보고서는 옛 PBT4 48/100을
  연결했으므로 현재 runtime 기준 PBT4 50/100과 섞어 해석하지 않는다.
- 가상 사용자 답변과 실제 테스트가 다른 사례도 있다. 코드 실패를 질문 품질만으로 해석하지 않는다.

## 포함한 원본 기록

`.local/` 아래 초기 실행, validation 실행, 질문 감사, 실패 분석, 재채점, 고정 train 실험의
JSON/JSONL, 보고서, Python·shell 스크립트와 로그를 보존했다. 중복·실패·중단 기록도 연구 경위 확인용으로 포함했다.
원본 로그와 메타데이터 안의 과거 로컬 절대 경로는 출처 기록으로 남겼다. 그 경로를 새 환경의 실행 경로로 쓰지 않는다.
전체 크기와 파일별 원본/공유본 SHA-256, 복사 시각은 [TEAM_SNAPSHOT.json](TEAM_SNAPSHOT.json)에 기록한다.
파일별 시점의 스냅샷이므로 진행 중인 실행의 로그 끝은 불완전할 수 있다.
`.env`, 비밀키, 가상환경, `__pycache__`, PID와 잠금 파일은 포함하지 않았다.

## 설치와 비용 없는 확인

저장소 루트에서 실행한다. Python 3.13과 uv가 필요하며 실제 코드 채점에는 Docker가 필요하다.

```bash
uv sync --frozen
uv run --frozen python -m unittest discover -s tests
uv run --frozen python -m unittest discover -s experiment_tools/tests
uv run --frozen python experiment_tools/compare_train100.py
```

위 테스트와 기존 비교표 재생성은 모델을 호출하지 않는다. 비교 도구는 기록된 과거 절대 경로를
현재 checkout의 `.local/train100-v1`로 해석하고 원본 결과의 해시를 검증한다.

## 새 실험 실행

`cp .env.example .env` 후 자신의 키를 넣고 `source .env`로 불러온다. 아래는 **계획 확인만** 한다.

```bash
uv run --frozen python experiment_tools/run_train100.py \
  --algorithm .local/train100-v1/v1_1-decision-properties-20261101/algorithm.py \
  --output-dir .local/team-runs/v1_1-new \
  --model openai/gpt-4.1-mini --decision-model openai/gpt-6-luna
```

실제 호출은 같은 명령에 `--execute --pilot 1`을 추가한다. 이후 같은 출력 폴더에서 `--pilot 1`을
빼고 `--execute`로 이어서 100개를 실행·채점할 수 있다. **모델 사용료가 발생한다.** 기존 결과 폴더를 덮어쓰지 않는다.
최신 반복 질문 v2는 별도 실험이며 `--max-turns 3` 등 질문 예산도 함께 기록한다.
실행·분석 도구의 상세 사용법은 [experiment_tools/README.md](experiment_tools/README.md)를 참고한다.

`clarify/runtime.py`에는 입력에 제공된 함수명을 채점에서 호출하는 수정과 회귀 테스트가 포함돼 있다.
`clarify/llm.py`의 변경은 로컬 Ollama 설정용이다. 이 SDK 변경들은 연구용이며 대회 제출 PR에 함께 넣지 않는다.
제출 시에는 최종 알고리즘 파일, 팀·라이선스 정보와 공식 규칙에 맞는 검증을 따로 준비한다.

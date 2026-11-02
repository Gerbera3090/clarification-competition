# 대회 실험 및 실패 분석 도구

이 도구들은 대회 SDK와 제출 알고리즘을 수정하지 않는다. 실험이 채점된 다음 결과를 읽어 실패를 분석한다. 입력과 테스트 결과는 제출 알고리즘에 전달되지 않는다.

## 이미 채점한 실행 분석

미리보기는 모델을 호출하지 않고 분석 대상과 호출 횟수만 표시한다.

```bash
cd /path/to/clarification-competition
uv run --frozen python experiment_tools/analyze_run.py \
  --results .local/train100-v1/pbt3/results.jsonl \
  --trace-dir .local/train100-v1/pbt3 \
  --limit 5
```

실제 분석은 `--analyze`를 추가한다. 예시는 실패한 문제 중 5개에 대해 각 1회, 전체 요약에 1회 모델을 호출하므로 **최대 6회 추가 호출**이다.

```bash
cd /path/to/clarification-competition
source .env
uv run --frozen python experiment_tools/analyze_run.py \
  --results .local/train100-v1/pbt3/results.jsonl \
  --trace-dir .local/train100-v1/pbt3 \
  --output-dir .local/train100-v1/pbt3/analysis-first5 \
  --limit 5 --analyze
```

`--limit`을 생략하면 모든 실패를 분석한다. 전체 분석을 하려면 `analysis-all`처럼 **새 출력 폴더**를 지정한다. 기본 분석 모델은 `.env`를 불러온 뒤 `ECC_OPENAI_MODEL`이며 `--model`로 바꿀 수 있다.

출력:

- `REPORT.md`: 전체 통계, LLM의 반복 패턴 요약, 각 실패의 관찰·가설·다음 확인.
- `failures.jsonl`: 실패별 원문 분석 응답, 상태, 토큰과 기록된 비용.
- `summary.json`: 전체 요약 응답과 기록된 비용.
- `run.json`: 입력 해시, 로그 해시와 모델 설정. 같은 결과와 설정으로 재개할 때 이미 기록한 분석은 호출하지 않는다.

분석에 사용되는 것은 해당 문제, 질문과 답, 생성 코드, 채점 메시지와 매칭 가능한 중간 로그다. `--trace-dir`은 선택 사항이다. 긴 근거가 잘리면 보고서에 표시한다. LLM 분석은 확정된 원인이 아니라 검토할 가설이다. 완료된 호출의 기록 비용은 보고서에 따로 표시하지만, 네트워크 중단 등의 청구는 API 사용량에서 확인해야 한다.

전체 요약 호출에는 전체 통계, 실패별 분석과 모든 성공 문제의 축약된 문제·질문·답변·코드가 들어간다. 성공 사례의 전체 실행 로그는 요약 호출에 전달하지 않는다.

중단 후 같은 명령을 다시 실행하면 기록된 항목을 건너뛴다. 이미 기록된 오류 응답은 자동 재시도하지 않는다. 다만 요청이 모델 제공자에게 도달한 직후 기록 전에 프로세스가 중단되면, 재개 시 해당 요청이 다시 호출될 수 있다.

## 고정 train 100문제 실행 → 채점 → 분석

실행 계획만 확인:

```bash
uv run --frozen python experiment_tools/run_train100.py \
  --algorithm clarify/algorithms/pbt_clarifier3.py \
  --output-dir .local/experiments/pbt3-new-run
```

실제로 100문제를 생성·채점하고, 실패 5개만 LLM으로 분석하려면:

```bash
source .env
open -a Docker
uv run --frozen python experiment_tools/run_train100.py \
  --algorithm clarify/algorithms/pbt_clarifier3.py \
  --output-dir .local/experiments/pbt3-new-run \
  --execute --analyze --analysis-limit 5
```

`--execute`는 생성 API 호출을 켜며 **문제당 여러 번의 모델 호출**이 발생할 수 있다. `--analyze`는 채점 후 실패 분석에 별도의 호출을 추가한다. 전체 실패를 분석하려면 `--analysis-limit`을 생략한다.

무거운 알고리즘의 시간과 비용을 먼저 확인하려면 `--execute --pilot 1`로 첫 문제만 실행할 수 있다. 이후 같은 출력 폴더에서 `--pilot` 없이 실행하면 해당 문제를 다시 호출하지 않고 재사용한다. 파일럿은 생성만 수행하며, 100문제 채점·비교표 등록은 전체 실행이 완료된 뒤 진행한다.

실행 폴더에 알고리즘 사본과 입력 해시가 저장된다. 완료된 배치는 재실행 시 재사용한다. 일부만 기록된 배치나 다른 알고리즘·모델·표본이 있는 폴더는 덮어쓰지 않고 중단한다. 채점만으로 만든 `REPORT.md`와 선택한 LLM 분석의 `analysis/REPORT.md`는 별도다.

## 이전 실행과 자동 비교

고정 100문제의 실행과 채점이 끝나면 `run_train100.py`가 결과를 자동으로 등록하고 `.local/train100-v1/COMPARISON.md`를 갱신한다. 이전 결과를 지우지 않고 실행별 행을 추가한다. 문제의 ID와 원문, 입력 해시, 평가 완료 여부를 확인하며 다른 문제 집합의 결과는 합치지 않는다.

비교 보고서를 다시 만들려면:

```bash
uv run --frozen python experiment_tools/compare_train100.py
```

같은 알고리즘도 실행마다 결과가 달라질 수 있으며, 모델이나 평가 환경이 다르면 직접 비교할 때 주의한다. `CounterThenPBT`는 현재 `PBTClarifier3`의 다른 이름이므로 별도 알고리즘 행으로 중복 집계하지 않는다.

이 고정 표본은 train 개발용이다. validation 개별 문제를 기준으로 조정하지 않으며, 비공개 테스트나 숨은 요구사항을 참가 알고리즘에 공급하지 않는다.

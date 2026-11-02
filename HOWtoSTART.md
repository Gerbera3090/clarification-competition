# The Clarification Challenge: 로컬에서 시작하기

이 문서는 `ECC`에 준비한 Quick Start 에이전트를 **로컬 모델로 한 문제만** 실행하는 방법이다. OpenAI API 키나 유료 모델 호출은 필요 없다.

## OpenAI API 크레딧으로 실행하기

자격이 되는 ChatGPT Pro 계정은 [OpenAI 안내](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)에 따라 API 크레딧을 신청할 수 있다. ChatGPT `Settings → Billing`에서 크레딧 혜택을 **본인이 소유한 API 조직**에 연결하고, API Platform의 Billing에서 잔액을 확인한다. 키는 그 조직의 프로젝트에서 만든다.

1. [API Keys](https://platform.openai.com/api-keys)에서 연결한 조직의 프로젝트 키를 만든다.
2. Git에서 제외된 `.env` 파일의 `# export OPENAI_API_KEY=` 줄에서 `#`를 지우고 `=` 뒤에 키를 직접 넣는다. 키를 채팅이나 PR에 붙여넣지 않는다.
3. Docker Desktop을 켜고 `docker info`가 성공하면 아래 한 문제 시험을 실행한다.

```bash
cd /path/to/clarification-competition
open -a Docker
docker info
./.local/openai-smoke-test.sh
```

이 스크립트는 `.env`의 `ECC_OPENAI_MODEL=openai/gpt-4.1-mini`를 코드 생성 모델과 가상 사용자 모델에 모두 지정한다. `OPENAI_API_KEY`가 비어 있으면 호출하지 않고 종료한다. 결과는 `.local/openai-smoke-results.jsonl`에 저장된다. **API 크레딧이 소진되면 조직의 결제 설정에 따라 요청이 실패하거나 유료 잔액을 사용할 수 있으므로**, 실행 전 Billing에서 잔액과 자동 충전 설정을 확인한다.

`You have no credits remaining` 오류가 나오면 키가 속한 **API Platform 조직의 Billing**에서 API 크레딧을 확인한다. ChatGPT 앱의 일반 사용량 표시와 API 조직의 크레딧은 구분해서 본다. 오류가 발생한 실행의 채점 결과는 모델 성능 결과로 해석하지 않는다.

## OpenAI decision model 연결 확인

`.env`에 있는 기존 `OPENAI_API_KEY`를 그대로 사용하고, `ECC_DECISION_MODEL`에는 `openai/gpt-6-luna`를 지정했다. 코드 생성용 `ECC_OPENAI_MODEL`은 별도로 유지한다. 아래 명령은 대회 SDK의 `env.decide()`로 **한 번** 호출해 예제 property 두 개를 분류한다. API 사용료가 발생하며 Docker는 필요 없다.

```bash
cd /path/to/clarification-competition
source .env
.venv/bin/python experiment_tools/decision_smoke.py
```

응답의 `choice`가 모델의 선택이고 `probabilities`는 선택지별 모델 확률이다. 연결 확인용 작은 예제이므로 이 결과만으로 실제 문제의 성능을 판단할 수는 없다. 출력되는 비용은 SDK가 기록한 추정치이며 실제 청구액과 다를 수 있다.

나중에 `env.decide()`를 실제로 사용하는 clarifier를 만들면 `experiment_tools/run_train100.py`의 `--decision-model "$ECC_DECISION_MODEL"` 옵션으로 이 모델을 전달한다. `--pilot 1 --execute`는 첫 문제만 실행하며, 추후 전체 실행에서 그 결과를 재사용한다. 현재 PBTClarifier4는 `env.decide()`를 호출하지 않으므로 옵션만 추가해도 알고리즘이 바뀌지 않는다. 대회 제출 시 decision model을 사용하려면 주최 측에 요청해야 한다.

## 준비된 것

- Python 패키지: `.venv`에 설치됨 (`uv sync --python 3.13 --frozen`)
- 로컬 모델: Ollama의 `qwen2.5-coder:1.5b`
- 에이전트 코드: `clarify/algorithms/my_clarification.py`
- 실행 스크립트: `.local/start-ollama.sh`, `.local/smoke-test.sh`, `.local/chat.sh`
- 코드 채점: Docker의 `ganler/evalplus` 이미지

## 1. 로컬 모델 서버 시작 — 터미널 1

```bash
cd /path/to/clarification-competition
./.local/start-ollama.sh
```

이 터미널은 실행 중인 채로 둔다. 서버는 이 명령을 실행한 동안만 켜지고, 모델은 응답을 마치면 메모리에서 내려간다. 자동 시작 서비스는 등록하지 않았다.

## 2. 한 문제 생성·채점 — 터미널 2

```bash
cd /path/to/clarification-competition
open -a Docker
docker info
./.local/smoke-test.sh
```

`docker info`가 연결 오류를 내면 Docker Desktop이 완전히 켜질 때까지 잠시 기다렸다가 다시 실행한다. `smoke-test.sh`는 공개 예제의 첫 문제 **하나만** 사용한다. 두 모델 역할(코드 생성과 가상 사용자 답변) 모두 `.env`에 지정된 로컬 모델을 사용한다.

첫 실행에서는 EvalPlus 기준 데이터를 추가로 다운로드하므로 시간이 더 걸릴 수 있다. 실행 출력 끝의 `Test Results`와 `Run Statistics`에서 통과 여부와 점수를 볼 수 있다.

## 3. 결과 보기

```bash
cd /path/to/clarification-competition
cat .local/quickstart-results.jsonl
```

입력은 `.local/smoke-input.jsonl`, 모델이 생성한 코드는 `.local/quickstart-output.jsonl`, 채점 결과는 `.local/quickstart-results.jsonl`에 저장된다. `.local/`은 Git에서 제외되어 대회 제출 PR에 들어가지 않는다.

코드를 고쳐서 다시 확인하고 싶으면 `clarify/algorithms/my_clarification.py`를 편집한 다음 `./.local/smoke-test.sh`를 재실행하면 된다.

## 4. 직접 대화해보기 — 선택 사항

터미널 1에서 Ollama 서버가 실행 중일 때, 다른 터미널에서 다음 명령을 사용한다.

```bash
cd /path/to/clarification-competition
./.local/chat.sh
```

스크립트가 `.env`를 읽고 `ollama/qwen2.5-coder:1.5b`를 자동으로 전달한다. 이 모드는 직접 요청을 입력하고 질문에 답해보는 연습용이며, 대회 채점과 동일한 설정은 아니다. `/quit`으로 대화를 마친다.

직접 `chat.py`를 실행한다면 모델 변수 앞의 `$`를 빼먹지 않는다. `"$ECC_LOCAL_MODEL"`은 설정된 모델명으로 치환되지만, `"ECC_LOCAL_MODEL"`은 문자 그대로 전달되어 LiteLLM의 `LLM Provider NOT provided` 오류가 난다.

## 5. 종료

- 터미널 1에서 `Ctrl+C`를 눌러 Ollama 서버를 종료한다.
- Docker Desktop은 사용을 마쳤다면 메뉴에서 Quit Docker Desktop을 선택한다.

모델이 메모리에 남아 있는지 확인하려면 Ollama 서버가 켜진 동안 `ollama ps`를 실행한다.

## 코드 구조

`my_clarification.py`의 `run(env, problem)`은 문제를 받아 `env.llm()`으로 질문 하나를 생성한다. `env.ask_human()`으로 가상 사용자 답변을 얻은 뒤, 원래 문제와 질문·답변을 함께 모델에 전달해 Python 코드를 만든다. 현재는 질문 필요성을 판단하지 않고 매번 한 번 묻는 연습용 방식이다. 충분히 명확한 문제에도 질문하므로 대회 점수에는 불리할 수 있다.

팀명·팀원·연락처·라이선스 헤더는 비워두었다. 실제 대회 PR을 열기 전에는 이 정보를 채우고, `CONTRIBUTING.md`의 제출 규칙을 확인해야 한다. **제출 PR에는 알고리즘 파일 하나와 선택적인 리더보드 행만 포함**한다.

## 실행 후 실패 원인 분석

기존 채점 결과를 먼저 비용 없이 미리 볼 수 있다.

```bash
cd /path/to/clarification-competition
uv run --frozen python experiment_tools/analyze_run.py \
  --results .local/train100-v1/pbt3/results.jsonl \
  --trace-dir .local/train100-v1/pbt3 --limit 5
```

실제로 LLM 분석을 실행하려면 `source .env` 후 위 명령에 `--output-dir .local/train100-v1/pbt3/analysis-first5 --analyze`를 추가한다. 이 예시는 실패 5개를 각각 분석하고 전체 요약을 한 번 생성하므로 **최대 6회 추가 모델 호출**이 발생한다.

100문제 생성부터 채점, 실패 분석까지 연결하는 방법과 전체 결과 분석·재개 방법은 [실험 도구 안내](experiment_tools/README.md)를 참고한다.

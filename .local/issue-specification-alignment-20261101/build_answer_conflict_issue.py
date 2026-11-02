"""Prepare an observed-answer/evaluator-conflict issue; never publishes."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
evidence = json.loads((HERE / "humaneval42-clarification-evidence.json").read_text())
verification = json.loads((HERE / "answer-conflict-verification.json").read_text())
run = evidence["runs"][0]
q, aspect, quality, answer = run["clarification_history"][0]
assert quality == "3"
assert [r["passed"] for r in verification["checks"]] == [False, True]
title = "How should participants handle QUALITY=3 clarification answers that contradict evaluation tests?"
body = f'''Hi organizers,

Could you clarify the expected participant behavior when the simulated user assigns `QUALITY=3` to a clarification, but following its answer directly causes a test failure?

## Observed example: HumanEval/42 (`incr_list`)

The [released original prompt](https://github.com/serval-uni-lu/clarification-competition/blob/be108fb8ef4b87ede7b9f8edd1bd3c2166169e29/data/humaneval/humaneval_original.jsonl#L43) asks to return a list with its elements incremented by 1. Its signature is `incr_list(l: list)`; it does not impose an integer-only element restriction.

Our captured interaction was:

> **Question:** {q}
>
> **Recorded quality:** `QUALITY={quality}`, requirement ID `{aspect}`
>
> **Answer:** {answer}

The generated implementation followed that instruction:

```python
def incr_list(l: list):
    if not all(isinstance(x, int) for x in l):
        raise TypeError("All elements must be integers")
    return [x + 1 for x in l]
```

However, the EvalPlus inputs used by evaluation include:

```python
incr_list([2.5, 3.7, 8.9, 1.2, 0.5])
# Expected: [3.5, 4.7, 9.9, 2.2, 1.5]
```

The answer-following implementation raises `TypeError` instead. The saved evaluation result records that failure at the integer check.

We also replayed the captured implementation with the current Docker evaluator. It fails, while removing only the two-line integer guard makes the same implementation pass all 3 base and 999 plus inputs. A local comparison against the reference implementation identifies 108 float-containing plus inputs rejected by that guard.

This reproduces the conflict using a saved transcript; it does not claim that rerunning the model always produces the same answer. `QUALITY=3` is the simulator's recorded score, rather than our independent certification of question quality.

## Questions

1. Are simulated-user clarification answers intended to be authoritative specifications? Should the assistant follow them when they add restrictions not present in the original prompt?
2. How should answer/evaluation conflicts like this be handled in scoring or reporting? Should they be treated as participant failures, simulator errors, or samples requiring correction, exclusion, or regrading?
3. If robustness to incorrect simulator answers is part of the challenge, what behavior is expected from participants who cannot inspect the evaluation tests, particularly under the default one-turn clarification budget?

An explicit policy would help us distinguish clarification-algorithm failures from errors introduced by an accepted clarification answer. A consistency check between simulator answers and the evaluator's semantic contract could also help.

## Environment and verification

- Repository baseline: `be108fb8ef4b87ede7b9f8edd1bd3c2166169e29`.
- Agent and simulator configured as `openai/gpt-4.1-mini` in the original run.
- `evalplus==0.3.1`; HumanEvalPlus dataset hash `fe585eb4df8c88d844eeb463ea4d0302`.
- The guard-removal replay used our current local evaluator, including an entry-point compatibility fix. This task's function name is `incr_list` on both sides, so that fix does not affect the demonstrated conflict.

The conflicting released fixture can be inspected without any model call:

```python
from evalplus.data import get_human_eval_plus

problem = get_human_eval_plus()["HumanEval/42"]
values = [2.5, 3.7, 8.9, 1.2, 0.5]
assert [values] in problem["plus_input"]
print([x + 1 for x in values])
# [3.5, 4.7, 9.9, 2.2, 1.5]
```
'''
payload = {"repository_full_name": "serval-uni-lu/clarification-competition", "title": title,
           "body": body, "status": "draft_only_not_published", "assessment_date": "2026-11-01",
           "supersedes_for_current_discussion": "issue_payload.json",
           "evidence_files": ["humaneval42-clarification-evidence.json", "answer-conflict-verification.json"]}
(HERE / "issue_answer_conflict_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
plain = title + "\n\n" + body.replace("## ", "").replace("```python\n", "").replace("```\n", "")
(HERE / "ISSUE_ANSWER_CONFLICT_DRAFT.txt").write_text(plain)
ko = '''이전 초안의 요지
가상사용자에게 제공되는 참조 명세가 실제 평가에서 요구하는 행동 선택을 구별하지 못하는 사례(MBPP753/627)를 보이고, 참조 보완을 요청했다.

새 초안의 요지
HumanEval42 incr_list의 실제 QUALITY3 질문·답변·생성 코드·평가 실패를 제시한다.
가상사용자가 정수가 아닌 원소를 거부하라고 했고, 그 지시를 따른 검사 때문에 float 포함 평가에서 실패했다.
동일 코드에서 두 줄짜리 정수 검사만 제거하면 현재 Docker evaluator의 base3+plus999를 모두 통과했다.

운영진에게 물을 내용
1. 가상사용자 답변은 의도한 요구사항의 권위 있는 근거인가?
2. 질문이3점이고 그 답을 충실히 구현했는데 평가와 충돌하면, 참가자·simulator·데이터 중 어느 오류로 다루며 점수는 어떻게 처리하는가?
3. simulator 답변 오류에 대한 강건성이 챌린지의 일부라면, 숨은 테스트를 볼 수 없고 질문 한도가 기본1회인 참가자는 어떤 행동을 해야 하는가?

주장 범위
질문3점은 실제 simulator의 점수다. 독립적인 품질 판정 결과로 포장하지 않는다.
이번 검증은 저장된 상호작용의 재생과 코드의 두 줄 수정 비교이며, 모델이 항상 같은 답을 한다고 주장하지 않는다.
현재 로컬 evaluator의 entry_point 호환 수정 사실을 명시했다. 이 문제의 함수명은 양쪽 모두 incr_list라 그 수정이 충돌의 원인이 아니다.
이전 참조 누락 초안은 그대로 보존했고, 새 초안도 GitHub에는 게시하지 않았다.
'''
(HERE / "ANSWER_CONFLICT_RECOMMENDATION.txt").write_text(ko)
print(json.dumps({"title": title, "body_words": len(body.split()), "published": False}))

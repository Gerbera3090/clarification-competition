"""Prepare reviewable GitHub issue text. This script does not publish anything."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = "serval-uni-lu/clarification-competition"
COMMIT = "be108fb8ef4b87ede7b9f8edd1bd3c2166169e29"
BASE = f"https://github.com/{REPO}/blob/{COMMIT}"
title = "Simulated-user references can leave evaluator-required semantics unspecified (MBPP 753/627)"
body = f'''Hi organizers, and thanks for organizing the challenge.

I found two released training examples where the privileged reference supplied to the simulated user does not distinguish semantic choices that evaluation later distinguishes. Could you clarify whether this is intended, or whether these references should be expanded?

## Current context

In [`_build_human_system_prompt`]({BASE}/clarify/env.py#L156-L172), the simulated user receives `clarifications` when present, otherwise `reference_prompt`. For the two variants below, the released clarification overlay does not contain a matching entry, so the decoded reference is the effective hidden-requirements context.

These observations were made at commit `{COMMIT}`. I also checked that the relevant `clarify/env.py` and variant-data blobs are unchanged on `main` when preparing this report.

## Example 1: MBPP/753 — which tuple field defines the minimum?

The [variant record]({BASE}/data/mbpp/mbpp_larbi_contradictory.jsonl#L753) decodes to this reference:

```text
Write a function to find minimum k records from tuple list.
assert min_k([('Manjeet', 10), ('Akshat', 4), ('Akash', 2), ('Nikhil', 8)], 2) == [('Akash', 2), ('Akshat', 4)]
```

Both of these interpretations satisfy that reference example:

```python
sorted(records)[:k]                         # ordinary tuple ordering
sorted(records, key=lambda r: r[1])[:k]     # second numeric field
```

They also agree on the second checked-in assertion. On the third assertion, `records=[('tanmay',14), ('Amer',11), ('Ayesha',9), ('SKD',16)]`, `k=1`, tuple ordering selects `('Amer',11)`, while numeric-field ordering selects `('Ayesha',9)`. The checked-in assertion and EvalPlus reference implementation require the latter.

An atomic question such as “Which tuple field should determine the ranking?” addresses this choice, but the supplied reference does not explicitly identify the field, and its example is non-discriminating.

## Example 2: MBPP/627 — does the missing-number domain include zero?

The [reference]({BASE}/data/mbpp/mbpp_larbi_contradictory.jsonl#L627) says “find the smallest missing number” and gives only:

```python
assert find_First_Missing([0,1,2,3],0,3) == 4
```

Searching for the smallest missing nonnegative integer and the smallest missing positive integer both return `4`. Evaluation additionally requires `find_First_Missing([2,3,5,8,9],0,4) == 0`, which distinguishes these choices. The reference does not state the candidate domain.

## Why this matters

The intended ambiguity in the assistant-facing prompt can be resolved only if the simulated user has sufficiently specified intent. Otherwise, an answer may depend on the model's conventions rather than an identified requirement, potentially confounding clarification quality and end-to-end success.

This is a deterministic reference-coverage observation. I have not established that a particular simulated-user model must fail, that no successful question exists, or how much this affects aggregate scores. A model may infer the intended convention.

## Suggested clarification or improvement

1. Does the official evaluation provide an additional authoritative specification beyond this context?
2. If not, could the simulator-only reference explicitly state behavioral facts such as “rank by the second tuple element” and “search over nonnegative integers including zero”?
3. Could reference coverage and reference/example/evaluator consistency be checked when preparing the benchmark, with unresolved cases corrected or marked separately?

The assistant-facing interface and hidden evaluation tests can stay unchanged. A complete behavioral reference for the simulated user would let clarification recover intent without requiring direct access to test cases or reference code.

## Reproduction

This uses only the standard library, from the repository root; no model calls or Docker are needed:

```python
import base64, json, zlib
from pathlib import Path

path = Path("data/mbpp/mbpp_larbi_contradictory.jsonl")
rows = {{r["task_id"]: r for r in map(json.loads, path.read_text().splitlines())}}
for task in ("Mbpp/753", "Mbpp/627"):
    ref = rows[task]["reference_prompt"]
    print(task, zlib.decompress(base64.b64decode(ref[4:])).decode())

reference_records = [('Manjeet',10), ('Akshat',4), ('Akash',2), ('Nikhil',8)]
assert sorted(reference_records)[:2] == sorted(reference_records, key=lambda r:r[1])[:2]
check_records = [('tanmay',14), ('Amer',11), ('Ayesha',9), ('SKD',16)]
print(sorted(check_records)[:1])                         # [('Amer', 11)]
print(sorted(check_records, key=lambda r:r[1])[:1])     # [('Ayesha', 9)]

def missing(values, start):
    while start in values:
        start += 1
    return start
assert missing([0,1,2,3], 0) == missing([0,1,2,3], 1) == 4
print(missing([2,3,5,8,9], 0), missing([2,3,5,8,9], 1))  # 0 1
```
'''

payload = {"repository_full_name": REPO, "title": title, "body": body,
           "status": "draft_only_not_published", "assessment_date": "2026-11-01"}
(HERE / "issue_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
# Plain-text companion for reading; the JSON body preserves GitHub formatting.
plain = title + "\n\n" + body.replace("## ", "").replace("```python\n", "").replace("```text\n", "").replace("```\n", "")
(HERE / "ISSUE_DRAFT.txt").write_text(plain)
notes = '''이슈 제안의 초점

가상사용자의 비공개 명세가 평가에서 구별하는 행동 선택을 충분히 담고 있는가를 묻는다.
테스트 접근 제한 자체는 버그라고 주장하지 않는다. 모델 실패율이나 가장 큰 성능 저하 원인도 측정하지 않았다.

권장 대표 사례
MBPP/753: 튜플의 비교 키. 공개·참조 정보만으로 두 자연스러운 구현을 구별하기 어렵고 실제 예시에서 차이가 확인된다.
MBPP/627: 탐색 도메인의 0 포함 여부. 관례 추론 여지가 있으므로 보조 사례로 둔다.

요청할 개선
현재 reference_prompt를 가상사용자 전용 행동 명세로 보완한다.
정답 코드·테스트를 참가 알고리즘에게 제공하지 않고, 비교 키와 탐색 도메인 같은 의미상의 사실을 명확히 한다.
명세와 예시·평가의 일관성을 검증하고, 근거가 불충분한 행을 별도 표시하는 방안을 묻는다.

별도 후속 데이터 오류
MBPP/461: uppercase count라고 하면서 PYthon과 BigData의 기대값이 1이다(실제 대문자 2개).
MBPP/328: rotation이라고 하면서 입력 길이 10의 기대 출력이 11 또는 7이다.
두 사례는 현재 참조 자체에 이미 이상한 예시가 있어, 이슈의 명세 누락 문제와 나누어 보고하는 편이 원인이 선명하다.

표현에서 피할 주장
모든 가상사용자가 반드시 틀린다, 질문으로 절대 해결 불가능하다, 전체 성능 저하의 가장 큰 원인이다.
현재 재현은 참조 정보가 목표 해석을 유일하게 정하지 않는다는 사실이며 simulator 실험이 아니다.

기존 이슈
검색에서 동일 내용의 이슈는 확인하지 못했다. #7은 entry_point 불일치, #46은 call adapter 허용 여부로 다른 문제다.
GitHub에는 게시하지 않았으며, issue_payload.json에 제목과 GitHub 형식의 본문을 저장했다.
'''
(HERE / "RECOMMENDATION.txt").write_text(notes)
print(json.dumps({"title": title, "body_words": len(body.split()), "published": False}))

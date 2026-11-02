"""Combine two related concerns while keeping their evidence distinct."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMIT = "be108fb8ef4b87ede7b9f8edd1bd3c2166169e29"
BASE = f"https://github.com/serval-uni-lu/clarification-competition/blob/{COMMIT}"
evidence = json.loads((HERE / "humaneval42-clarification-evidence.json").read_text())
verification = json.loads((HERE / "answer-conflict-verification.json").read_text())
assert [case["passed"] for case in verification["checks"]] == [False, True]
question, fact_id, quality, answer = evidence["runs"][0]["clarification_history"][0]
assert quality == "3"
title = "Are participants expected to tolerate incorrect answers from the simulated human?"
body = f'''Hi organizers,

We have a concrete case where the simulated human in the released SDK gave an instruction inconsistent with evaluation. The generated code implemented that instruction, and the resulting restriction caused the task to fail.

This was observed in a local run with both the agent and simulated human configured as `openai/gpt-4.1-mini`. We have not verified that the final private evaluation uses the same simulator model, context, or safeguards. The contribution guide says organizers fix those settings for final evaluation.

**Are incorrect simulated-human answers an intended source of noise that participants are expected to tolerate, or do the organizers plan to validate, correct, or otherwise account for these errors in evaluation?**

## A. Observed answer/test conflict: HumanEval/42

The [original `incr_list` prompt]({BASE}/data/humaneval/humaneval_original.jsonl#L43) asks to increment list elements by 1, without an integer-only element restriction. Our captured interaction was:

> **Question:** {question}
>
> **Recorded score:** `QUALITY={quality}`, requirement ID `{fact_id}`
>
> **Answer:** {answer}

The resulting implementation followed the answer:

```python
def incr_list(l: list):
    if not all(isinstance(x, int) for x in l):
        raise TypeError("All elements must be integers")
    return [x + 1 for x in l]
```

However, the EvalPlus inputs used by evaluation include `[2.5, 3.7, 8.9, 1.2, 0.5]`, for which the reference expects `[3.5, 4.7, 9.9, 2.2, 1.5]`. The answer-following code raises `TypeError` instead, as recorded in our evaluation result.

We replayed the captured code with the current local Docker evaluator: it fails, while removing only the two-line integer guard makes it pass all 3 base and 999 plus inputs. This isolates the restriction introduced by the answer as the cause of this failure.

This is a replay of a saved interaction; it does not claim that sampling the model again always yields the same answer.

## Policy clarification

1. Is robustness to misleading or incorrect simulated-human answers an intended capability being evaluated? If so, what reliability assumptions should participants make about this channel?
2. If such errors are not intended as part of the task, what correction or mitigation is planned, including the treatment of affected evaluation outcomes? For example, will answers be checked against authoritative requirements, erroneous interactions be replayed, or simulator-caused failures otherwise be accounted for?

If official evaluation uses a different simulator configuration or additional safeguards, clarifying those would also help. We can provide the captured interaction and the code before and after the two-line change.

<details>
<summary>Related reference-coverage observation: MBPP/753</summary>

In [`_build_human_system_prompt`]({BASE}/clarify/env.py#L156-L172), the simulator receives `clarifications` when available, otherwise `reference_prompt`. The [MBPP/753 variant]({BASE}/data/mbpp/mbpp_larbi_contradictory.jsonl#L753) has no matching clarification overlay, and its decoded reference is:

```text
Write a function to find minimum k records from tuple list.
assert min_k([('Manjeet',10), ('Akshat',4), ('Akash',2), ('Nikhil',8)], 2) == [('Akash',2), ('Akshat',4)]
```

Both ordinary tuple ordering and ordering by the second numeric field satisfy this reference example. They also agree on the second checked-in assertion. In the third assertion, the two policies select `('Amer',11)` and `('Ayesha',9)` respectively; evaluation requires the latter. The reference does not identify the comparison field.

This is a reference-coverage observation, not an observed simulator failure. A model may infer the intended convention. We are not claiming that insufficient reference information caused the particular answer in case A.

</details>

<details>
<summary>Verification context</summary>

- Repository baseline: `{COMMIT}`.
- Case A: agent and simulator configured as `openai/gpt-4.1-mini`; `evalplus==0.3.1`; HumanEvalPlus hash `fe585eb4df8c88d844eeb463ea4d0302`.
- The local replay includes an entry-point compatibility fix; both sides use `incr_list` here, so that fix does not affect the demonstrated conflict.
- Case B is reproducible from the released JSONL by decoding `REF_` with base64 and zlib and comparing the two sorting policies; it requires no model calls.

</details>
'''
payload = {"repository_full_name": "serval-uni-lu/clarification-competition", "title": title, "body": body,
           "status": "draft_only_not_published", "assessment_date": "2026-11-01",
           "combines": ["issue_payload.json", "issue_answer_conflict_payload.json"],
           "framing": "intended_simulator_noise_vs_organizer_correction_and_evaluation_mitigation",
           "evidence_distinction": {"A": "observed_saved_answer_and_controlled_code_replay",
                                    "B": "deterministic_privileged_reference_coverage_observation"}}
(HERE / "issue_combined_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
plain = title + "\n\n" + body.replace("## ", "").replace("```python\n", "").replace("```text\n", "").replace("```\n", "")
(HERE / "ISSUE_COMBINED_DRAFT.txt").write_text(plain)
(HERE / "ISSUE_BODY_FOR_GITHUB.txt").write_text(body)
(HERE / "ISSUE_TITLE_FOR_GITHUB.txt").write_text(title + "\n")
print(json.dumps({"title": title, "body_words": len(body.split()), "published": False}))

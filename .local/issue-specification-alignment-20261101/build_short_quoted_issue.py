"""Build concise context/example/question issue with captured verbatim Q/A."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
he = json.loads((HERE / "humaneval42-clarification-evidence.json").read_text())
mb = json.loads((HERE / "mbpp753-sorting-key-interaction.json").read_text())
he_q, _, he_quality, he_a = he["runs"][0]["clarification_history"][0]
title = "Clarification on simulated-human answers and reference context"
body = f'''Hi organizers, and thank you for organizing the challenge.

### Context

While testing the released SDK locally with `gpt-4.1-mini`, we encountered the following cases. We would appreciate your guidance on answer reliability and the reference context available to the simulated human.

### Example

**1. HumanEval/42 — an answer conflicting with evaluation**

> **Question:** {he_q}
>
> **Recorded quality:** `QUALITY={he_quality}`
>
> **Answer:** {he_a}

Our implementation followed this instruction, but evaluation includes float inputs and expects normal incrementing. Removing only the integer check allowed the implementation to pass all **1,002 tests**.

**2. MBPP/753 — an unspecified comparison field**

The reference supplied to the simulated human asks for the “minimum k records from tuple list,” without specifying the comparison field. Its reference example produces the same result under ordinary tuple ordering and ordering by the second numeric field.

In a recorded interaction:

> **Question:** {mb['question']}
>
> **Recorded quality:** `QUALITY={mb['recorded_quality']}`
>
> **Answer:** {mb['answer']}

This answer agrees with evaluation's comparison key. Our separate concern is that the supplied reference does not identify that key or distinguish the two interpretations; we are unsure what grounding is intended for this choice.

### Question

Could you please clarify:

1. Are occasional inaccuracies in the simulated human's answers an intended part of the challenge that participants should accommodate, or are there plans to validate/correct such answers or account for their impact on evaluation?
2. Is the simulated human's reference context intended to specify evaluator-required choices such as MBPP/753's comparison key? Does official evaluation provide additional context for these cases?

Thank you for your time and guidance.
'''
payload = {"repository_full_name": "serval-uni-lu/clarification-competition", "title": title, "body": body,
           "status": "draft_only_not_published", "assessment_date": "2026-11-02",
           "builder": Path(__file__).name,
           "quoted_sources": ["humaneval42-clarification-evidence.json", "mbpp753-sorting-key-interaction.json"]}
assert he_q in body and he_a in body and mb["question"] in body and mb["answer"] in body
(HERE / "issue_combined_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
(HERE / "ISSUE_BODY_FOR_GITHUB.txt").write_text(body)
(HERE / "ISSUE_TITLE_FOR_GITHUB.txt").write_text(title + "\n")
(HERE / "ISSUE_COMBINED_DRAFT.txt").write_text(title + "\n\n" + body)
print(json.dumps({"words": len(body.split()), "quotes_match_captured_records": True, "published": False}))

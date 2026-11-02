"""Replay captured HE42 code with/without its answer-directed type guard.

Uses current real Docker evaluator; does not generate a new simulator answer.
"""
import hashlib
import json
from pathlib import Path

from clarify.runtime import init_evalplus_evaluator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
evidence = json.loads((HERE / "humaneval42-clarification-evidence.json").read_text())
sample = [json.loads(s) for s in Path(evidence["dataset_source"]).read_text().splitlines()]
problem = next(r for r in sample if r["task_id"] == "HumanEval/42")
captured = evidence["runs"][0]["prompt_result"]
guard = '    if not all(isinstance(x, int) for x in l):\n        raise TypeError("All elements must be integers")\n'
assert captured.count(guard) == 1
without_guard = captured.replace(guard, "")
evaluator = init_evalplus_evaluator([problem], train=True)
checks = []
for label, code, expected in [("captured_answer_following_code", captured, False),
                              ("same_code_with_only_type_guard_removed", without_guard, True)]:
    passed, message = evaluator.evaluate(problem, "```python\n" + code + "\n```")
    checks.append({"label": label, "passed": passed, "expected": expected,
                   "message": message, "code": code})
    print(label, passed, flush=True)
    assert passed == expected
payload = {"task_id": "HumanEval/42", "checks": checks,
           "method": "Current Docker evaluator; stored model code and a two-line guard-removal intervention",
           "fresh_model_calls": 0, "fresh_simulator_calls": 0,
           "test_source": "EvalPlus base_input plus plus_input through clarify.runtime",
           "test_count": {"base": len(problem["base_input"]), "plus": len(problem["plus_input"])},
           "runtime_sha256": hashlib.sha256((ROOT / "clarify/runtime.py").read_bytes()).hexdigest(),
           "limitations": ["This verifies the observed answer/code/evaluation conflict, not deterministic reproduction of the model answer.",
                           "QUALITY=3 is the captured simulator score, not an independent quality adjudication."]}
(HERE / "answer-conflict-verification.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

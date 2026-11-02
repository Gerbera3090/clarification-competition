"""Check two illustrative information gaps against the current real evaluator.

Analyst-authored implementations, not a simulated-user/LLM experiment.
"""
import hashlib
import json
from pathlib import Path

from clarify.runtime import init_evalplus_evaluator

HERE = Path(__file__).resolve().parent
rows = [json.loads(s) for s in (HERE / "audit100.jsonl").read_text().splitlines()]
selected = {r["task_id"]: r for r in rows if r["task_id"] in {"HumanEval/43", "HumanEval/149"}}
evaluator = init_evalplus_evaluator(list(selected.values()), train=True)
cases = [
    ("HumanEval/43", "distinct_positions", True, '''def pairs_sum_to_zero(l):
    seen = set()
    for x in l:
        if -x in seen:
            return True
        seen.add(x)
    return False
'''),
    ("HumanEval/43", "distinct_values_counterinterpretation", False, '''def pairs_sum_to_zero(l):
    values = set(l)
    return any(-x in values and x != -x for x in values)
'''),
    ("HumanEval/149", "list_return_alphabetical_ties", True, '''def sorted_list_sum(lst):
    return sorted((s for s in lst if len(s) % 2 == 0), key=lambda s: (len(s), s))
'''),
    ("HumanEval/149", "list_return_reverse_alphabetical_ties", False, '''def sorted_list_sum(lst):
    values = sorted((s for s in lst if len(s) % 2 == 0), reverse=True)
    return sorted(values, key=len)
'''),
]
results = []
for task_id, interpretation, expected, code in cases:
    passed, message = evaluator.evaluate(selected[task_id], "```python\n" + code + "\n```")
    row = {"task_id": task_id, "interpretation": interpretation, "expected_pass": expected,
           "actual_pass": passed, "message": message, "code": code,
           "method": "analyst_authored_counterinterpretation_checked_in_current_docker_evaluator",
           "simulator_called": False, "llm_called": False}
    results.append(row)
    print(task_id, interpretation, passed, flush=True)
    if passed != expected:
        raise AssertionError(row)
payload = {"cases": results, "limitations": [
    "These checks validate illustrative test distinctions only, not the sufficiency annotations for all 100 tasks.",
    "Code was written with oracle knowledge; this is not a one-question LLM success-rate experiment.",
], "runtime_sha256": hashlib.sha256(Path("clarify/runtime.py").read_bytes()).hexdigest()}
(HERE / "example-verification.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

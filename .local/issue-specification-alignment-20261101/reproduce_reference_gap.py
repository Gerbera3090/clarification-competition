"""Inspect checked-in MBPP references; no models, network, or third-party packages.

Run from the repository root:
    python3 .local/issue-specification-alignment-20261101/reproduce_reference_gap.py

An optional positional argument selects another checkout of the same repository.
This demonstrates non-unique example behavior, not simulator response behavior.
"""

import ast
import base64
import json
from pathlib import Path
import sys
import zlib


root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
source = Path("data/mbpp/mbpp_larbi_contradictory.jsonl")
rows = {}
for line_no, line in enumerate((root / source).read_text().splitlines(), 1):
    row = json.loads(line)
    if row["task_id"] in {"Mbpp/627", "Mbpp/753", "Mbpp/461"}:
        rows[row["task_id"]] = (line_no, row)


def decode_reference(row):
    ref = row["reference_prompt"]
    assert ref.startswith("REF_")
    return zlib.decompress(base64.b64decode(ref[4:])).decode("utf-8")


def assertions(text):
    """Read only literal call arguments and expected values; never execute data."""
    lines = "\n".join(line for line in text.splitlines() if line.startswith("assert "))
    for stmt in ast.parse(lines).body:
        assert isinstance(stmt, ast.Assert)
        expr = stmt.test
        assert isinstance(expr, ast.Compare) and len(expr.comparators) == 1
        assert len(expr.ops) == 1 and isinstance(expr.ops[0], ast.Eq)
        call = expr.left
        assert isinstance(call, ast.Call) and not call.keywords
        yield [ast.literal_eval(arg) for arg in call.args], ast.literal_eval(expr.comparators[0])


def missing_nonnegative(array, _start, _end):
    n = 0
    while n in array:
        n += 1
    return n


def missing_positive(array, _start, _end):
    n = 1
    while n in array:
        n += 1
    return n


def minimum_by_tuple(records, k):
    return sorted(records)[:k]


def minimum_by_number(records, k):
    return sorted(records, key=lambda record: record[1])[:k]


def inspect(task_id, candidates):
    line_no, row = rows[task_id]
    ref = decode_reference(row)
    print(f"\n{task_id} ({source}:{line_no})")
    print("Decoded simulator reference:")
    print(ref)
    ref_cases = list(assertions(ref))
    check_cases = list(assertions(row["test_cases"]))
    for name, candidate in candidates:
        ref_ok = all(candidate(*args) == expected for args, expected in ref_cases)
        check_ok = [candidate(*args) == expected for args, expected in check_cases]
        print(f"  {name}: reference examples={ref_ok}; checked-in test_cases={check_ok}")
    for i, (args, expected) in enumerate(check_cases, 1):
        results = {name: candidate(*args) for name, candidate in candidates}
        if len(set(map(repr, results.values()))) > 1:
            print(f"  Differing test {i}: args={args!r}, expected={expected!r}, outputs={results!r}")


inspect("Mbpp/627", [("nonnegative", missing_nonnegative), ("positive", missing_positive)])
inspect("Mbpp/753", [("tuple order", minimum_by_tuple), ("numeric field", minimum_by_number)])

line_no, row = rows["Mbpp/461"]
print(f"\nMbpp/461 ({source}:{line_no}; separate source/example inconsistency)")
print("Decoded simulator reference:")
print(decode_reference(row))
for args, expected in assertions(row["test_cases"]):
    conventional_count = sum(char.isupper() for char in args[0])
    print(f"  input={args[0]!r}; count of uppercase characters={conventional_count}; checked-in expected={expected}")

print("\nScope: examples alone do not distinguish these candidate interpretations.")
print("This does not establish that a simulator cannot infer the intended rule from conventions.")

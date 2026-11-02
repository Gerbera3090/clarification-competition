#!/usr/bin/env python3
"""Register and compare completed, matched train100-v1 experiment results."""
from __future__ import annotations

import argparse
import collections
import fcntl
import hashlib
import itertools
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BENCHMARK = ROOT / ".local/train100-v1"
EXPECTED = ["LLMClarification", "Okanagan", "ClarifyGPT", "PBTClarifier1", "PBTClarifier2", "PBTClarifier3", "PBTClarifier4", "PBTClarifier5", "PBTClarifier5_1", "SpecTraceClarifier", "V1MultiJudgeClarifier", "V1_1DecisionPropertiesClarifier", "V2ConcreteSpecClarifier"]
DISPLAY = {"LLMClarification": "Direct", "Okanagan": "Okanagan", "ClarifyGPT": "ClarifyGPT",
           "PBTClarifier1": "PBT1", "PBTClarifier2": "PBT2", "PBTClarifier3": "PBT3 / CounterThenPBT",
           "PBTClarifier4": "PBT4 / PropertyConflictGate", "PBTClarifier5": "PBT5 / DecisionProperties",
           "PBTClarifier5_1": "PBT5_1 / NoSanitizer", "SpecTraceClarifier": "SpecTrace / 구조화 명세",
           "V1MultiJudgeClarifier": "v1 / multi_judge", "V1_1DecisionPropertiesClarifier": "v1_1 / decision_properties",
           "V2ConcreteSpecClarifier": "v2 / concrete_spec"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Expected JSON objects: {path}")
    return rows


def _key(row: dict) -> tuple[str, str]:
    return (str(row["task_id"]), str(row["prompt"]))


def _result_path(benchmark: Path, recorded: str) -> Path:
    """Resolve historical paths inside this checkout, preserving recorded metadata."""
    path = Path(recorded)
    if not path.is_absolute():
        return benchmark / path
    # A shared snapshot may still have the producer's absolute checkout path.
    # Prefer this benchmark even when that old checkout also exists locally.
    for index in range(len(path.parts) - 1):
        if path.parts[index:index + 2] == (".local", "train100-v1"):
            return benchmark.joinpath(*path.parts[index + 2:])
    return path


def _expected(benchmark: Path) -> tuple[dict, list[dict]]:
    manifest_path = benchmark / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for batch in manifest["batches"]:
        source = benchmark / batch["path"]
        if _sha(source) != batch["sha256"]:
            raise ValueError(f"Frozen input hash mismatch: {source}")
        rows.extend(_read(source))
    if len(rows) != 100 or len({_key(r) for r in rows}) != 100 or len({r["task_id"] for r in rows}) != 100:
        raise ValueError("Expected 100 distinct frozen tasks")
    return manifest, rows


def _validate(path: Path, expected: list[dict]) -> tuple[list[dict], str, str]:
    rows = _read(path)
    if len(rows) != 100 or len({_key(r) for r in rows}) != 100 or {_key(r) for r in rows} != {_key(r) for r in expected}:
        raise ValueError(f"Result is not a complete match for frozen train 100: {path}")
    if not all(isinstance(r.get("success"), bool) and isinstance(r.get("clarification_history"), list) for r in rows):
        raise ValueError(f"Result has unscored or incomplete entries: {path}")
    if any(len(r["clarification_history"]) > 1 or any(not isinstance(h, (list, tuple)) or len(h) < 3
           for h in r["clarification_history"]) for r in rows):
        raise ValueError(f"Result does not match the one-question benchmark protocol: {path}")
    algorithms, models = {r.get("algorithm") for r in rows}, {r.get("model") for r in rows}
    if len(algorithms) != 1 or len(models) != 1 or None in algorithms or None in models:
        raise ValueError(f"Expected one recorded algorithm and model: {path}")
    return rows, next(iter(algorithms)), next(iter(models))


def _metric(rows: list[dict]) -> dict:
    n = len(rows)
    tds = sum(math.log(10) / math.log(10 + len(r["clarification_history"])) for r in rows if r["success"]) / n
    ndcg = 0.0
    for row in rows:
        history = row["clarification_history"]
        gains = [math.log(2) / math.log(2 + i) for i in range(len(history))]
        if gains:
            ndcg += sum(gain for gain, item in zip(gains, history) if str(item[2]) == "3") / sum(gains)
    costs_present = all(isinstance(r.get(k), (int, float)) for r in rows for k in ("prompt_cost", "clarification_cost"))
    return {"pass": sum(r["success"] for r in rows), "count": n, "tds": tds, "ndcg": ndcg / n,
            "questions": sum(bool(r["clarification_history"]) for r in rows),
            "recorded_model_cost": sum(r["prompt_cost"] + r["clarification_cost"] for r in rows) if costs_present else None}


def register(benchmark: Path, path: Path, label: str | None = None) -> None:
    benchmark, path = benchmark.resolve(), path.resolve()
    _, expected = _expected(benchmark)
    rows, algorithm, model = _validate(path, expected)
    state = path.parent / "experiment.json"
    if state.exists():
        config = json.loads(state.read_text())
        if config.get("manifest_sha256") != _sha(benchmark / "manifest.json") or config.get("model") != model:
            raise ValueError("Run metadata does not match the frozen sample/model")
        provenance = {"type": "experiment", "algorithm_sha256": config.get("algorithm_sha256"),
                      "sdk_sha256": config.get("sdk_sha256")}
        if config.get("decision_model"):
            provenance["decision_model"] = config["decision_model"]
    elif path in {(benchmark / "pbt2/results.jsonl").resolve(), (benchmark / "pbt3/results.jsonl").resolve()}:
        snapshots = json.loads((benchmark / "algorithm-snapshots.json").read_text())
        snapshot_key = {"PBTClarifier2": "pbt_clarifier2", "PBTClarifier3": "pbt_clarifier3"}.get(algorithm)
        if not snapshot_key:
            raise ValueError("Unexpected historical algorithm")
        provenance = {"type": "historical", "algorithm_sha256": snapshots[snapshot_key],
                      "note": "Recorded OpenAI model; simulator used same model, default 1 turn and temperature 0.7."}
    else:
        raise ValueError("Result lacks experiment metadata; use a recorded run or preserve its configuration first")
    entry = {"label": label or path.parent.name, "algorithm": algorithm, "model": model,
             "results_path": str(path), "results_sha256": _sha(path),
             "benchmark_manifest_sha256": _sha(benchmark / "manifest.json"), "provenance": provenance}
    lock_path, registry_path = benchmark / "comparison.lock", benchmark / "comparison-registry.json"
    with lock_path.open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        reg = json.loads(registry_path.read_text()) if registry_path.exists() else {"version": 1, "entries": []}
        previous = next((x for x in reg["entries"] if x["results_path"] == str(path)), None)
        if previous:
            if previous != entry:
                raise ValueError(f"Registered result changed: {path}")
        else:
            if any(x["label"] == entry["label"] for x in reg["entries"]):
                raise ValueError(f"Run label already exists: {entry['label']}")
            reg["entries"].append(entry)
            tmp = registry_path.with_suffix(f".tmp-{os.getpid()}")
            tmp.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n")
            os.replace(tmp, registry_path)
        render(benchmark, reg, expected)


def render(benchmark: Path, registry: dict, expected: list[dict]) -> None:
    manifest_hash = _sha(benchmark / "manifest.json")
    entries = []
    for entry in registry["entries"]:
        path = _result_path(benchmark, entry["results_path"])
        if entry.get("benchmark_manifest_sha256") != manifest_hash or not path.is_file() or _sha(path) != entry["results_sha256"]:
            raise ValueError(f"Registered file or frozen sample changed: {path}")
        rows, algorithm, model = _validate(path, expected)
        if algorithm != entry["algorithm"] or model != entry["model"]:
            raise ValueError(f"Registered algorithm/model changed: {path}")
        entries.append({**entry, "metrics": _metric(rows), "rows": rows})
    strata = {r["task_id"]: (r["dataset"], r["source"]) for r in json.loads((benchmark / 'manifest.json').read_text())["tasks"]}
    lines = ["# train100-v1 동일 문제 비교", "",
             "- 동일한 train 문제 100개. HumanEval/MBPP와 원본/모순 변형 각 25개를 균형 선택했다.",
             "- 문제·출력 쌍과 샘플 해시를 검증한 결과만 표시한다. LLM/가상 사용자 설정이 다른 행은 직접 비교에 주의한다.",
             "- 한 번의 확률적 실행 결과다. 참조 설명이 있어도 가상 사용자 답변과 채점 기준이 일치한다는 보장은 없다.",
             "- train의 need_clarification 기본값은 과잉 질문률 판정에 사용하지 않는다.", "",
             "| 알고리즘 | 실행 | 모델 | 결정 모델 | 통과 | TDS | nDCG | 질문 | 모델 비용 합계 |",
             "|---|---|---|---|---:|---:|---:|---:|---:|"]
    ordered = sorted(entries, key=lambda e: (EXPECTED.index(e["algorithm"]) if e["algorithm"] in EXPECTED else len(EXPECTED), e["label"]))
    for e in ordered:
        q=e["metrics"];cost=f"${q['recorded_model_cost']:.4f}" if q['recorded_model_cost'] is not None else "미기록"
        decision_model = e.get('provenance', {}).get('decision_model') or '—'
        lines.append(f"| {DISPLAY.get(e['algorithm'], e['algorithm'])} | {e['label']} | {e['model']} | {decision_model} | {q['pass']}/100 | {q['tds']:.4f} | {q['ndcg']:.4f} | {q['questions']}/100 | {cost} |")
    for name in EXPECTED:
        if not any(e["algorithm"] == name for e in entries):
            lines.append(f"| {DISPLAY[name]} | 미완료 | — | — | — | — | — | — | — |")
    lines += ["", "비용은 완료된 결과에 기록된 에이전트와 가상 사용자 모델 비용의 합계다. 중단·실패한 호출의 청구액이나 별도 실패 분석 비용은 빠질 수 있다.", "", "## 출처별 통과", "", "| 데이터 / 출처 | 문제 수 | " + " | ".join(e['label'] for e in ordered) + " |",
              "|---|---:|" + "---:|" * len(ordered)]
    for group in sorted(set(strata.values())):
        counts=[sum(r['success'] for r in e['rows'] if strata[r['task_id']]==group) for e in ordered]
        group_size = sum(value == group for value in strata.values())
        lines.append(f"| {group[0]} / {group[1]} | {group_size} | " + " | ".join(str(x) for x in counts) + " |")
    lines += ["", "## 실행 간 짝 비교", "", "| A | B | 둘 다 통과 | A만 통과 | B만 통과 | 둘 다 실패 |",
              "|---|---|---:|---:|---:|---:|"]
    pairs = []
    for left, right in itertools.combinations(ordered, 2):
        lm, rm = ({_key(r): r for r in entry['rows']} for entry in (left, right))
        counts = collections.Counter((lm[_key(r)]['success'], rm[_key(r)]['success']) for r in expected)
        pair = {"a": left['label'], "b": right['label'], "both_pass": counts[True, True],
                "a_only": counts[True, False], "b_only": counts[False, True], "both_fail": counts[False, False]}
        pairs.append(pair)
        lines.append(f"| {pair['a']} | {pair['b']} | {pair['both_pass']} | {pair['a_only']} | {pair['b_only']} | {pair['both_fail']} |")
    lines += ["", "## 문제별 비교", "", "| 문제 | " + " | ".join(e['label'] for e in ordered) + " |",
              "|---|" + "---|" * len(ordered)]
    maps=[{_key(r):r for r in e['rows']} for e in ordered]
    for item in expected:
        k=_key(item); lines.append("| " + item['task_id'] + " | " + " | ".join("통과" if mm[k]['success'] else "실패" for mm in maps) + " |")
    lines += ["", "## 실행별 결과 파일", ""]
    for e in ordered:
        link = os.path.relpath(_result_path(benchmark, e['results_path']), benchmark)
        lines.append(f"- {e['label']}: [{e['algorithm']} 결과]({link})")
    lines += ["", "각 결과 파일에 질문과 답변·생성 코드·오류가 포함된다."]
    (benchmark / "COMPARISON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    data = [{k:v for k,v in e.items() if k != "rows"} for e in ordered]
    (benchmark / "comparison.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (benchmark / "pairwise.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--register", help="Register a fully graded result JSONL")
    parser.add_argument("--label", help="Unique human-readable run label")
    args=parser.parse_args();benchmark=Path(args.benchmark)
    try:
        if args.register:
            register(benchmark, Path(args.register), args.label)
        else:
            _, expected = _expected(benchmark)
            registry_path=benchmark/'comparison-registry.json'
            with (benchmark/'comparison.lock').open('a') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                reg=json.loads(registry_path.read_text()) if registry_path.exists() else {"version":1,"entries":[]}
                render(benchmark,reg,expected)
        print(f"Comparison: {benchmark.resolve() / 'COMPARISON.md'}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

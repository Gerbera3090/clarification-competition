#!/usr/bin/env python3
"""Run the frozen train100-v1 sample, grade, report, and optionally analyze.

Without --execute this only previews the plan. --analyze explicitly enables
additional model calls after grading. Competition source files are not modified.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / ".local/train100-v1"
SDK_FILES = ("generate_responses.py", "evaluate_responses.py", "clarify/env.py", "clarify/llm.py",
             "clarify/runtime.py", "clarify/data.py", "clarify/utils.py", "clarify/baselines/base.py", "uv.lock")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _keys(rows: list[dict]) -> set[tuple[str, str]]:
    return {(r["task_id"], r["prompt"]) for r in rows}


def _complete(path: Path, expected: list[dict], require_success: bool = False) -> bool:
    try:
        rows = _read(path)
        return (len(rows) == len(expected) and _keys(rows) == _keys(expected)
                and (not require_success or all(isinstance(r.get("success"), bool) for r in rows)))
    except (OSError, ValueError, KeyError):
        return False


def _run(command: list[str], log: Path) -> None:
    if log.exists():
        raise RuntimeError(f"Log already exists; inspect partial execution before retrying: {log}")
    with log.open("w", encoding="utf-8") as f:
        process = subprocess.run(command, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False)
    if process.returncode:
        raise RuntimeError(f"Command failed (exit {process.returncode}); see {log}")


def _local_report(path: Path, rows: list[dict]) -> None:
    n = len(rows)
    success = sum(r.get("success") is True for r in rows)
    tds = sum(math.log(10) / math.log(10 + len(r.get("clarification_history") or []))
              for r in rows if r.get("success") is True) / n if n else 0
    cost = sum(float(r.get(k, 0) or 0) for r in rows for k in ("prompt_cost", "clarification_cost"))
    lines = ["# train100-v1 실행 결과", "", f"- 통과: {success}/{n}", f"- TDS: {tds:.4f}",
             f"- 원래 모델 호출 기록 비용 합계: ${cost:.6f}",
             "- 이 표본은 균형을 맞춘 train 개발 표본이며 전체 train 성능을 대표하지 않는다.",
             "- 참조 설명이 있어도 가상 사용자 답변과 테스트 기대값이 일치한다고 보장되지 않는다.", "",
             "| 문제 | 결과 | 질문 |", "|---|---|---|"]
    for r in rows:
        h = r.get("clarification_history") or []
        question = str(h[0][0]).replace("\n", " ").replace("|", "\\|") if h else "질문 없음"
        lines.append(f"| {r.get('task_id')} | {'통과' if r.get('success') else '실패'} | {question} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithm", required=True, help="Clarifier Python file")
    parser.add_argument("--output-dir", required=True, help="New or matching experiment directory")
    parser.add_argument("--model", help="LiteLLM model; defaults to ECC_OPENAI_MODEL")
    parser.add_argument("--decision-model", help="Optional decision model passed to env.decide; e.g. openai/gpt-6-luna")
    parser.add_argument("--analysis-model", help="Model for offline post-run analysis")
    parser.add_argument("--analysis-limit", type=int, help="Limit failure analyses for a low-cost pilot")
    parser.add_argument("--pilot", type=int, help="Generate only the first 1–9 tasks; reuse them in the full run")
    parser.add_argument("--max-turns", type=int, default=1, help="Maximum clarification turns per task")
    parser.add_argument("--parallel-batches", type=int, default=1, choices=(1, 2), help="Run at most two distinct batches at once")
    parser.add_argument("--execute", action="store_true", help="Enable model calls for 100 problems")
    parser.add_argument("--analyze", action="store_true", help="After grading, make additional failure analysis calls")
    args = parser.parse_args()
    if args.max_turns < 1:
        parser.error("--max-turns must be positive")
    if args.max_turns != 1 and args.analyze:
        parser.error("--analyze currently supports single-turn traces only")
    if args.analysis_limit is not None and args.analysis_limit < 0:
        parser.error("--analysis-limit must be non-negative")
    if args.pilot is not None and not 1 <= args.pilot <= 9:
        parser.error("--pilot must be between 1 and 9")
    if args.pilot is not None and args.analyze:
        parser.error("--pilot does not grade or analyze; continue the full run without --pilot")
    if args.analyze and not args.execute:
        parser.error("--analyze requires --execute; to analyze existing results use analyze_run.py")
    if not args.analyze and (args.analysis_model is not None or args.analysis_limit is not None):
        parser.error("--analysis-model and --analysis-limit require --analyze")
    try:
        manifest_path = BENCHMARK / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        algorithm = Path(args.algorithm).resolve()
        if not algorithm.is_file():
            raise ValueError(f"Algorithm file not found: {algorithm}")
        batches = []
        for entry in manifest["batches"]:
            path = BENCHMARK / entry["path"]
            if _sha(path) != entry["sha256"]:
                raise ValueError(f"Frozen batch hash mismatch: {path}")
            batches.append((path, _read(path)))
        if sum(len(rows) for _, rows in batches) != 100:
            raise ValueError("Expected 100 frozen benchmark records")
        if len({r["task_id"] for _, rows in batches for r in rows}) != 100:
            raise ValueError("Frozen benchmark must contain 100 distinct task IDs")
        model = args.model or os.environ.get("ECC_OPENAI_MODEL") or "openai/gpt-4.1-mini"
        output = Path(args.output_dir).resolve()
        print(f"Plan: {len(batches)} batches / 100 train problems; model={model}; output={output}")
        print(f"Maximum clarification turns: {args.max_turns}")
        if args.decision_model:
            print(f"Decision model: {args.decision_model}")
        if args.pilot is not None:
            print(f"Pilot: generate {args.pilot} problems; the full run can reuse these outputs.")
        print("The algorithm may make multiple model calls per problem; generation and simulated users incur costs.")
        if not args.execute:
            print("Preview only: no generation, grading, or model calls. Add --execute to run.")
            return 0
        if shutil.which("docker") is None or subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL,
                                                              stderr=subprocess.DEVNULL).returncode:
            raise RuntimeError("Docker is unavailable; start Docker Desktop before the paid run.")
        output.mkdir(parents=True, exist_ok=True)
        state_path, snapshot = output / "experiment.json", output / "algorithm.py"
        sdk_hashes = {name: _sha(ROOT / name) for name in SDK_FILES}
        state = {"algorithm_source": str(algorithm), "algorithm_sha256": _sha(algorithm),
                 "manifest_sha256": _sha(manifest_path), "model": model, "split": "train",
                 "sdk_sha256": sdk_hashes, "format_version": 1}
        if args.decision_model:
            state["decision_model"] = args.decision_model
        if args.max_turns != 1:
            state["max_clarification_turns"] = args.max_turns
        if state_path.exists():
            if json.loads(state_path.read_text()) != state or not snapshot.exists() or _sha(snapshot) != state["algorithm_sha256"]:
                raise ValueError("Existing run has a different algorithm, sample, or model; use another output directory.")
        else:
            if any(output.iterdir()):
                raise ValueError("Output directory is not empty and lacks experiment metadata.")
            shutil.copyfile(algorithm, snapshot)
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        decision_args = ["--decision_model", args.decision_model] if args.decision_model else []
        decision_args += ["--max_clarification_turns", str(args.max_turns)]
        if args.pilot is not None:
            expected = batches[0][1][:args.pilot]
            pilot_input, pilot_output, pilot_log = (output / "pilot-benchmark.jsonl", output / "pilot-output.jsonl",
                                                    output / "pilot-generate.log")
            content = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in expected)
            if pilot_input.exists() and pilot_input.read_text() != content:
                raise ValueError("Existing pilot selects different inputs; use another output directory.")
            if not pilot_input.exists():
                pilot_input.write_text(content, encoding="utf-8")
            if pilot_output.exists():
                if not _complete(pilot_output, expected):
                    raise RuntimeError(f"Incomplete pilot; review before resuming: {pilot_output}")
            else:
                print(f"Generating pilot: {len(expected)} problems", flush=True)
                _run([sys.executable, str(ROOT / "generate_responses.py"), str(snapshot),
                      "--dataset_path", str(pilot_input), "--output_path", str(pilot_output),
                      "--language_model", model, "--clarification_model", model,
                      "--fail_on_exception=True", "--max_workers", "1"] + decision_args, pilot_log)
                if not _complete(pilot_output, expected):
                    raise RuntimeError(f"Pilot did not complete: {pilot_output}")
            print(f"Pilot output saved: {pilot_output}; continue without --pilot to reuse it.")
            return 0
        def generate_batch(index: int, input_path: Path, expected: list[dict]) -> list[dict]:
            if any(_sha(ROOT / name) != digest for name, digest in sdk_hashes.items()):
                raise RuntimeError("SDK files changed during execution; preserve outputs and inspect before resuming.")
            name = input_path.stem
            result, log = output / f"{name}-output.jsonl", output / f"{name}-generate.log"
            if result.exists():
                if not _complete(result, expected):
                    raise RuntimeError(f"Partial or mismatched result; review before resuming: {result}")
            elif index == 1 and (output / "pilot-output.jsonl").exists():
                pilot_input, pilot_output = output / "pilot-benchmark.jsonl", output / "pilot-output.jsonl"
                pilot_rows = _read(pilot_input)
                if not 1 <= len(pilot_rows) < len(expected) or _keys(pilot_rows) != _keys(expected[:len(pilot_rows)]) or not _complete(pilot_output, pilot_rows):
                    raise ValueError("Existing pilot does not match the first frozen batch.")
                pilot_keys = _keys(pilot_rows)
                remaining = [row for row in expected if (row['task_id'], row['prompt']) not in pilot_keys]
                rest_input = output / f"{name}-remaining-benchmark.jsonl"
                rest_result = output / f"{name}-remaining-output.jsonl"
                rest_log = output / f"{name}-remaining-generate.log"
                content = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in remaining)
                if rest_input.exists() and rest_input.read_text() != content:
                    raise ValueError("Existing pilot remainder does not match frozen inputs.")
                if not rest_input.exists():
                    rest_input.write_text(content, encoding="utf-8")
                if rest_result.exists():
                    if not _complete(rest_result, remaining):
                        raise RuntimeError(f"Incomplete pilot remainder; review before resuming: {rest_result}")
                else:
                    print(f"Generating batch {index}/{len(batches)}: {name} ({len(remaining)} remaining)", flush=True)
                    _run([sys.executable, str(ROOT / "generate_responses.py"), str(snapshot),
                          "--dataset_path", str(rest_input), "--output_path", str(rest_result),
                          "--language_model", model, "--clarification_model", model,
                          "--fail_on_exception=True", "--max_workers", "1"] + decision_args, rest_log)
                    if not _complete(rest_result, remaining):
                        raise RuntimeError(f"Pilot remainder did not complete: {rest_result}")
                found = {_key: row for row in (_read(pilot_output) + _read(rest_result))
                         for _key in [(row['task_id'], row['prompt'])]}
                result.write_text(''.join(json.dumps(found[(r['task_id'], r['prompt'])], ensure_ascii=False) + '\n' for r in expected), encoding='utf-8')
            else:
                print(f"Generating batch {index}/{len(batches)}: {name}", flush=True)
                _run([sys.executable, str(ROOT / "generate_responses.py"), str(snapshot),
                      "--dataset_path", str(input_path), "--output_path", str(result),
                      "--language_model", model, "--clarification_model", model,
                      "--fail_on_exception=True", "--max_workers", "1"] + decision_args, log)
                if not _complete(result, expected):
                    raise RuntimeError(f"Generation did not complete: {result}")
            return _read(result)
        # Separate batches have separate files and logs; preserve manifest order.
        collected: dict[int, list[dict]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel_batches) as pool:
            pending_batches = iter(enumerate(batches, 1))
            futures = {}
            def submit_next() -> bool:
                item = next(pending_batches, None)
                if item is None:
                    return False
                i, (path, rows) = item
                futures[pool.submit(generate_batch, i, path, rows)] = i
                return True
            for _ in range(args.parallel_batches):
                submit_next()
            try:
                while futures:
                    done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                    for future in done:
                        index = futures.pop(future)
                        collected[index] = future.result()
                    for _ in done:
                        submit_next()
            except BaseException:
                for future in futures:
                    future.cancel()
                raise
        all_rows = [row for index in sorted(collected) for row in collected[index]]
        combined = output / "all-output.jsonl"
        serialized = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_rows)
        if combined.exists() and combined.read_text() != serialized:
            raise ValueError("Existing combined generation differs; refusing to overwrite.")
        if not combined.exists():
            combined.write_text(serialized, encoding="utf-8")
        results, log = output / "results.jsonl", output / "evaluate.log"
        if any(_sha(ROOT / name) != digest for name, digest in sdk_hashes.items()):
            raise RuntimeError("SDK files changed before grading; preserve outputs and inspect before resuming.")
        if results.exists():
            if not _complete(results, all_rows, require_success=True):
                raise RuntimeError(f"Partial or mismatched evaluation; review before resuming: {results}")
        else:
            print("Grading 100 responses locally with Docker", flush=True)
            _run([sys.executable, str(ROOT / "evaluate_responses.py"), "--split", "train",
                  "--generation_path", str(combined), "--output_path", str(results),
                  "--max_workers", "1"], log)
            if not _complete(results, all_rows, require_success=True):
                raise RuntimeError(f"Evaluation did not complete: {results}")
        _local_report(output / "REPORT.md", _read(results))
        print(f"Saved local run report: {output / 'REPORT.md'}", flush=True)
        if args.max_turns == 1:
            print("Registering the completed run in the matched train100 comparison", flush=True)
            comparison = subprocess.run([sys.executable, str(ROOT / "experiment_tools/compare_train100.py"),
                                         "--benchmark", str(BENCHMARK), "--register", str(results),
                                         "--label", output.name], cwd=ROOT, check=False)
            if comparison.returncode:
                raise RuntimeError("Comparison registration failed; the graded results remain saved.")
        else:
            print("Multi-turn run: kept separate from the single-turn comparison registry.", flush=True)
        if args.analyze:
            command = [sys.executable, str(ROOT / "experiment_tools/analyze_run.py"),
                       "--results", str(results), "--trace-dir", str(output),
                       "--output-dir", str(output / "analysis"), "--analyze",
                       "--model", args.analysis_model or model]
            if args.analysis_limit is not None:
                command += ["--limit", str(args.analysis_limit)]
            print("Starting additional model-based failure analysis", flush=True)
            return subprocess.run(command, cwd=ROOT, check=False).returncode
        print("No post-run LLM calls: add --analyze to enable failure analysis.")
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

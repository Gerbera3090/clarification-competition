"""Build an offline source inventory for a subsequent semantic single-question audit.

No questions or sufficiency claims are inferred from textual differences. Every raw
benchmark row is retained, including rows the SDK would skip or overwrite. This
script never calls a model, fetches a dataset, or executes benchmark solutions.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def read_jsonl(path: Path):
    result = []
    for line_no, raw in enumerate(path.read_bytes().splitlines(keepends=True), 1):
        if raw.strip():
            result.append((line_no, raw, json.loads(raw)))
    return result


def dump(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snippet(value, limit=12000):
    if value is None:
        return None
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, default=repr)
    return {"text": value if len(value) <= limit else value[:limit],
            "full_sha256": sha(value), "full_characters": len(value),
            "truncated": len(value) > limit}


def count_inputs(value):
    return len(value) if isinstance(value, (list, tuple, dict)) else None


def load_official_local():
    """Resolve the installed EvalPlus default cache without calling cache/download helpers."""
    import evalplus
    import evalplus.data.humaneval as human
    import evalplus.data.mbpp as mbpp
    from evalplus.data.utils import get_dataset_metadata
    from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS, MBPP_OUTPUT_SET_EQ_TASKS

    specs = [
        ("HumanEval", human.HUMANEVAL_OVERRIDE_PATH, "HumanEvalPlus", human.HUMANEVAL_PLUS_VERSION),
        ("Mbpp", mbpp.MBPP_OVERRIDE_PATH, "MbppPlus", mbpp.MBPP_PLUS_VERSION),
    ]
    datasets, sources, metadata = {}, {}, {}
    for family, override, name, version in specs:
        _, default_path = get_dataset_metadata(name, version, False, False)
        path = Path(override or default_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Offline EvalPlus cache missing: {path}; no download attempted")
        rows = read_jsonl(path)
        datasets[family] = {x["task_id"]: x for _, _, x in rows}
        sources[family] = {x["task_id"]: {"path": str(path), "line": line_no,
                            "raw_line_sha256": sha(raw)} for line_no, raw, x in rows}
        metadata[family] = {"path": str(path), "version": version,
                            "sha256": sha(path.read_bytes()), "rows": len(rows)}
        if family == "Mbpp":
            for task_id, task in datasets[family].items():
                task["base_input"] = mbpp.mbpp_deserialize_inputs(task_id, task["base_input"])
                task["plus_input"] = mbpp.mbpp_deserialize_inputs(task_id, task["plus_input"])
    return datasets, sources, {"package_path": evalplus.__file__, "caches": metadata}, {
        "output_not_none_entry_points": sorted(MBPP_OUTPUT_NOT_NONE_TASKS),
        "output_set_eq_entry_points": sorted(MBPP_OUTPUT_SET_EQ_TASKS),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    official, official_sources, official_meta, oracle_meta = load_official_local()
    spec = importlib.util.spec_from_file_location("audit_sdk_data", root / "clarify/data.py")
    sdk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sdk)
    # SDK preprocess mutates its input and the dictionaries returned by getters.
    # A pristine deep copy per file prevents earlier prompt variants from leaking
    # into later variants' reference_prompt or other metadata.
    sdk.get_human_eval_plus = lambda: copy.deepcopy(official["HumanEval"])
    sdk.get_mbpp_plus = lambda: copy.deepcopy(official["Mbpp"])

    split_files = {"train": root / "data/splits/train.txt", "val": root / "data/splits/validation.txt"}
    split_ids = {name: set(path.read_text().splitlines()) for name, path in split_files.items()}
    split_metadata = {name: {"path": str(path.relative_to(root)),
                            "sha256": sha(path.read_bytes()), "task_ids": len(split_ids[name])}
                      for name, path in split_files.items()}
    clarification_path = root / "data/clarifications.jsonl"
    clarification_rows = read_jsonl(clarification_path) if clarification_path.is_file() else []
    overlay = {(r["task_id"], r["prompt"]): (line_no, r["clarifications"])
               for line_no, _, r in clarification_rows}
    overlay_groups = defaultdict(list)
    for line_no, _, row in clarification_rows:
        overlay_groups[(row["task_id"], row["prompt"])].append({"line": line_no, "clarifications": row["clarifications"]})
    overlay_duplicate_keys = [{"task_id": task_id, "prompt_sha256": sha(prompt),
                               "entries": entries,
                               "exact_payloads_differ": any(e["clarifications"] != entries[-1]["clarifications"] for e in entries[:-1]),
                               "effective_line": entries[-1]["line"]}
                              for (task_id, prompt), entries in overlay_groups.items() if len(entries) > 1]

    source_files = sorted((root / "data/humaneval").glob("*.jsonl")) + sorted((root / "data/mbpp").glob("*.jsonl"))
    records, file_inventory, seen_ids = [], [], set()
    for path in source_files:
        relative = str(path.relative_to(root))
        rows = read_jsonl(path)
        raw_data = [copy.deepcopy(row) for _, _, row in rows]
        processed = sdk.preprocess_benchmark(raw_data)
        last_usable_line = {}
        for line_no, _, row in rows:
            if row.get("prompt"):
                last_usable_line[row["task_id"]] = line_no
        file_stats = Counter()
        for line_no, raw_bytes, raw in rows:
            task_id = raw["task_id"]
            family = task_id.split("/", 1)[0]
            seen_ids.add(task_id)
            memberships = [name for name, ids in split_ids.items() if task_id in ids]
            usable = bool(raw.get("prompt")) and last_usable_line.get(task_id) == line_no
            if usable:
                # This row is read-only below; the enclosing per-file preprocess
                # already owns deep copies of both raw and official dictionaries.
                task = processed[task_id]
                exclusion = None
            else:
                # Preserve all rows without implying the SDK would deliver them.
                task = copy.deepcopy(raw)
                if isinstance(task.get("reference_prompt"), str) and task["reference_prompt"].startswith("REF_"):
                    task["reference_prompt"] = zlib.decompress(base64.b64decode(task["reference_prompt"][4:])).decode()
                if family == "Mbpp" and task.get("prompt"):
                    task["prompt"] = task["prompt"].strip() + "\n"
                exclusion = "empty_prompt" if not raw.get("prompt") else "overwritten_task_id_in_source"
            prompt = task.get("prompt")
            prompt_hash = sha(prompt) if isinstance(prompt, str) else sha(json.dumps(prompt))
            raw_prompt = raw.get("prompt")
            row_key = f"{relative}::{task_id}::{prompt_hash}"
            source = {"path": relative, "line": line_no}
            official_task = official[family].get(task_id)
            official_source = official_sources[family].get(task_id)

            if "reference_prompt" in raw:
                reference_source = {**source, "field": "reference_prompt",
                                    "encoding": "base64+zlib" if str(raw["reference_prompt"]).startswith("REF_") else "plain"}
            elif official_task:
                reference_source = {**official_source, "field": "prompt", "kind": "official_evalplus_fallback"}
            else:
                reference_source = None
            reference_prompt = task.get("reference_prompt")

            overlay_entry = overlay.get((task_id, prompt))
            if overlay_entry:
                effective_clarifications = copy.deepcopy(overlay_entry[1])
                hidden_source = {"kind": "clarifications_overlay", "path": "data/clarifications.jsonl",
                                 "line": overlay_entry[0], "field": "clarifications",
                                 "match": "exact task_id + SDK-processed prompt"}
                hidden_payload = effective_clarifications
            elif "clarifications" in task:
                effective_clarifications = task["clarifications"]
                hidden_source = {"kind": "source_clarifications", **source, "field": "clarifications"}
                hidden_payload = effective_clarifications
            else:
                effective_clarifications = None
                hidden_source = {"kind": "reference_prompt" if reference_prompt is not None else "absent_redacted",
                                 "reference": reference_source}
                hidden_payload = reference_prompt

            if official_task:
                evaluation_task = official_task
                tests_source = {"kind": "official_evalplus", **official_source,
                                "authority": "clarify/runtime.py:init_evalplus_evaluator",
                                "expected_outputs": "EvalPlus get_groundtruth(canonical_solution + official prompt, inputs)",
                                "entry_point": task.get("entry_point")}
                special_oracle = []
                official_entry = official_task.get("entry_point")
                if official_entry in oracle_meta["output_not_none_entry_points"]:
                    special_oracle.append("output_not_none")
                if official_entry in oracle_meta["output_set_eq_entry_points"]:
                    special_oracle.append("output_set_eq")
                if official_entry == "are_equivalent":
                    special_oracle.append("always_true_are_equivalent")
                if official_entry == "sum_div":
                    special_oracle.append("accept_zero_sum_div")
            else:
                evaluation_task = task
                tests_source = {"kind": "raw_test_cases", **source, "field": "test_cases",
                                "authority": "clarify/runtime.py:init_evalplus_evaluator missing_entries fallback",
                                "entry_point": task.get("entry_point")}
                special_oracle = []
            tests = {
                "source": tests_source,
                "base_input_count": count_inputs(evaluation_task.get("base_input")),
                "plus_input_count": count_inputs(evaluation_task.get("plus_input")),
                "canonical_solution": snippet(evaluation_task.get("canonical_solution")),
                "test_cases": snippet(evaluation_task.get("test_cases")),
                "raw_source_test_cases": snippet(raw.get("test_cases")),
                "contract": snippet(evaluation_task.get("contract")),
                "atol": evaluation_task.get("atol", 0),
                "special_oracle": special_oracle,
                "official_entry_point_for_oracle": evaluation_task.get("entry_point"),
                "oracle_selection_source": "clarify/runtime.py:EvalPlusDockerInstanceEvaluator._oracle",
            }
            record = {
                "row_key": row_key, "source_file": relative, "source_line": line_no,
                "source_variant": path.stem, "dataset_family": family, "split": memberships[0] if len(memberships) == 1 else "outside" if not memberships else "overlap",
                "split_memberships": memberships, "task_id": task_id,
                "sdk_preprocess_usable": usable, "sdk_exclusion_reason": exclusion,
                "prompt": prompt, "prompt_sha256": prompt_hash,
                "raw_prompt_sha256": sha(raw_prompt) if isinstance(raw_prompt, str) else None,
                "prompt_changed_by_preprocess": prompt != raw_prompt,
                "entry_point": task.get("entry_point"),
                "reference_prompt": reference_prompt, "reference_prompt_source": reference_source,
                "hidden_requirements_source": hidden_source,
                "effective_hidden_requirements": hidden_payload,
                "effective_clarifications": effective_clarifications,
                "tests": tests,
                "raw_line_sha256": sha(raw_bytes), "raw_line_hash_includes_line_ending": True,
                "raw_json_sha256": sha(json.dumps(raw, sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
                "annotation_status": "pending",
                "annotation_note": "Individual semantic review and test sufficiency verification required; no question inferred by this inventory.",
            }
            records.append(record)
            file_stats["raw_rows"] += 1
            file_stats["sdk_usable_rows" if usable else "sdk_excluded_rows"] += 1
            file_stats[f"raw_{record['split']}_rows"] += 1
            if usable:
                file_stats[f"usable_{record['split']}_rows"] += 1
        file_inventory.append({"path": relative, "sha256": sha(path.read_bytes()),
                               "unique_task_ids": len({row[2]["task_id"] for row in rows}), **file_stats})

    groups = defaultdict(list)
    text_groups = defaultdict(list)
    for record in records:
        if record["sdk_preprocess_usable"]:
            groups[(record["task_id"], record["prompt_sha256"])].append(record["row_key"])
            text_groups[record["prompt_sha256"]].append(record["row_key"])
    for record in records:
        group = groups.get((record["task_id"], record["prompt_sha256"]), [])
        record["same_task_exact_prompt_group_size"] = len(group)
        record["same_task_exact_prompt_duplicate_row_keys"] = [k for k in group if k != record["row_key"]]
        record["exact_prompt_group_size_across_task_ids"] = len(text_groups.get(record["prompt_sha256"], []))

    index_path = out / "corpus-index.jsonl"
    with index_path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    usable = [r for r in records if r["sdk_preprocess_usable"]]
    counts = Counter(r["split"] for r in records)
    usable_counts = Counter(r["split"] for r in usable)
    match_counts = Counter(r["hidden_requirements_source"]["kind"] for r in usable)
    inventory = {
        "scope": "All raw rows in data/humaneval/*.jsonl and data/mbpp/*.jsonl; SDK split loader scope, including originals and every variant",
        "schema_version": 1,
        "root": str(root), "preprocess_source": "clarify/data.py", "preprocess_source_sha256": sha((root / "clarify/data.py").read_bytes()),
        "runtime_source_sha256": sha((root / "clarify/runtime.py").read_bytes()),
        "environment_source_sha256": sha((root / "clarify/env.py").read_bytes()),
        "generation_source_sha256": sha((root / "generate_responses.py").read_bytes()),
        "preprocess_isolation": "deepcopy raw source rows and pristine official EvalPlus dictionaries per source file; exact SDK preprocessing function",
        "offline": True, "model_calls": 0, "solution_or_test_execution": False,
        "source_file_count": len(source_files), "raw_row_count": len(records),
        "sdk_usable_row_count": len(usable), "sdk_excluded_row_count": len(records) - len(usable),
        "raw_rows_by_split": dict(counts), "sdk_usable_rows_by_split": dict(usable_counts),
        "unique_task_ids": len(seen_ids), "unique_task_ids_by_split": {name: len(ids & seen_ids) for name, ids in split_ids.items()},
        "split_task_id_intersection": sorted(split_ids["train"] & split_ids["val"]),
        "split_task_id_disjoint": not bool(split_ids["train"] & split_ids["val"]),
        "unused_split_task_ids": {name: sorted(ids - seen_ids) for name, ids in split_ids.items()},
        "unique_task_and_exact_processed_prompt_pairs": len(groups),
        "unique_exact_processed_prompt_texts": len(text_groups),
        "same_task_exact_prompt_duplicate_groups": sum(len(g) > 1 for g in groups.values()),
        "same_task_exact_prompt_duplicate_excess_rows": sum(max(0, len(g) - 1) for g in groups.values()),
        "unique_task_and_prompt_pairs_by_split": {name: len({(r["task_id"], r["prompt_sha256"]) for r in usable if name in r["split_memberships"]}) for name in split_ids},
        "processed_prompt_changed_rows": sum(r["prompt_changed_by_preprocess"] for r in records),
        "effective_hidden_requirements_source_counts": dict(match_counts),
        "reference_prompt_absent_rows": sum(r["reference_prompt"] is None for r in usable),
        "test_source_counts": dict(Counter(r["tests"]["source"]["kind"] for r in usable)),
        "annotation_status_counts": dict(Counter(r["annotation_status"] for r in usable)),
        "readme_claim": {"train": 7961, "val": 770, "total": 8731},
        "readme_comparison": {"raw_matches_train": counts["train"] == 7961,
                              "raw_matches_val": counts["val"] == 770,
                              "usable_matches_train": usable_counts["train"] == 7961,
                              "usable_matches_val": usable_counts["val"] == 770,
                              "interpretation": "README counts source-variant rows, not distinct task IDs or distinct task+prompt pairs. SDK preprocessing is applied independently to each source file."},
        "split_files": split_metadata, "files": file_inventory, "evalplus": official_meta,
        "clarifications_overlay": {"path": "data/clarifications.jsonl", "sha256": sha(clarification_path.read_bytes()) if clarification_path.is_file() else None,
                                   "raw_rows": len(clarification_rows), "unique_exact_keys": len(overlay),
                                   "duplicate_keys": overlay_duplicate_keys,
                                   "matching_usable_source_rows": match_counts["clarifications_overlay"],
                                   "semantics": "last identical (task_id, prompt) key wins; exact match against SDK-processed prompt, as in generate_responses.py"},
        "index": {"path": str(index_path), "sha256": sha(index_path.read_bytes()), "rows": len(records),
                  "row_key": "source_file :: task_id :: SHA256(exact SDK-processed prompt)",
                  "no_omission_check": len(records) == sum(f["raw_rows"] for f in file_inventory)},
        "limits": ["Inventory only: all individual single-question semantic annotations remain pending.",
                   "Test/canonical snippets are context, not executed proof that a question is necessary or sufficient.",
                   "EvalPlus cached canonical prompt/solution and inputs define official task tests; raw variant test_cases may differ.",
                   "An absent reference_prompt means the simulator falls back to [REDACTED] unless exact clarifications overlay matches.",
                   "Source-variant identity is retained even when its exact prompt is duplicated in another file."],
        "special_oracle_row_counts": dict(Counter(oracle for row in usable for oracle in row["tests"]["special_oracle"])),
    }
    assert len({r["row_key"] for r in records}) == len(records), "row_key collision; inspect source duplicates"
    assert inventory["index"]["no_omission_check"]
    dump(out / "corpus-inventory.json", inventory)
    print(json.dumps({k: inventory[k] for k in ("source_file_count", "raw_row_count", "sdk_usable_row_count", "raw_rows_by_split", "unique_task_ids", "unique_task_and_exact_processed_prompt_pairs", "effective_hidden_requirements_source_counts", "reference_prompt_absent_rows", "test_source_counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

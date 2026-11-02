"""Build a reproducible, reference-bearing, balanced train benchmark.

This is an experimental data-selection script, not a submitted algorithm.
Do not pass reference_prompt or tests to participant algorithms.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from clarify.data import load_split, preprocess_benchmark

DEST = Path(__file__).resolve().parent
SEED = 20261030
PER_STRATUM = 25
SOURCES = [
    ("humaneval", "original"),
    ("humaneval", "larbi_contradictory"),
    ("mbpp", "original"),
    ("mbpp", "larbi_contradictory"),
]


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    if (DEST / "manifest.json").exists():
        raise SystemExit("Manifest already exists; preserve the frozen sample.")
    train = set((ROOT / "data/splits/train.txt").read_text().splitlines())
    valid = set((ROOT / "data/splits/validation.txt").read_text().splitlines())
    if train & valid:
        raise ValueError("Train and validation task IDs overlap.")
    rng, used, selected, manifest = random.Random(SEED), set(), [], []
    for dataset, variant in SOURCES:
        source = ROOT / f"data/{dataset}/{dataset}_{variant}.jsonl"
        raw = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
        rows = preprocess_benchmark(raw).values()
        candidates = sorted(
            (r for r in rows if r["task_id"] in train and r["task_id"] not in used
             and isinstance(r.get("reference_prompt"), str)
             and r["reference_prompt"].strip() not in {"", "[REDACTED]"}),
            key=lambda r: r["task_id"],
        )
        if len(candidates) < PER_STRATUM:
            raise ValueError(f"Not enough eligible inputs in {source}: {len(candidates)}")
        for r in rng.sample(candidates, PER_STRATUM):
            used.add(r["task_id"])
            selected.append(r)
            manifest.append({
                "task_id": r["task_id"], "dataset": dataset, "source": variant,
                "source_file": str(source.relative_to(ROOT)),
                "prompt_sha256": digest(r["prompt"]),
                "reference_sha256": digest(r["reference_prompt"]),
                "reference_present": True,
            })

    if len(selected) != 100 or len(used) != 100:
        raise ValueError("Expected exactly 100 distinct training task IDs.")
    # Validate every selected prompt belongs to the official training split.
    split_keys = {(r["task_id"], r["prompt"]) for r in load_split(str(ROOT / 'data/splits/train.txt'))}
    if any((r["task_id"], r["prompt"]) not in split_keys for r in selected):
        raise ValueError("A selected prompt was not found in the official train split.")

    batches = []
    for dataset in ("humaneval", "mbpp"):
        subset = [r for r, m in zip(selected, manifest) if m["dataset"] == dataset]
        rng.shuffle(subset)
        for i in range(5):
            chunk = subset[i * 10:(i + 1) * 10]
            path = DEST / "batches" / f"{dataset}-{i + 1:02d}.jsonl"
            path.write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in chunk))
            reread = [json.loads(line) for line in path.read_text().splitlines()]
            checked = list(preprocess_benchmark(reread).values())
            expected = {(r["task_id"], r["prompt"], r["reference_prompt"]) for r in chunk}
            actual = {(r["task_id"], r["prompt"], r["reference_prompt"]) for r in checked}
            if expected != actual:
                raise ValueError(f"Reprocessing changed prompt or reference in {path}")
            batches.append({"path": str(path.relative_to(DEST)), "sha256": digest(path.read_text()),
                            "tasks": [r["task_id"] for r in chunk]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = {"name": "train100-v1", "split": "train", "seed": SEED,
              "selection": "25 per dataset and original/contradictory stratum; distinct task IDs; reference required",
              "repo_commit": commit, "tasks": manifest, "batches": batches}
    (DEST / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("Frozen 100 examples:", dict(Counter((m["dataset"], m["source"]) for m in manifest)))
    print("Ten batches; all 100 IDs belong to train, are distinct, and have a reference prompt.")


if __name__ == "__main__":
    main()

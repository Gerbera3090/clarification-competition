"""Snapshot and deduplicate existing local evaluated failures; no model calls."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    paths = sorted(p for p in (ROOT / ".local").rglob("*.jsonl")
                   if "result" in p.name and OUT not in p.parents)
    inventory = []
    records: dict[str, dict] = {}
    for path in paths:
        data = path.read_bytes()
        stats = Counter()
        for line_no, line in enumerate(data.decode().splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            stats["rows"] += 1
            stats["passed" if row.get("success") is True else
                  "failed" if row.get("success") is False else "unscored"] += 1
            history = row.get("clarification_history") or []
            good = any(isinstance(h, (list, tuple)) and len(h) > 2 and str(h[2]) == "3"
                       for h in history)
            if not (row.get("success") is False and good):
                continue
            stats["selected"] += 1
            # Exact record duplicates are merged; source locations are retained.
            digest = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            source = {"path": str(path), "line": line_no}
            if digest not in records:
                records[digest] = {"record_sha256": digest, "row": row, "sources": []}
            records[digest]["sources"].append(source)
        inventory.append({"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), **stats})

    cases = []
    for index, record in enumerate(records.values(), 1):
        row = record["row"]
        algorithm = row.get("algorithm", "unknown")
        group = {"PBTClarifier2": "pbt2", "PBTClarifier3": "pbt3",
                 "PBTClarifier1": "pbt1", "Okanagan": "okanagan",
                 "ClarifyGPT": "clarifygpt"}.get(algorithm, "other")
        # Prefer a merged results file when providing the main clickable source.
        source = min(record["sources"], key=lambda s: (Path(s["path"]).name != "results.jsonl", len(s["path"])))
        cases.append({"case_id": f"CF{index:03d}", "group": group,
                      "record_sha256": record["record_sha256"], "source": source,
                      "all_sources": record["sources"], **row})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cases.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases))
    for group in sorted({c["group"] for c in cases}):
        (OUT / f"input-{group}.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n"
                                                        for c in cases if c["group"] == group))
    dump(OUT / "inventory.json", {"scope": "existing evaluated local experiment result files under .local; bundled leaderboard files excluded",
                                 "selection": "success is false and at least one clarification_history entry has quality 3",
                                 "deduplication": "identical complete JSON result records only; retain all source locations",
                                 "files": inventory, "selected_source_rows": sum(i.get("selected", 0) for i in inventory),
                                 "unique_selected_records": len(cases),
                                 "groups": dict(Counter(c["group"] for c in cases))})
    print(json.dumps({"files": len(paths), "selected_source_rows": sum(i.get("selected", 0) for i in inventory),
                      "unique_selected_records": len(cases), "groups": dict(Counter(c["group"] for c in cases))}, ensure_ascii=False))


if __name__ == "__main__":
    main()

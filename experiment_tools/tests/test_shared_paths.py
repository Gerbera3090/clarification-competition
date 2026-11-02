import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare_train100


class SharedBenchmarkTests(unittest.TestCase):
    def test_comparison_uses_the_shared_copy_even_if_the_original_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "original/.local/train100-v1"
            shared = root / "shared/.local/train100-v1"
            original.mkdir(parents=True)
            shared.mkdir(parents=True)
            rows = [{"task_id": str(i), "prompt": f"task {i}", "success": True,
                     "clarification_history": [], "algorithm": "demo", "model": "fake",
                     "prompt_cost": 0.0, "clarification_cost": 0.0} for i in range(100)]
            result = shared / "run/results.jsonl"
            result.parent.mkdir()
            result.write_text("".join(json.dumps(row) + "\n" for row in rows))
            old_result = original / "run/results.jsonl"
            old_result.parent.mkdir()
            old_result.write_text("wrong file from another checkout")
            manifest = shared / "manifest.json"
            manifest.write_text(json.dumps({"tasks": [
                {"task_id": row["task_id"], "dataset": "demo", "source": "original"}
                for row in rows
            ]}))
            registry = {"entries": [{"label": "shared", "results_path": str(old_result),
                "results_sha256": compare_train100._sha(result), "algorithm": "demo",
                "model": "fake", "benchmark_manifest_sha256": compare_train100._sha(manifest)}]}
            compare_train100.render(shared, registry, rows)
            report = (shared / "COMPARISON.md").read_text()
            self.assertIn("100/100", report)
            self.assertIn("](run/results.jsonl)", report)
            self.assertNotIn(str(original), report)
            self.assertEqual(old_result.read_text(), "wrong file from another checkout")

    def test_relative_and_unrelated_absolute_paths_are_preserved(self):
        benchmark = Path("/shared/.local/train100-v1")
        self.assertEqual(compare_train100._result_path(benchmark, "run/results.jsonl"),
                         benchmark / "run/results.jsonl")
        self.assertEqual(compare_train100._result_path(benchmark, "/external/results.jsonl"),
                         Path("/external/results.jsonl"))


if __name__ == "__main__":
    unittest.main()

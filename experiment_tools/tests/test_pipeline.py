import argparse
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_run
import compare_train100
import run_train100


def _row(task, success):
    return {"task_id": task, "prompt": f"Implement task {task} with a clear description.",
            "success": success, "clarification_history": [], "prompt_result": "def f(): pass",
            "test_result": "test failed" if not success else "passed", "prompt_cost": 0.01,
            "clarification_cost": 0.0}


CASE = {"category": "interface", "observations": ["인자가 다름"], "hypotheses": ["명세 부족"],
        "next_step": "인터페이스 확인", "confidence": "medium"}
SUMMARY = {"overview": "실패 분석", "patterns": ["인터페이스"],
           "recommendations": ["시그니처 확인"], "limitations": ["표본 작음"]}


class AnalysisTests(unittest.TestCase):
    def test_preview_no_calls_then_one_per_failure_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "result.jsonl"
            result.write_text("".join(json.dumps(r) + "\n" for r in [_row("A", False), _row("B", True), _row("C", False)]))
            args = argparse.Namespace(results=str(result), trace_dir=None, output_dir=str(root / "analysis"),
                                      model="fake/model", limit=None, analyze=False)
            with patch.object(analyze_run, "_call") as call, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(analyze_run.analyze(args), 0)
                call.assert_not_called()
                self.assertFalse((root / "analysis").exists())
            payloads = []
            def fake_call(model, system, payload):
                payloads.append(payload)
                return json.dumps(SUMMARY if "run_statistics" in payload else CASE), 0.001, {"input": 10, "output": 5}
            args.analyze = True
            with patch.object(analyze_run, "_call", side_effect=fake_call), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(analyze_run.analyze(args), 0)
                self.assertEqual(len(payloads), 3)
                self.assertEqual({payloads[0]["task_id"], payloads[1]["task_id"]}, {"A", "C"})
                self.assertEqual(payloads[2]["run_statistics"]["total"], 3)
                self.assertEqual([x["task_id"] for x in payloads[2]["successful_case_summaries"]], ["B"])
                self.assertEqual(analyze_run.analyze(args), 0)
                self.assertEqual(len(payloads), 3, "resume must not call model twice")
            self.assertEqual(len(analyze_run._read_jsonl(root / "analysis/failures.jsonl")), 2)
            self.assertIn("$0.003000", (root / "analysis/REPORT.md").read_text())
            result.write_text(result.read_text() + json.dumps(_row("D", False)) + "\n")
            with patch.object(analyze_run, "_call") as call, contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(ValueError):
                    analyze_run.analyze(args)
                call.assert_not_called()

    def test_invalid_json_is_saved_with_known_cost_and_no_automatic_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = root / "result.jsonl"; path.write_text(json.dumps(_row("A", False)) + "\n")
            args = argparse.Namespace(results=str(path), trace_dir=None, output_dir=str(root / "analysis"),
                                      model="fake/model", limit=None, analyze=True)
            def fake_call(model, system, payload):
                return (json.dumps(SUMMARY) if "run_statistics" in payload else "not json"), 0.02, {}
            with patch.object(analyze_run, "_call", side_effect=fake_call) as call, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(analyze_run.analyze(args), 1)
                self.assertEqual(call.call_count, 2)
                self.assertEqual(analyze_run.analyze(args), 1)
                self.assertEqual(call.call_count, 2)
            records = analyze_run._read_jsonl(root / "analysis/failures.jsonl")
            self.assertEqual(records[0]["status"], "error")
            self.assertEqual(records[0]["cost_usd"], 0.02)
            self.assertIn("$0.040000", (root / "analysis/REPORT.md").read_text())

    def test_interrupted_log_extra_event_does_not_shift_matching(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r = _row("A", False); r["algorithm"] = "PBTClarifier2"
            (root / "batch-output.jsonl").write_text(json.dumps(r) + "\n")
            def panel(title, text):
                return f"╭── {title} ──╮\n│ {text} │\n╰──╯\n"
            prompt = "You analyze a Python programming task to choose relevant TASK: " + r["prompt"] + " ENTRY POINT: f"
            log = panel("Prompt", prompt) + panel("Model Response", '{"categories":[5]}')
            log += panel("Prompt", "You analyze a Python programming task to choose relevant TASK: unfinished ENTRY POINT: f")
            (root / "batch-generate.log").write_text(log)
            traces, info = analyze_run.extract_traces(root, [r])
            self.assertEqual(info["matched"], 1)
            self.assertEqual(traces[(r["task_id"], r["prompt"])]["events"][0]["stage"], "category_selection")


class RunnerTests(unittest.TestCase):
    def test_frozen_batches_and_resume_do_not_repeat_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); benchmark = root / "benchmark"; benchmark.mkdir()
            batches = []
            for b in range(10):
                path = benchmark / f"batch-{b}.jsonl"
                rows = [_row(f"{b}-{i}", True) for i in range(10)]
                path.write_text("".join(json.dumps(r) + "\n" for r in rows))
                batches.append({"path": path.name, "sha256": run_train100._sha(path)})
            (benchmark / "manifest.json").write_text(json.dumps({"batches": batches}))
            algorithm = root / "algorithm_source.py"; algorithm.write_text("# fake algorithm\n")
            output = root / "out"
            args = ["run_train100.py", "--algorithm", str(algorithm), "--output-dir", str(output), "--execute"]
            calls = []
            def fake_run(command, log):
                calls.append(command)
                if "--dataset_path" in command:
                    source = Path(command[command.index("--dataset_path") + 1]); target = Path(command[command.index("--output_path") + 1])
                    target.write_text(source.read_text())
                else:
                    source = Path(command[command.index("--generation_path") + 1]); target = Path(command[command.index("--output_path") + 1])
                    target.write_text(source.read_text())
                log.write_text("mocked\n")
            with patch.object(run_train100, "BENCHMARK", benchmark), patch.object(run_train100.shutil, "which", return_value="docker"), \
                 patch.object(run_train100.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as process, \
                 patch.object(run_train100, "_run", side_effect=fake_run), patch.object(sys, "argv", args + ["--pilot", "1"]), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_train100.main(), 0)
                self.assertEqual(len(calls), 1)
                with patch.object(sys, "argv", args):
                    self.assertEqual(run_train100.main(), 0)
                    self.assertEqual(len(calls), 12)
                    self.assertEqual(run_train100.main(), 0)
                    self.assertEqual(len(calls), 12)
                compare_calls = [c.args[0] for c in process.call_args_list
                                 if any(str(v).endswith('compare_train100.py') for v in c.args[0])]
                self.assertEqual(len(compare_calls), 2, 'every completed run refreshes comparison')
            sent = []
            for command in calls:
                if "--dataset_path" in command:
                    sent.extend(run_train100._read(Path(command[command.index("--dataset_path") + 1])))
            self.assertEqual(len(sent), 100)
            self.assertEqual(len({r['task_id'] for r in sent}), 100, 'pilot tasks must not be rerun')
            self.assertIn('100/100', (output / 'REPORT.md').read_text())


class ComparisonTests(unittest.TestCase):
    def test_register_requires_identical_100_tasks_and_tracks_multiple_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); bench = root / 'benchmark'; bench.mkdir()
            rows = [_row(str(i), i % 2 == 0) for i in range(100)]
            source = bench / 'batch.jsonl'; source.write_text(''.join(json.dumps(x) + '\n' for x in rows))
            manifest = {'batches': [{'path': source.name, 'sha256': run_train100._sha(source)}],
                        'tasks': [{'task_id': x['task_id'], 'dataset': 'demo', 'source': 'original'} for x in rows]}
            (bench / 'manifest.json').write_text(json.dumps(manifest))
            paths = []
            for run, algorithm in [('one', 'PBTClarifier2'), ('two', 'PBTClarifier3')]:
                folder = root / run; folder.mkdir(); result = folder / 'results.jsonl'
                result.write_text(''.join(json.dumps({**x, 'algorithm': algorithm, 'model': 'fake/model'}) + '\n' for x in rows))
                (folder / 'experiment.json').write_text(json.dumps({'manifest_sha256': run_train100._sha(bench / 'manifest.json'), 'model': 'fake/model'}))
                paths.append(result)
            compare_train100.register(bench, paths[0], 'first')
            compare_train100.register(bench, paths[1], 'second')
            compare_train100.register(bench, paths[1], 'second')
            reg = json.loads((bench / 'comparison-registry.json').read_text())
            self.assertEqual(len(reg['entries']), 2)
            self.assertIn('50/100', (bench / 'COMPARISON.md').read_text())
            pair = json.loads((bench / 'pairwise.json').read_text())[0]
            self.assertEqual((pair['both_pass'], pair['a_only'], pair['b_only'], pair['both_fail']), (50, 0, 0, 50))
            changed = [json.loads(x) for x in paths[0].read_text().splitlines()]
            changed[0]['prompt'] = 'a different prompt'
            paths[0].write_text(''.join(json.dumps(x) + '\n' for x in changed))
            with self.assertRaises(ValueError):
                compare_train100.register(bench, paths[0], 'first')


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

from clarify import runtime


class EntryPointTests(unittest.TestCase):
    def initialize(self, dataset, canonical):
        truth = {task_id: {"base": [1], "plus": []} for task_id in canonical}
        with (
            patch.object(runtime, "get_mbpp_plus", return_value=canonical),
            patch.object(runtime, "get_mbpp_plus_hash", return_value="fixture"),
            patch.object(runtime, "get_groundtruth", return_value=truth),
        ):
            return runtime.init_evalplus_evaluator(dataset)

    def test_calls_input_entry_point_for_all_three_train100_mismatches(self):
        names = [
            ("Mbpp/770", "odd_Num_Sum", "odd_num_sum"),
            ("Mbpp/763", "find_Min_Diff", "find_min_diff"),
            ("Mbpp/166", "find_even_Pair", "find_even_pair"),
        ]
        canonical = {
            task_id: {
                "task_id": task_id,
                "entry_point": canonical_name,
                "base_input": [[1]],
                "plus_input": [],
            }
            for task_id, _, canonical_name in names
        }
        dataset = [
            {"task_id": task_id, "entry_point": input_name} for task_id, input_name, _ in names
        ]
        evaluator = self.initialize(dataset, canonical)
        for task_id, input_name, canonical_name in names:
            with self.subTest(task_id=task_id):
                # Saved generation rows do not contain an entry_point field.
                instance = evaluator.partial({"task_id": task_id})
                trigger = instance._construct_tests()
                self.assertIn(f"assertion({input_name}(*inp)", trigger)
                self.assertNotIn(f"assertion({canonical_name}(*inp)", trigger)
                self.assertIs(instance.problem, canonical[task_id])
                self.assertEqual(instance.problem["entry_point"], canonical_name)
                # Execute only the fixed fixture, never model-generated code.
                scope = {}
                exec(f"def {input_name}(value): return value\n" + trigger, scope)

    def test_special_oracle_uses_canonical_name_despite_call_name_override(self):
        problem = {"entry_point": "are_equivalent", "base_input": [[1]], "plus_input": []}
        instance = runtime.EvalPlusDockerInstanceEvaluator(
            problem, {"base": [1], "plus": []}, entry_point="areEquivalent"
        )
        self.assertEqual(instance._oracle(), "out == exp or True")
        trigger = instance._construct_tests()
        self.assertIn("assertion(areEquivalent(*inp)", trigger)
        self.assertIn("assert out == exp or True", trigger)

    def test_fallback_test_cases_are_preserved(self):
        tests = "assert local_function(1) == 2"
        dataset = [{"task_id": "Mbpp/183", "entry_point": "local_function", "test_cases": tests}]
        evaluator = self.initialize(dataset, {})
        instance = evaluator.partial({"task_id": "Mbpp/183"})
        self.assertEqual(instance._construct_tests(), tests + '\nprint("PASSED TESTS")')

    def test_existing_constructors_keep_canonical_call_name(self):
        problem = {"entry_point": "canonical", "base_input": [[1]], "plus_input": []}
        evaluator = runtime.EvalPlusEvaluator(
            {"Mbpp/1": problem}, {"Mbpp/1": {"base": [1], "plus": []}}
        )
        self.assertIn(
            "assertion(canonical(*inp)", evaluator.partial({"task_id": "Mbpp/1"})._construct_tests()
        )

    def test_conflicting_input_names_fail_instead_of_silently_overwriting(self):
        with self.assertRaisesRegex(ValueError, "conflicting entry points"):
            self.initialize(
                [
                    {"task_id": "Mbpp/1", "entry_point": "first"},
                    {"task_id": "Mbpp/1", "entry_point": "second"},
                ],
                {"Mbpp/1": {"entry_point": "canonical"}},
            )

    def test_prompt_variants_can_share_the_same_entry_point(self):
        evaluator = self.initialize(
            [
                {"task_id": "Mbpp/1", "entry_point": "given", "prompt": "one"},
                {"task_id": "Mbpp/1", "entry_point": "given", "prompt": "two"},
            ],
            {"Mbpp/1": {"entry_point": "canonical", "base_input": [[1]], "plus_input": []}},
        )
        self.assertEqual(evaluator.partial({"task_id": "Mbpp/1"}).entry_point, "given")


if __name__ == "__main__":
    unittest.main()

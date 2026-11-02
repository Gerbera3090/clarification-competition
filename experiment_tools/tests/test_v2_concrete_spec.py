import contextlib
import io
import json
import unittest

from clarify.algorithms.v2_concrete_spec import V2ConcreteSpecClarifier


class FakeEnvironment:
    def __init__(self, gates=(), finals=(), budget=1):
        self.gates, self.finals, self.budget = list(gates), list(finals), budget
        self.prompts, self.questions, self.events = [], [], []

    def can_ask(self):
        return len(self.questions) < self.budget

    def ask_human(self, question):
        self.questions.append(question)
        return f'Answer {len(self.questions)}.'

    def llm(self, prompt):
        if isinstance(prompt, list):
            prompt = prompt[0]['content']
        self.prompts.append(prompt)
        if 'V2 CONCRETE SPEC GATE' in prompt:
            self.events.append('gate')
            question = self.gates.pop(0) if self.gates else None
            return json.dumps({'ask': bool(question), 'issue': 'input_arity' if question else 'none',
                               'input_status': 'partial', 'output_status': 'explicit', 'reason': 'check',
                               'question': question or ''})
        if 'V1 SIMPLE JUDGE' in prompt:
            self.events.append('judge')
            return json.dumps({'has_conflict': False, 'evidence': [], 'reason': ''})
        if 'V1 STRUCTURE.' in prompt:
            return json.dumps({'instructions': [], 'examples': []})
        if 'V1 TASK-SPECIFIC PROPERTIES' in prompt:
            return json.dumps({'properties': []})
        if 'V1 FINAL JUDGE' in prompt:
            question = self.finals.pop(0) if self.finals else None
            return json.dumps({'ask': bool(question), 'question': question or '', 'reason': '', 'sources': []})
        if 'Implement the Python function' in prompt:
            self.events.append('code')
            return 'def f(x): return x'
        raise AssertionError(prompt[:200])

    def decide(self, *_args, **_kwargs):
        raise AssertionError('No properties in the test should need decisions')


class ConcreteSpecTests(unittest.TestCase):
    def run_case(self, **kwargs):
        env = FakeEnvironment(**kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            result = V2ConcreteSpecClarifier().run(env, {'prompt': 'Return the input.', 'entry_point': 'f'})
        self.assertEqual(result, 'def f(x): return x')
        return env

    def test_three_gate_questions_repeat_from_start_until_budget(self):
        env = self.run_case(budget=3, gates=['One?', 'Two?', 'Three?'])
        self.assertEqual(env.questions, ['One?', 'Two?', 'Three?'])
        self.assertEqual(env.events, ['gate', 'gate', 'gate', 'code'])
        self.assertIn('Answer 1.', env.prompts[1])
        self.assertIn('Answer 2.', env.prompts[2])
        self.assertIn('Answer 3.', env.prompts[-1])

    def test_gate_falls_through_then_loop_restarts(self):
        env = self.run_case(budget=3, gates=['Interface?', None, None], finals=['Conflict?', None])
        self.assertEqual(env.questions, ['Interface?', 'Conflict?'])
        self.assertEqual(env.events, ['gate', 'gate', 'judge', 'gate', 'judge', 'code'])
        simple_prompts = [p for p in env.prompts if 'V1 SIMPLE JUDGE' in p]
        self.assertIn('Answer 1.', simple_prompts[0])
        self.assertIn('Answer 2.', simple_prompts[1])

    def test_stop_when_all_steps_select_no_question(self):
        env = self.run_case(budget=3, gates=[None], finals=[None])
        self.assertEqual(env.questions, [])
        self.assertEqual(env.events, ['gate', 'judge', 'code'])

    def test_exact_duplicate_falls_through_instead_of_consuming_turn(self):
        env = self.run_case(budget=3, gates=['Interface?', 'Interface?', None], finals=['Conflict?', None])
        self.assertEqual(env.questions, ['Interface?', 'Conflict?'])
        self.assertEqual(env.events, ['gate', 'gate', 'judge', 'gate', 'judge', 'code'])

    def test_no_budget_goes_directly_to_code(self):
        env = self.run_case(budget=0)
        self.assertEqual(env.questions, [])
        self.assertEqual(env.events, ['code'])


if __name__ == '__main__':
    unittest.main()

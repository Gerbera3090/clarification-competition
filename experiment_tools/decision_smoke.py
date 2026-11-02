#!/usr/bin/env python3
"""Make one small, billable OpenAI Decisions call through the competition SDK."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clarify.env import ClarificationConfiguration, ClarificationEnvironment


def main() -> int:
    if not os.getenv('OPENAI_API_KEY'):
        print('OPENAI_API_KEY is not set. Run: source .env', file=sys.stderr)
        return 2
    model = os.getenv('ECC_DECISION_MODEL', 'openai/gpt-6-luna')
    env = ClarificationEnvironment(ClarificationConfiguration(decision_model=model),
                                   {'prompt': '', 'entry_point': 'sort_numbers'})
    questions = {
        'sortedness': {
            'type': 'choice',
            'instructions': 'Does the task explicitly specify whether the output must be sorted?',
            'criteria': {'established': 'Sorted output is explicitly required.',
                         'ambiguous': 'Whether output is sorted is not specified.',
                         'not_applicable': 'Sorting is unrelated to the task.'},
        },
        'cardinality': {
            'type': 'choice',
            'instructions': 'Does the task explicitly say how many elements the output contains?',
            'criteria': {'established': 'The required output count is explicitly specified.',
                         'ambiguous': 'The output count is not specified.',
                         'not_applicable': 'Output element count is unrelated to the task.'},
        },
    }
    context = ('Write a Python function that sorts a list. The returned list must have exactly '
               'the same number of elements as the input list.')
    started = monotonic()
    try:
        answers = env.decide(questions=questions, context=context)
        if not all(isinstance(answers.get(k), dict) and answers[k].get('choice') in v['criteria']
                   for k, v in questions.items()):
            raise ValueError('Decision response was missing an expected choice')
    except Exception as exc:
        print(f'Decision smoke test failed ({type(exc).__name__}): {exc}', file=sys.stderr)
        return 1
    print(f'model: {model}')
    print('answers:')
    print(json.dumps(answers, ensure_ascii=False, indent=2))
    print(f'elapsed: {monotonic() - started:.2f}s')
    print(f'SDK recorded prompt cost: ${env.prompt_cost:.8f} (may not match the final bill)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

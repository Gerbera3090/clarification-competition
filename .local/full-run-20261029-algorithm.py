# Local starter template. Complete the submission header before opening a PR.
# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier:

"""Quick Start clarification algorithm for local experiments.

Always ask one model-generated question before implementing the function.

Team:
Team Members:
Main Contact:
"""

from __future__ import annotations

from typing import Any

from clarify.baselines import ClarificationAlgorithmBase
from clarify.env import ClarificationEnvironment, TooManyQuestionException
from clarify.runtime import _validate_and_parse_evalplus_result


QUESTION_PROMPT = """You are about to implement the Python function `{entry_point}`.
The user requested:

{prompt}

Before coding, ask exactly one short, specific question about the function's
expected behavior. Choose a detail whose answer could change the code.
Return only the question. Do not write any Python code.
"""

CODING_PROMPT = """Implement the Python function `{entry_point}`.
Original request:

{prompt}

Your clarification question: {question}
The user's answer: {answer}

Follow the user's answer. Return only the implementation enclosed in
```python and ```.
"""


class MyClarification(ClarificationAlgorithmBase):
    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        question_response = env.llm(
            QUESTION_PROMPT.format(
                entry_point=problem["entry_point"], prompt=problem["prompt"]
            )
        )
        question = next(
            (line.split("?", 1)[0].strip() + "?" for line in question_response.splitlines() if "?" in line),
            f"What should `{problem['entry_point']}` return for an empty input?",
        )

        answer = ""
        if env.can_ask():
            try:
                answer = env.ask_human(question)
            except TooManyQuestionException:
                pass

        response = env.llm(
            CODING_PROMPT.format(
                entry_point=problem["entry_point"],
                prompt=problem["prompt"],
                question=question,
                answer=answer,
            )
        )
        try:
            return _validate_and_parse_evalplus_result(response)
        except ValueError:
            return response

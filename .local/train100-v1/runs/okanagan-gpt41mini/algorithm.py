"""
Okanagan - Based on https://github.com/jie-jw-wu/human-eval-comm
https://arxiv.org/abs/2406.00215
"""

from __future__ import annotations

from typing import Any

from clarify.baselines.base import ClarificationAlgorithmBase
from clarify.env import ClarificationEnvironment, TooManyQuestionException
from clarify.runtime import _validate_and_parse_evalplus_result

CODE_PROMPT_TEMPLATE = """
Generate Python code directly (Markdown) to solve the coding problem implementing `{entry_point}`.

{prompt}

Enclose your solution in ```python and ```.
""".strip()

CLARIFICATION_PROMPT_TEMPLATE = """
Given the programming problem and a generated candidate, ask ONE clarifying question if the requirements in the given problem description are incomplete, inconsistent or ambiguous 
for solving the problem correctly and passing the tests.
If no need to ask clarifying questions, return strictly ’NO_QUESTIONS’ only. Otherwise, return the clarifying questions.

### Problem:

{prompt}

### Candidate

{candidate}
""".strip()

REGEN_CODE_PROMPT_TEMPLATE = """
{prompt}
{clarification}

Given the above conversations, generate Python code directly (Markdown) to solve the coding problem implementing `{entry_point}`:
"""


class Okanagan(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {"generation_attempts": 3}

    def _generate_seed_candidate(
        self, env: ClarificationEnvironment, problem: dict[str, str]
    ) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    CODE_PROMPT_TEMPLATE.replace("{prompt}", problem["prompt"]).replace(
                        "{entry_point}", problem["entry_point"]
                    )
                ),
            }
        ]

        response = env.llm(messages)

        messages += [{"role": "assistant", "content": response}]

        for _ in range(self.config.get("generation_attempts", 3)):
            try:
                return _validate_and_parse_evalplus_result(response)
            except ValueError:
                # The response might not contain an answer, assume a question is raised.
                try:
                    answer = env.ask_human(response)
                    messages += [{"role": "user", "content": answer}]
                    response = env.llm(messages)
                    messages += [{"role": "assistant", "content": response}]
                except TooManyQuestionException:
                    return response

    def _generate_candidate(
        self, env: ClarificationEnvironment, problem: dict[str, str], clarifications: list[str]
    ) -> str:

        messages = [
            {
                "role": "user",
                "content": (
                    REGEN_CODE_PROMPT_TEMPLATE.replace("{prompt}", problem["prompt"])
                    .replace("{clarification}", "\n".join(clarifications))
                    .replace("{entry_point}", problem["entry_point"])
                ),
            }
        ]

        response = env.llm(messages)

        messages += [{"role": "assistant", "content": response}]

        for _ in range(self.config.get("generation_attempts", 3)):
            try:
                return _validate_and_parse_evalplus_result(response)
            except ValueError as e:
                # The response might not contain an answer, assume a question is raised.
                messages += [{"role": "user", "content": str(e)}]
                response = env.llm(messages)
                messages += [{"role": "assistant", "content": response}]

    def _generate_clarifying_question(self, env, prompt, candidate):
        response = env.llm(
            (
                CLARIFICATION_PROMPT_TEMPLATE.replace("{prompt}", prompt).replace(
                    "{candidate}", candidate
                )
            )
        )

        if "```" in response:
            _, response = response.split("```", 1)
        if "```" in response:
            response, _ = response.split("```", 1)
        return response

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:

        clarifications = []
        while True:
            if clarifications:
                candidate = self._generate_candidate(env, problem, clarifications)
            else:
                candidate = self._generate_seed_candidate(env, problem)

            if not env.can_ask():
                return candidate

            clarification_question = self._generate_clarifying_question(
                env, problem["prompt"], candidate
            )

            if "NO_QUESTIONS" in clarification_question:
                return candidate

            clarification = env.ask_human(clarification_question)
            num_rounds = len(clarifications)
            clarifications += [
                f"Questions #{num_rounds + 1}:\n{clarification_question}\nAnswers:\n{clarification}\n"
            ]

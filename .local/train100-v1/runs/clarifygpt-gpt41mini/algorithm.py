"""
A modernized variant of ClarifyGPT
https://arxiv.org/abs/2310.10996
"""

from __future__ import annotations

from typing import Any

from clarify.baselines.base import ClarificationAlgorithmBase
from clarify.env import ClarificationEnvironment, TooManyQuestionException
from clarify.runtime import _validate_and_parse_evalplus_result

DEFAULT_MBPP_TEMPLATE = """
Please provide a self-contained Python script implementing `{entry_point}` that solves the following problem:

{prompt}

Enclose your solution in ```python and ```.
""".strip()

GEN_FROM_PROGRAM = """
You are given user requirements for a Python function:

{prompt}

and a candidate implementation:

```python
{candidate}
```

Your task is to generate some complex, difficult, or corner-case inputs for this requirement.
Return a suffix to the candidate implementation with Python assert statements to test the functionality of the code.

You may import and use helpers from the Python standard library to construct
inputs. Return ONLY the function. Use ```python and ``` to uniquely indicate your solution. 
Do not repeat the implementation.
""".strip()

CLARIFICATION_PROMPT = """
You will be given a user requirement and its candidate solutions. Your task is to clarify this requirement by asking clarifying questions.
Specifically, you will first analyze the functionality of each solution. Then, by comparing their differences, you can determine which parts in the requirement are ambiguous and ask ONE targeted clarification question.

### User Requirement:

{prompt}

### Inconsistent Solutions
Solution 0:
{target}
Solution 1:
{alternative}

### Test Result
{test_result}

### Analysis and Clarifying Questions
Return your analysis and the resulting clarifying questions. Only ask questions that help to differiante the solution. 
Enclose your set of questions in ``` and ```. If the solutions are identical, simply state ```The task description is clear.```
""".strip()


class ClarifyGPT(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {
        "generation_attempts": 3,
        "test_attempts": 3,
        "cluster_size": 25,
    }

    def _generate_seed_candidate(
        self, env: ClarificationEnvironment, problem: dict[str, str]
    ) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    DEFAULT_MBPP_TEMPLATE.replace("{prompt}", problem["prompt"]).replace(
                        "{entry_point}", problem["entry_point"]
                    )
                ),
            }
        ]

        response = env.llm(messages)

        messages += [{"role": "assistant", "content": response}]

        while True:
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

    def _generate_candidate(self, env: ClarificationEnvironment, problem: dict[str, str]) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    DEFAULT_MBPP_TEMPLATE.replace("{prompt}", problem["prompt"]).replace(
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
            except ValueError as e:
                # The response might not contain an answer, assume a question is raised.
                messages += [{"role": "user", "content": str(e)}]
                response = env.llm(messages)
                messages += [{"role": "assistant", "content": response}]

    def _generate_seed_test_cases(
        self, env: ClarificationEnvironment, prompt: str, candidate: str
    ) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    GEN_FROM_PROGRAM.replace("{prompt}", prompt).replace("{candidate}", candidate)
                ),
            }
        ]

        response = env.llm(messages)
        messages += [{"role": "assistant", "content": response}]
        for _ in range(self.config.get("test_attempts", 3)):
            try:
                test_cases = _validate_and_parse_evalplus_result(response)
                test_result = self._test_candidate(env, candidate, test_cases)
                if test_result != "success":
                    raise ValueError(test_result)
                return test_cases
            except ValueError as e:
                messages += [{"role": "user", "content": str(e)}]
                response = env.llm(messages)
                messages += [{"role": "assistant", "content": response}]

    def _test_candidate(self, env, candidate, test_cases):
        test_code = f'{candidate}\n{test_cases}\nprint("TEST SUCCESS")'
        test_result = env.exec_code(test_code)
        if "TEST SUCCESS" in test_result:
            return "success"
        return test_result

    def _generate_clarifying_question(self, env, prompt, candidate, alternative, test_result):
        response = env.llm(
            (
                CLARIFICATION_PROMPT.replace("{prompt}", prompt)
                .replace("{target}", candidate)
                .replace("{alternative}", alternative)
                .replace("{test_result}", test_result)
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
            current_prompt = "\n".join([problem["prompt"]] + clarifications)
            seed_candidate = self._generate_seed_candidate(
                env, {"prompt": current_prompt, "entry_point": problem["entry_point"]}
            )

            if not env.can_ask():
                return seed_candidate

            seed_test_cases = self._generate_seed_test_cases(env, current_prompt, seed_candidate)

            test_result = "success"
            for _ in range(self.config.get("cluster_size", 25) - 1):
                alternative_candidate = self._generate_candidate(
                    env, {"prompt": current_prompt, "entry_point": problem["entry_point"]}
                )
                test_result = self._test_candidate(env, alternative_candidate, seed_test_cases)
                if test_result != "success":
                    break

            if test_result == "success":
                return seed_candidate  # Clear description

            clarifying_question = self._generate_clarifying_question(
                env, current_prompt, seed_candidate, alternative_candidate, test_result
            )

            clarification = env.ask_human(clarifying_question)
            num_rounds = len(clarifications)
            clarifications += [
                f"Questions #{num_rounds + 1}:\n{clarifying_question}\nAnswers:\n{clarification}\n"
            ]

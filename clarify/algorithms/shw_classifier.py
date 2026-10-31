# SPDX-FileCopyrightText: 2026 Hyukwon Kwon <gerbera3090@kaist.ac.kr>
#
# SPDX-License-Identifier: MIT

"""Algorithm name.

Short description of the main mechanism of the implemented algorithm.
This does not need to go into details, but should capture the core idea.

Team: SHW
Team Members: Sihyun Ahn (KAIST), Hyukwon Kwon (KAIST)
Main Contact: gerbera3090@kaist.ac.kr (Hyukwon Kwon)
"""

from __future__ import annotations

from typing import Any

from clarify.baselines import ClarificationAlgorithmBase
from clarify.env import ClarificationEnvironment, TooManyQuestionException
from clarify.runtime import _validate_and_parse_evalplus_result

##########################################################################
# Prompts
# loaded from ClarifyGPT
##########################################################################

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

#########################################################################
# Auxiliary Functions
#########################################################################


def sanitize():
    pass


class ContradictionDetector:
    def __init__(self, problem: dict[str, Any]):
        self.problem = problem

    def is_contradictory(self) -> tuple[bool, str | None]:
        checks = (
            self.base_llm_judge,
            self.delta_debugging,
            self.property_check,
            self.code_sampling,
            self.testcase_sampling,
        )
        for check in checks:
            result = check()
            if result[0]:
                return result
        return (False, "")

    def base_llm_judge(self) -> tuple[bool, str | None]:
        pass

    def delta_debugging(self) -> tuple[bool, str | None]:
        pass

    def property_check(self) -> tuple[bool, str | None]:
        pass

    def code_sampling(self) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(self) -> tuple[bool, str | None]:
        pass


class AmbiguityDetector:
    def __init__(self, problem: dict[str, Any]):
        self.problem = problem

    def is_ambiguous(self) -> tuple[bool, str | None]:
        checks = (
            self.base_llm_judge,
            self.property_check,
            self.code_sampling,
            self.testcase_sampling,
        )
        for check in checks:
            result = check()
            if result[0]:
                return result
        return (False, "")

    def base_llm_judge(self) -> tuple[bool, str | None]:
        pass

    def property_check(self) -> tuple[bool, str | None]:
        pass

    def code_sampling(self) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(self) -> tuple[bool, str | None]:
        pass


#########################################################################
# Classifier
#########################################################################
class SHWClassifier(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {}

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        contradiction_detector = ContradictionDetector(problem)
        ambiguity_detector = AmbiguityDetector(problem)

        if contradiction_detector.is_contradictory()[0]:
            pass

        if ambiguity_detector.is_ambiguous()[0]:
            pass

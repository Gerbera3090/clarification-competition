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

import ast
import json
import re
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

CHECK_CONTRADICTION = """
Following is the problem description of function `{entry_point}`. Does the description itself contain contradictory content? Your answer should contain <yes/no>, <what should be asked to the user>.

{prompt}

Your answer format (fill part within <>):
Contradiction: <yes/no>
Description: <what should be asked to the user (e.g., The first and second sentence contradicts each other)>
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

DECOMPOSE_PROMPT = """
Following is the problem description of function `{entry_point}`:

{prompt}

Split the description into its atomic requirements so that each item states exactly one constraint, behavior, or example.
Copy the wording of the description verbatim and do not add, merge, or rephrase content.
Keep each example (an input together with its expected output) as one item.
Return a single Python list of strings in the original order. Enclose the list in ```python and ```.
""".strip()

GEN_TEST_INPUTS = """
Following is the problem description of function `{entry_point}`:

{prompt}

Generate {num_inputs} diverse test inputs for `{entry_point}`, covering typical cases and corner cases.
Return a single Python list where each item is a tuple of positional arguments (e.g., [(1, 2), ([3, 4],)]).
Use only Python literals. Enclose the list in ```python and ```.
""".strip()

# Runs every candidate on every input inside one container and prints the outputs as JSON.
# Expects `_sources`, `_inputs` and `_entry_point` to be defined before it.
BEHAVIOR_HARNESS = """
import copy
import json
import signal


def _on_timeout(signum, frame):
    raise TimeoutError()


signal.signal(signal.SIGALRM, _on_timeout)

_behaviors = []
for _source in _sources:
    _namespace = {"__name__": "candidate"}
    signal.alarm(2)
    try:
        exec(_source, _namespace)
        _function = _namespace[_entry_point]
    except BaseException as e:
        _behaviors.append(["<load error: " + type(e).__name__ + ">"] * len(_inputs))
        continue
    finally:
        signal.alarm(0)

    _outputs = []
    for _args in _inputs:
        signal.alarm(1)
        try:
            _outputs.append(repr(_function(*copy.deepcopy(_args))))
        except BaseException as e:
            _outputs.append("<" + type(e).__name__ + ">")
        finally:
            signal.alarm(0)
    _behaviors.append(_outputs)

print("__BEHAVIORS__" + json.dumps(_behaviors))
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


DOCSTRING_PATTERN = re.compile(r"(\"\"\"|''')(.*?)\1", re.DOTALL)
DOCSTRING_SLOT = "<<DESCRIPTION>>"
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(`])")
# Splits a sentence before clauses that typically add a separate constraint,
# e.g. "find primes, where 2 is non-prime and also reject even numbers"
CLAUSE_BOUNDARY = re.compile(
    r";\s+"
    r"|,\s+(?=(?:where|while|whereas|but|however|although|though|unless|except|"
    r"provided|given that|such that|so that|and)\b)"
    r"|\s+(?=(?:and also|but also|while also|as well as)\b)",
    re.IGNORECASE,
)
EXAMPLE_HEADER = re.compile(r"^(for )?examples?\s*:?$", re.IGNORECASE)
DECOMPOSITION_METHODS = ("heuristic", "llm")


def parse_python_literal(response: str) -> Any:
    """Parses a literal enclosed in ```python and ```, also as `name = <literal>`."""
    code = _validate_and_parse_evalplus_result(response)
    return ast.literal_eval(ast.parse(code.strip()).body[0].value)


def decompose_prompt(
    problem: dict[str, Any],
    method: str = "heuristic",
    env: ClarificationEnvironment | None = None,
) -> tuple[str, list[str]]:
    """Splits the prompt into a fixed context and droppable elements.

    The context is the code around the docstring (imports, signature) with the
    docstring replaced by DOCSTRING_SLOT. Elements are parts of the description
    in their original order. With `method="heuristic"`, they are the clauses and
    examples (doctests or asserts); with `method="llm"`, they are the atomic
    requirements identified by the LLM, falling back to the heuristic on failure.
    """
    if method not in DECOMPOSITION_METHODS:
        raise ValueError(f"Unknown decomposition method `{method}`")

    prompt = problem["prompt"]
    match = DOCSTRING_PATTERN.search(prompt)
    if match:
        context = prompt[: match.start()] + DOCSTRING_SLOT + prompt[match.end() :]
        description = match.group(2)
    else:
        context, description = DOCSTRING_SLOT, prompt

    if method == "llm":
        if env is None:
            raise ValueError("LLM decomposition requires an environment")
        elements = _decompose_with_llm(description, problem["entry_point"], env)
        if elements:
            return context, elements

    return context, _decompose_with_heuristic(description)


def _decompose_with_llm(
    description: str, entry_point: str, env: ClarificationEnvironment
) -> list[str]:
    messages = [
        {
            "role": "user",
            "content": (
                DECOMPOSE_PROMPT.replace("{prompt}", description.strip()).replace(
                    "{entry_point}", entry_point
                )
            ),
        }
    ]
    response = env.llm(messages)
    try:
        elements = parse_python_literal(response)
    except (ValueError, SyntaxError, IndexError, AttributeError, TypeError):
        return []

    if not isinstance(elements, list):
        return []
    return [e.strip() for e in elements if isinstance(e, str) and e.strip()]


def _decompose_with_heuristic(description: str) -> list[str]:
    elements, prose = [], []

    def flush_prose():
        text = " ".join(prose).strip()
        for sentence in SENTENCE_BOUNDARY.split(text):
            elements.extend(c.strip() for c in CLAUSE_BOUNDARY.split(sentence) if c.strip())
        prose.clear()

    lines = [line.strip() for line in description.splitlines()]
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith(">>>"):
            # A doctest example is the call plus its expected output lines
            flush_prose()
            example = [line]
            while i < len(lines) and lines[i] and not lines[i].startswith(">>>"):
                example.append(lines[i])
                i += 1
            elements.append("\n".join(example))
        elif line.startswith("assert "):
            flush_prose()
            elements.append(line)
        elif line and not EXAMPLE_HEADER.match(line):
            prose.append(line)
    flush_prose()

    return elements


def compose_prompt(context: str, elements: list[str]) -> str:
    body = "\n".join(line for element in elements for line in element.splitlines())
    if context.strip() == DOCSTRING_SLOT:
        return body
    indented = "\n".join("    " + line for line in body.splitlines())
    return context.replace(DOCSTRING_SLOT, f'"""\n{indented}\n    """')


def format_call(entry_point: str, args: tuple) -> str:
    return f"{entry_point}({', '.join(repr(arg) for arg in args)})"


class ContradictionDetector:
    def __init__(self, problem: dict[str, Any], decomposition: str = "heuristic"):
        self.problem = problem
        self.decomposition = decomposition

    def is_contradictory(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        checks = (
            self.base_llm_judge,
            self.delta_debugging,
            self.property_check,
            self.code_sampling,
            self.testcase_sampling,
        )
        for check in checks:
            result = check(env)
            # Unimplemented checks return None
            if result is not None and result[0]:
                return result
        return (False, "")

    def base_llm_judge(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        messages = [
            {
                "role": "user",
                "content": (
                    CHECK_CONTRADICTION.replace(
                        "{prompt}", self.problem["prompt"]
                    ).replace("{entry_point}", self.problem["entry_point"])
                ),
            }
        ]
        response = env.llm(messages)

    def delta_debugging(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        """Drops one element at a time and checks whether the behavior changes.

        If every partial prompt yields a solution that behaves like the solution
        for the full prompt, no element is in conflict. Otherwise, the elements
        whose removal changes the behavior are reported.
        """
        entry_point = self.problem["entry_point"]
        context, elements = decompose_prompt(self.problem, self.decomposition, env)
        if len(elements) < 2:
            # Dropping the only element leaves nothing to compare against
            return (False, None)

        inputs = self._generate_test_inputs(env)
        if not inputs:
            return (False, None)

        variants = [elements] + [elements[:i] + elements[i + 1 :] for i in range(len(elements))]
        sources = [self._generate_solution(env, compose_prompt(context, v)) for v in variants]
        behaviors = self._run_candidates(env, sources, inputs)
        if behaviors is None:
            return (False, None)

        reference = behaviors[0]
        findings = []
        for i, behavior in enumerate(behaviors[1:]):
            if behavior == reference:
                continue
            k = next(k for k, (a, b) in enumerate(zip(reference, behavior)) if a != b)
            findings.append(
                f'Dropping "{elements[i]}" changes {format_call(entry_point, inputs[k])} '
                f"from {reference[k]} to {behavior[k]}."
            )

        if not findings:
            return (False, None)
        return (True, "\n".join(findings))

    def _generate_solution(self, env: ClarificationEnvironment, prompt: str) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    DEFAULT_MBPP_TEMPLATE.replace("{prompt}", prompt).replace(
                        "{entry_point}", self.problem["entry_point"]
                    )
                ),
            }
        ]
        response = env.llm(messages)
        try:
            return _validate_and_parse_evalplus_result(response)
        except ValueError:
            return ""

    def _generate_test_inputs(
        self, env: ClarificationEnvironment, num_inputs: int = 10
    ) -> list[tuple]:
        messages = [
            {
                "role": "user",
                "content": (
                    GEN_TEST_INPUTS.replace("{prompt}", self.problem["prompt"])
                    .replace("{entry_point}", self.problem["entry_point"])
                    .replace("{num_inputs}", str(num_inputs))
                ),
            }
        ]
        response = env.llm(messages)
        try:
            inputs = parse_python_literal(response)
        except (ValueError, SyntaxError, IndexError, AttributeError, TypeError):
            return []

        if not isinstance(inputs, list):
            return []
        return [args if isinstance(args, tuple) else (args,) for args in inputs][:num_inputs]

    def _run_candidates(
        self, env: ClarificationEnvironment, sources: list[str], inputs: list[tuple]
    ) -> list[list[str]] | None:
        script = (
            f"_sources = {sources!r}\n"
            f"_inputs = {inputs!r}\n"
            f"_entry_point = {self.problem['entry_point']!r}\n"
            f"{BEHAVIOR_HARNESS}"
        )
        output = env.exec_code(script)
        for line in output.splitlines():
            if line.startswith("__BEHAVIORS__"):
                return json.loads(line[len("__BEHAVIORS__") :])
        # Timeout of the whole script or a harness failure
        return None

    def property_check(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def code_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass


class AmbiguityDetector:
    def __init__(self, problem: dict[str, Any]):
        self.problem = problem

    def is_ambiguous(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        checks = (
            self.base_llm_judge,
            self.property_check,
            self.code_sampling,
            self.testcase_sampling,
        )
        for check in checks:
            result = check(env)
            # Unimplemented checks return None
            if result is not None and result[0]:
                return result
        return (False, "")

    def base_llm_judge(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def property_check(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def code_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass


#########################################################################
# Classifier
#########################################################################
class SHWClassifier(ClarificationAlgorithmBase):
    # decomposition: how delta debugging splits the prompt ("heuristic" or "llm")
    DEFAULT_CONFIG = {"decomposition": "heuristic"}

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        contradiction_detector = ContradictionDetector(problem, self.config["decomposition"])
        ambiguity_detector = AmbiguityDetector(problem)

        if contradiction_detector.is_contradictory(env)[0]:
            pass

        if ambiguity_detector.is_ambiguous(env)[0]:
            pass

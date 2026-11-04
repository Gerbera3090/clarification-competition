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
from clarify.env import (
    ClarificationEnvironment,
    LimitsExceededException,
    TooManyQuestionException,
)
from clarify.runtime import _validate_and_parse_evalplus_result

##########################################################################
# Prompts (`{name}` slots are filled by `fill`)
##########################################################################

# From ClarifyGPT
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
A contradiction needs two explicit statements applying to the same valid input. Cite both statements in Description. Missing information is not a contradiction.
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

# Delta debugging
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

DELTA_VERIFICATION = (
    "Verify whether the original task contains an explicit contradiction. Removing a "
    "normal requirement can legitimately change a program's behavior. Generated bugs "
    "and behavior differences are not proof. Cite two incompatible source statements "
    "for the same valid input and condition, or reject the alleged conflict. "
    "Return Contradiction: yes/no and Description: evidence and one targeted question."
    "\nTASK:\n{task}\nOBSERVED DIFFERENCES:\n{findings}"
)

# Property check
PROPERTY_EXTRACTION = (
    "Extract at most 12 behavioral properties explicitly stated or entailed by this task. "
    "Use English names/meanings and verbatim source quotes. Do not assume unmentioned laws. "
    "Return a Python list of dictionaries with name, quote and meaning in ```python fences."
    "\nTASK:\n{task}"
)

PROPERTY_PAIR = (
    "Do these source-grounded properties require incompatible behavior "
    "for the SAME valid input and condition? Missing details are not contradictions. "
    "{properties}"
)

PROPERTY_PAIR_CRITERIA = {
    "conflict": "Both apply and cannot hold together.",
    "compatible": "They can coexist or have different conditions.",
    "uncertain": "The source does not establish a conflict.",
}

PROPERTY_CONFLICT_VERIFICATION = (
    "Verify these possible property conflicts against the task. A model judgment is a hint. "
    "Require two explicit source statements that cannot hold for the same valid input. "
    "Reject missing details, different scopes and inferred assumptions. "
    "Return Contradiction: yes/no and Description: evidence and one targeted question."
    "\nTASK:\n{task}\nPOSSIBLE CONFLICTS:\n{conflicts}"
)

AMBIGUITY_CHECK = (
    "Analyze this task's relevant behavioral properties: input domain and argument "
    "count/order/types, output type/structure, ordering, boundaries and side effects. "
    "Find one consequential unresolved choice that changes a correct implementation. "
    "Clear signatures and examples can already establish a fact. An unmentioned law is "
    "not automatically missing. Ignore stylistic choices, invalid inputs and hypothetical "
    "hidden tests. Prior user answers settle only the issue they resolve; do not re-ask it. "
    "Return Ambiguity: yes/no and Description: source evidence, two plausible behaviors, "
    "and ONE question asking for ONE independent missing fact."
    "\nTASK:\n{task}"
)

# Clarification
CLARIFICATION_HISTORY = (
    "\nPrevious clarification turns (answers are authoritative within their scope):\n"
    "{clarifications}"
)

QUESTION_PROMPT = (
    "Use the task and fallible analysis to ask ONE consequential clarification "
    "question about ONE independent fact. Recheck the source and previous answers. "
    "Do not ask whether generated code is correct, ask for tests, or repeat an "
    "answered fact. Return only the question, or NONE if no grounded question remains."
    "\nTASK:\n{task}\nANALYSIS:\n{analysis}"
)

# Specification
CODE_PROTOCOL = (
    "Use Python standard library only. Return the required value, not printed output. "
    "Preserve the function signature unless a clarification changes it. "
    "Provide implementation code only: no tests, demos, input(), print(), CLI or __main__. "
    "Do not invent input restrictions or broaden an explicitly restricted domain. "
    "Preserve numeric precision, return types and general behavior beyond examples. "
    "Answers override only the issue they settle; preserve unaffected requirements. "
    "Never hard-code examples, return placeholders or silently discard conflicts."
)

SPEC_PROMPT = (
    "V9 SPECIFICATION. Consolidate the task and actual clarification answers into ONE "
    "specification. Later stages receive only this specification, not the raw task. "
    "Preserve every stated domain, strict/inclusive boundary, type, ordering/tie rule, "
    "side effect and implementation constraint. An answer overrides only its resolved "
    "issue, including superseded examples. Keep unresolved choices and assumptions "
    "explicit; do not invent defaults, hidden tests or an interpretation that removes "
    "an unusual but consistent constraint. Make each requirement atomic and cite "
    "existing source IDs. Return ONLY JSON; do not generate tests or code. Schema: "
    '{"requirements":[{"id":"R1","requirement":"one precise fact","sources":["T1"]}],'
    '"examples":[],"unresolved":[],"superseded":[],"assumptions":[]}.'
    "\nENTRY POINT: {entry_point}\nPROTOCOL: {protocol}"
    "\nSOURCE CATALOG: {sources}"
    "\nCLARIFICATION Q/A: {clarifications}"
)

SPEC_CORRECTION = "\nCorrect these issues: {errors}"

# Tests
TEST_GENERATOR = (
    "V9 TEST GENERATOR. Generate tests from ONLY the frozen specification. No candidate "
    "implementation exists. Cover every requirement with a meaningful check or an honest "
    "not_testable entry. Never add or change requirements. Respect explicit domains, "
    "boundaries, types, shapes, ordering and clarified facts. Write roughly 5-12 checks, "
    "maximum {max_tests}. Each code string defines check(fn, source, tree) "
    "with three positional arguments: target callable, implementation source, ast.Module. "
    "Use standard library only, bounded deterministic cases/property loops, and asserts "
    "with input/expected/actual values in messages. No top-level calls or external I/O. "
    "Do not invent expected values for unresolved behavior. Return ONLY JSON: "
    '{"tests":[{"id":"test_1","requirement_ids":["R1"],"kind":"functional",'
    '"description":"what is checked","code":"def check(fn, source, tree): ..."}],'
    '"not_testable":[{"requirement_ids":["R2"],"reason":"precise limitation"}]}.'
    " kind may be functional, property or static. Do not return a requirements field."
    "\nFROZEN SPECIFICATION:\n{spec}"
)

TEST_REVISION = "\nPREVIOUS TEST PLAN:\n{previous}\nFIX THESE REVIEW ISSUES:\n{review}"

TEST_REVIEW = (
    "V9 TEST REVIEW. Compare ONLY the frozen specification and proposed tests; no "
    "candidate implementation exists. Independently recompute expected values. "
    "Check domains, strict/inclusive boundaries, types, shapes, clarified facts, "
    "test consistency, coverage and unsupported assumptions. Do not change the spec. "
    "REVISE only for a concrete wrong expectation, out-of-domain input, contradictory "
    "assertion, invalid checker, specific missing testable behavior or mechanical issue. "
    "Cite test/requirement IDs and corrections. Optional examples or style changes are "
    "nonblocking. Honest untestable constraints are permitted. Never approve an empty "
    "test plan. Start with VERDICT: PASS or VERDICT: REVISE, then plain-text reasons."
    "\nFROZEN SPECIFICATION:\n{spec}\nTEST PLAN:\n{tests}"
)

# Code
CODE_GENERATOR = (
    "V9 CODE GENERATOR. Implement `{entry_point}` in ONE complete ```python block "
    "without surrounding prose. Follow the frozen specification and clarified "
    "facts in their exact scope. Tests are an executable interpretation, not "
    "permission to hard-code examples or ignore the specification. Preserve "
    "already-passed checks. Do not edit tests or disable assertions. "
    "\nPROTOCOL:\n{protocol}\nSPECIFICATION:\n{spec}"
    "\nFROZEN TEST PLAN:\n{tests}\nPREVIOUS BEST CODE:\n{previous}"
    "\nACTUAL FAILURES AND FEEDBACK:\n{feedback}"
)

CODE_FEEDBACK = (
    "FAILURES OF PREVIOUS BEST CODE:\n{failures}\nPASSED CHECKS TO PRESERVE:\n{passed}"
)

CODE_FEEDBACK_LATEST = "\nFAILURES OF LATEST REJECTED TRIAL:\n{failures}"

##########################################################################
# Execution harnesses
##########################################################################

# Runs every candidate on every input and prints the outputs as JSON.
# Expects `_sources`, `_inputs` and `_entry_point`.
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

# Runs static checks and generated tests on a candidate. Expects `_payload`.
TEST_HARNESS = r"""
import ast as _ast, builtins as _builtins, contextlib as _contextlib
import io as _io, json as _json, signal as _signal, sys as _sys, traceback as _traceback

_checks = []
def _result(_id, _status, _detail, _kind='static'):
    _checks.append({'id': _id, 'status': _status, 'detail': str(_detail)[-5000:], 'kind': _kind})
def _timed_out(_signum, _frame):
    raise TimeoutError('Fixed checker time limit exceeded')
_signal.signal(_signal.SIGALRM, _timed_out)
def _arm(_seconds):
    _signal.setitimer(_signal.ITIMER_REAL, _seconds)

_result('S_FORMAT', 'failed' if _payload['format_issue'] else 'passed', _payload['format_issue'] or 'One Python block.')
try:
    _tree = _ast.parse(_payload['source'])
    _compiled = compile(_tree, '<candidate>', 'exec')
    _result('S_SYNTAX', 'passed', 'Python source compiled.')
except BaseException as _error:
    _tree = None
    _result('S_SYNTAX', 'failed', type(_error).__name__ + ': ' + str(_error))

if _tree is not None:
    _names = {n.name for n in _tree.body if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))}
    _result('S_ENTRY_POINT', 'passed' if _payload['entry_point'] in _names else 'failed', 'Required function: ' + _payload['entry_point'])
    _external = []
    for _node in _ast.walk(_tree):
        _mods = [a.name for a in _node.names] if isinstance(_node, _ast.Import) else ([_node.module or ''] if isinstance(_node, _ast.ImportFrom) else [])
        for _mod in _mods:
            if _mod.split('.')[0] not in _sys.stdlib_module_names and _mod.split('.')[0] not in _sys.builtin_module_names:
                _external.append(_mod)
    _result('S_STDLIB', 'failed' if _external else 'passed', 'Non-standard imports: ' + repr(_external))
    _io_calls = [n.lineno for n in _ast.walk(_tree) if isinstance(n, _ast.Call) and (
        isinstance(n.func, _ast.Name) and n.func.id in {'print', 'input'}
        or isinstance(n.func, _ast.Attribute) and isinstance(n.func.value, _ast.Attribute)
        and isinstance(n.func.value.value, _ast.Name) and n.func.value.value.id == 'sys'
        and n.func.value.attr in {'stdin', 'stdout', 'stderr'})]
    _result('S_NO_IO', 'failed' if _io_calls else 'passed', 'Input/output calls at lines: ' + repr(_io_calls))
    _top_calls = [n.lineno for n in _tree.body if isinstance(n, _ast.Expr) and isinstance(n.value, _ast.Call)]
    _main_blocks = [n.lineno for n in _tree.body if isinstance(n, _ast.If) and any(
        isinstance(v, _ast.Constant) and v.value == '__main__' for v in _ast.walk(n.test))]
    _result('S_NO_HARNESS', 'failed' if _top_calls or _main_blocks else 'passed',
            'Top-level calls/main blocks: ' + repr(_top_calls + _main_blocks))
    try:
        _arm(1.0)
        _capture, _initial = _io.StringIO(), {'__name__': 'candidate'}
        with _contextlib.redirect_stdout(_capture), _contextlib.redirect_stderr(_capture):
            exec(_compiled, _initial)
        if not callable(_initial.get(_payload['entry_point'])):
            raise TypeError('Required function is not callable after module load')
        if _capture.getvalue():
            raise AssertionError('Module load produced output: ' + _capture.getvalue()[-1000:])
        _result('S_LOAD', 'passed', 'Candidate module loaded and function is callable.')
    except BaseException as _error:
        _result('S_LOAD', 'failed', type(_error).__name__ + ': ' + str(_error))
    finally:
        _arm(0)
    for _test in _payload['tests']:
        _capture, _ns, _tns = _io.StringIO(), {'__name__': 'candidate'}, {'__name__': 'generated_test'}
        _phase = 'load'
        try:
            _arm(_payload['timeout'])
            with _contextlib.redirect_stdout(_capture), _contextlib.redirect_stderr(_capture):
                exec(_compiled, _ns)
                _fn = _ns.get(_payload['entry_point'])
                if not callable(_fn):
                    raise TypeError('Required entry point is not callable')
                _phase = 'test_definition'
                exec(compile(_test['code'], '<test:' + _test['id'] + '>', 'exec'), _tns)
                _phase = 'test_execution'
                _outcome = _tns['check'](_fn, _payload['source'], _tree)
                if _outcome is False:
                    raise AssertionError('Checker returned False')
            if _capture.getvalue():
                _result(_test['id'], 'failed', 'Unexpected output: ' + _capture.getvalue()[-1000:], _test['kind'])
            else:
                _result(_test['id'], 'passed', 'Checker completed.', _test['kind'])
        except BaseException as _error:
            _frames = _traceback.extract_tb(_error.__traceback__)
            _candidate_frame = any(f.filename == '<candidate>' for f in _frames)
            _is_test_error = (_phase == 'test_definition' or (
                not _candidate_frame and isinstance(_error, (NameError, UnboundLocalError, ImportError, SyntaxError))))
            _detail = ''.join(_traceback.format_exception(type(_error), _error, _error.__traceback__))
            _result(_test['id'], 'test_error' if _is_test_error else 'failed', _detail, _test['kind'])
        finally:
            _arm(0)
else:
    for _test in _payload['tests']:
        _result(_test['id'], 'failed', 'Cannot run checker: candidate syntax invalid.', _test['kind'])
print('V8_RUN_RESULT=' + _json.dumps({'status': 'ok', 'checks': _checks}, ensure_ascii=True))
"""

#########################################################################
# Auxiliary Functions
#########################################################################

DOCSTRING_PATTERN = re.compile(r"(\"\"\"|''')(.*?)\1", re.DOTALL)
DOCSTRING_SLOT = "<<DESCRIPTION>>"
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(`])")
# Clauses that typically add a separate constraint
CLAUSE_BOUNDARY = re.compile(
    r";\s+"
    r"|,\s+(?=(?:where|while|whereas|but|however|although|though|unless|except|"
    r"provided|given that|such that|so that|and)\b)"
    r"|\s+(?=(?:and also|but also|while also|as well as)\b)",
    re.IGNORECASE,
)
EXAMPLE_HEADER = re.compile(r"^(for )?examples?\s*:?$", re.IGNORECASE)
DECOMPOSITION_METHODS = ("heuristic", "llm")
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def fill(template: str, **values: Any) -> str:
    """Fills `{name}` slots in one pass, so inserted text is never re-filled."""
    return PLACEHOLDER.sub(
        lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0),
        template,
    )


def parse_python_literal(response: str) -> Any:
    """Parses a literal enclosed in ```python and ```, also as `name = <literal>`."""
    code = _validate_and_parse_evalplus_result(response)
    return ast.literal_eval(ast.parse(code.strip()).body[0].value)


def parse_json(response: str) -> Any:
    return json.loads(response.strip().removeprefix("```json").removesuffix("```"))


def parse_verdict(response: str, label: str) -> bool:
    """Reads `<label>: yes/no`, also when decorated as `**<label>:** yes`."""
    verdict = re.search(label + r"\W*(yes|no)\b", response, re.IGNORECASE)
    return bool(verdict and verdict.group(1).lower() == "yes")


def format_call(entry_point: str, args: tuple) -> str:
    return f"{entry_point}({', '.join(repr(arg) for arg in args)})"


def decompose_prompt(
    problem: dict[str, Any],
    method: str = "heuristic",
    env: ClarificationEnvironment | None = None,
) -> tuple[str, list[str]]:
    """Splits the prompt into a context with DOCSTRING_SLOT and droppable elements."""
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
    response = env.llm(
        fill(DECOMPOSE_PROMPT, prompt=description.strip(), entry_point=entry_point)
    )
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
            elements.extend(
                c.strip() for c in CLAUSE_BOUNDARY.split(sentence) if c.strip()
            )
        prose.clear()

    lines = [line.strip() for line in description.splitlines()]
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith(">>>"):
            # A doctest is the call plus its expected output lines
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


#########################################################################
# Detectors
#########################################################################


class ContradictionDetector:
    def __init__(
        self,
        problem: dict[str, Any],
        decomposition: str = "heuristic",
        max_dropped_elements: int = 6,
    ):
        self.problem = problem
        self.decomposition = decomposition
        self.max_dropped_elements = max_dropped_elements

    def is_contradictory(
        self, env: ClarificationEnvironment
    ) -> tuple[bool, str | None]:
        checks = (
            self.base_llm_judge,
            self.delta_debugging,
            self.property_check,
            self.code_sampling,
            self.testcase_sampling,
        )
        for check in checks:
            result = check(env)
            if result is not None and result[0]:
                return result
        return (False, "")

    def base_llm_judge(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        response = env.llm(
            fill(
                CHECK_CONTRADICTION,
                prompt=self.problem["prompt"],
                entry_point=self.problem["entry_point"],
            )
        )
        print("SIMPLE JUDGE:", response, flush=True)
        return (parse_verdict(response, "Contradiction"), response)

    def delta_debugging(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        """Drops prose elements one by one (and all examples together) and reports
        the drops that change the behavior of the generated solution."""
        entry_point = self.problem["entry_point"]
        context, elements = decompose_prompt(self.problem, self.decomposition, env)
        if len(elements) < 2:
            return (False, None)

        inputs = self._generate_test_inputs(env)
        if not inputs:
            return (False, None)

        is_example = [e.startswith((">>>", "assert ")) for e in elements]
        groups = [[i] for i, example in enumerate(is_example) if not example][
            : self.max_dropped_elements
        ]
        examples = [i for i, example in enumerate(is_example) if example]
        if examples and len(examples) < len(elements):
            groups.append(examples)

        variants = [elements] + [
            [e for i, e in enumerate(elements) if i not in group] for group in groups
        ]
        sources = [
            self._generate_solution(env, compose_prompt(context, v)) for v in variants
        ]
        behaviors = self._run_candidates(env, sources, inputs)
        if behaviors is None:
            return (False, None)

        reference = behaviors[0]
        findings = []
        for group, behavior in zip(groups, behaviors[1:], strict=True):
            if behavior == reference:
                continue
            k = next(
                k
                for k, (a, b) in enumerate(zip(reference, behavior, strict=True))
                if a != b
            )
            dropped = f'"{elements[group[0]]}"' if len(group) == 1 else "all examples"
            findings.append(
                f"Dropping {dropped} changes {format_call(entry_point, inputs[k])} "
                f"from {reference[k]} to {behavior[k]}."
            )

        print(
            "DELTA DEBUGGING:",
            json.dumps(
                {
                    "elements": elements,
                    "inputs": repr(inputs),
                    "sources": sources,
                    "behaviors": behaviors,
                    "findings": findings,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if not findings:
            return (False, None)
        response = env.llm(
            fill(
                DELTA_VERIFICATION,
                task=self.problem["prompt"],
                findings="\n".join(findings),
            )
        )
        print("DELTA VERIFICATION:", response, flush=True)
        return (parse_verdict(response, "Contradiction"), response)

    def _generate_solution(self, env: ClarificationEnvironment, prompt: str) -> str:
        response = env.llm(
            fill(
                DEFAULT_MBPP_TEMPLATE,
                prompt=prompt,
                entry_point=self.problem["entry_point"],
            )
        )
        try:
            return _validate_and_parse_evalplus_result(response)
        except ValueError:
            return ""

    def _generate_test_inputs(
        self, env: ClarificationEnvironment, num_inputs: int = 10
    ) -> list[tuple]:
        response = env.llm(
            fill(
                GEN_TEST_INPUTS,
                prompt=self.problem["prompt"],
                entry_point=self.problem["entry_point"],
                num_inputs=num_inputs,
            )
        )
        try:
            inputs = parse_python_literal(response)
        except (ValueError, SyntaxError, IndexError, AttributeError, TypeError):
            return []

        if not isinstance(inputs, list):
            return []
        return [args if isinstance(args, tuple) else (args,) for args in inputs][
            :num_inputs
        ]

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
        return None

    def property_check(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        prompt = self.problem["prompt"]
        response = env.llm(fill(PROPERTY_EXTRACTION, task=prompt))
        try:
            properties = parse_python_literal(response)
            if not isinstance(properties, list):
                raise ValueError("Expected a list of properties")
            properties = [
                p
                for p in properties
                if isinstance(p, dict)
                and all(
                    isinstance(p.get(k), str) and p[k].strip()
                    for k in ("name", "quote", "meaning")
                )
                and " ".join(p["quote"].split()) in " ".join(prompt.split())
            ][:12]
        except (
            ValueError,
            SyntaxError,
            IndexError,
            AttributeError,
            TypeError,
        ) as error:
            print("PROPERTY EXTRACTION UNAVAILABLE:", error, flush=True)
            return (False, None)
        print("PROPERTIES:", json.dumps(properties, ensure_ascii=False), flush=True)
        pairs = [
            (i, j)
            for i in range(len(properties))
            for j in range(i + 1, len(properties))
        ]
        conflicts = []
        for start in range(0, len(pairs), 64):
            batch = pairs[start : start + 64]
            questions = {
                f"pair_{i}_{j}": {
                    "type": "choice",
                    "instructions": fill(
                        PROPERTY_PAIR,
                        properties=json.dumps(
                            [properties[i], properties[j]], ensure_ascii=False
                        ),
                    ),
                    "criteria": PROPERTY_PAIR_CRITERIA,
                }
                for i, j in batch
            }
            try:
                answers = env.decide(questions=questions, context={"task": prompt})
            except LimitsExceededException:
                raise
            except Exception as error:
                # Missing or unsupported decision model
                print("PROPERTY PAIRS UNAVAILABLE:", error, flush=True)
                return (False, None)
            print(
                "PROPERTY PAIRS:", json.dumps(answers, ensure_ascii=False), flush=True
            )
            if not isinstance(answers, dict):
                continue
            for i, j in batch:
                answer = answers.get(f"pair_{i}_{j}", {})
                if isinstance(answer, dict) and answer.get("choice") == "conflict":
                    conflicts.append([properties[i], properties[j]])
        if not conflicts:
            return (False, None)
        response = env.llm(
            fill(
                PROPERTY_CONFLICT_VERIFICATION,
                task=prompt,
                conflicts=json.dumps(conflicts, ensure_ascii=False),
            )
        )
        print("PROPERTY CONFLICT:", response, flush=True)
        return (parse_verdict(response, "Contradiction"), response)

    def code_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(
        self, env: ClarificationEnvironment
    ) -> tuple[bool, str | None]:
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
            if result is not None and result[0]:
                return result
        return (False, "")

    def base_llm_judge(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def property_check(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        response = env.llm(fill(AMBIGUITY_CHECK, task=self.problem["prompt"]))
        print("PROPERTY OMISSION:", response, flush=True)
        return (parse_verdict(response, "Ambiguity"), response)

    def code_sampling(self, env: ClarificationEnvironment) -> tuple[bool, str | None]:
        pass

    def testcase_sampling(
        self, env: ClarificationEnvironment
    ) -> tuple[bool, str | None]:
        pass


#########################################################################
# Classifier
#########################################################################


class SHWClassifier(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {
        "decomposition": "heuristic",  # "heuristic" or "llm"
        "max_dropped_elements": 6,
        "max_test_versions": 3,
        "max_code_attempts": 4,
        "max_tests": 24,
        "test_timeout": 0.5,
    }

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        clarifications = []
        while env.can_ask():
            task = problem["prompt"]
            if clarifications:
                task += fill(
                    CLARIFICATION_HISTORY,
                    clarifications=json.dumps(clarifications, ensure_ascii=False),
                )
            current_problem = {"prompt": task, "entry_point": problem["entry_point"]}
            contradiction_detector = ContradictionDetector(
                current_problem,
                self.config["decomposition"],
                self.config["max_dropped_elements"],
            )
            ambiguity_detector = AmbiguityDetector(current_problem)
            try:
                detected, description = contradiction_detector.is_contradictory(env)
                if not detected:
                    detected, description = ambiguity_detector.is_ambiguous(env)
                if not detected:
                    break
                question = env.llm(
                    fill(QUESTION_PROMPT, task=task, analysis=description)
                ).strip()
                if (
                    question.upper() == "NONE"
                    or not question
                    or any(
                        " ".join(question.lower().split())
                        == " ".join(q.lower().split())
                        for q, _ in clarifications
                    )
                ):
                    break
                answer = env.ask_human(question)
                clarifications.append((question, answer))
                print(
                    "CLARIFICATION:",
                    json.dumps([question, answer], ensure_ascii=False),
                    flush=True,
                )
            except TooManyQuestionException:
                break
            except LimitsExceededException:
                break

        spec = self._create_frozen_spec(env, problem, clarifications)
        tests = self._create_reviewed_tests(env, spec)
        return self._implement_with_tests(env, problem["entry_point"], spec, tests)

    def _create_frozen_spec(self, env, problem, clarifications):
        sources = {
            f"T{i}": line.strip()
            for i, line in enumerate(
                (line for line in problem["prompt"].splitlines() if line.strip()), 1
            )
        }
        sources.update({f"A{i}": a for i, (_, a) in enumerate(clarifications, 1)})
        prompt = fill(
            SPEC_PROMPT,
            entry_point=problem["entry_point"],
            protocol=CODE_PROTOCOL,
            sources=json.dumps(sources, ensure_ascii=False),
            clarifications=json.dumps(clarifications, ensure_ascii=False),
        )
        errors, spec = [], None
        for attempt in range(2):
            raw = env.llm(
                prompt + (fill(SPEC_CORRECTION, errors=errors) if errors else "")
            )
            try:
                value = parse_json(raw)
                if not isinstance(value, dict) or not isinstance(
                    value.get("requirements"), list
                ):
                    raise ValueError("Expected a requirements list")
                requirements = [
                    {"id": f"ANSWER_{i}", "requirement": answer, "sources": [f"A{i}"]}
                    for i, (_, answer) in enumerate(clarifications, 1)
                ]
                ids, errors = {r["id"] for r in requirements}, []
                answer_ids = set(ids)
                for row in value["requirements"]:
                    if isinstance(row, dict) and row.get("id") in answer_ids:
                        continue
                    if (
                        not isinstance(row, dict)
                        or not isinstance(row.get("id"), str)
                        or not row["id"].strip()
                        or row["id"] in ids
                        or not isinstance(row.get("requirement"), str)
                        or not row["requirement"].strip()
                        or not isinstance(row.get("sources"), list)
                        or not row["sources"]
                        or any(
                            not isinstance(ref, str) or ref not in sources
                            for ref in row["sources"]
                        )
                    ):
                        errors.append(
                            "Invalid requirement or source citation: " + repr(row)
                        )
                        continue
                    requirements.append(row)
                    ids.add(row["id"])
                if not requirements:
                    raise ValueError("No valid source-grounded requirements")
                for name in ("examples", "unresolved", "superseded", "assumptions"):
                    if not isinstance(value.get(name, []), list):
                        raise ValueError(name + " must be a list")
                for example in value.get("examples", []):
                    if (
                        not isinstance(example, dict)
                        or not isinstance(example.get("case"), str)
                        or not isinstance(example.get("sources"), list)
                        or not example["sources"]
                        or not all(
                            isinstance(ref, str) and ref in sources
                            for ref in example["sources"]
                        )
                    ):
                        errors.append("Invalid example/source citation")
                spec = {
                    "entry_point": problem["entry_point"],
                    "protocol": CODE_PROTOCOL,
                    "requirements": requirements,
                    "examples": value.get("examples", []),
                    "unresolved": value.get("unresolved", []),
                    "superseded": value.get("superseded", []),
                    "assumptions": value.get("assumptions", []),
                    "clarifications": clarifications,
                }
                if not errors:
                    break
            except (ValueError, KeyError, TypeError) as error:
                errors = [str(error)]
            print("SPECIFICATION RETRY:", attempt + 1, errors, flush=True)
        if spec is None:
            spec = {
                "entry_point": problem["entry_point"],
                "protocol": CODE_PROTOCOL,
                "requirements": [
                    {
                        "id": "RAW_TASK_FALLBACK",
                        "requirement": problem["prompt"],
                        "sources": list(sources),
                    }
                ],
                "examples": [],
                "unresolved": ["Specification extraction failed."],
                "superseded": [],
                "assumptions": [],
                "clarifications": clarifications,
            }
        spec["validation_issues"] = errors
        print("FROZEN SPECIFICATION:", json.dumps(spec, ensure_ascii=False), flush=True)
        return spec

    def _create_reviewed_tests(self, env, spec):
        frozen_spec = json.dumps(spec, ensure_ascii=False, sort_keys=True)
        requirement_ids = {r["id"] for r in spec["requirements"]}
        prompt = fill(
            TEST_GENERATOR, max_tests=self.config["max_tests"], spec=frozen_spec
        )
        best, previous, review = None, "", ""
        for version in range(1, self.config["max_test_versions"] + 1):
            raw = env.llm(
                prompt
                + (
                    fill(TEST_REVISION, previous=previous, review=review)
                    if previous
                    else ""
                )
            )
            issues, tests, not_testable, test_ids = [], [], [], set()
            try:
                value = parse_json(raw)
                if not isinstance(value, dict) or not isinstance(
                    value.get("tests"), list
                ):
                    raise ValueError("Expected a tests list")
                for row in value["tests"][: self.config["max_tests"]]:
                    try:
                        if (
                            not isinstance(row, dict)
                            or not isinstance(row.get("id"), str)
                            or not row["id"]
                            or row["id"] in test_ids
                            or not isinstance(row.get("requirement_ids"), list)
                            or not row["requirement_ids"]
                            or not all(
                                isinstance(r, str) and r in requirement_ids
                                for r in row["requirement_ids"]
                            )
                            or row.get("kind")
                            not in {"functional", "property", "static"}
                            or not isinstance(row.get("code"), str)
                            or len(row["code"]) > 14000
                        ):
                            raise ValueError("Invalid test fields")
                        tree = ast.parse(row["code"])
                        compile(tree, "<generated-test>", "exec")
                        check = next(
                            (
                                n
                                for n in tree.body
                                if isinstance(n, ast.FunctionDef) and n.name == "check"
                            ),
                            None,
                        )
                        if (
                            check is None
                            or len(check.args.args) != 3
                            or check.args.vararg
                            or check.args.kwarg
                            or not any(
                                isinstance(n, ast.Assert)
                                and not (
                                    isinstance(n.test, ast.Constant)
                                    and n.test.value is True
                                )
                                for n in ast.walk(check)
                            )
                            or any(
                                isinstance(n, ast.Expr)
                                and isinstance(n.value, ast.Call)
                                for n in tree.body
                            )
                        ):
                            raise ValueError(
                                "Define check(fn, source, tree) with a nontrivial assert and no top-level calls"
                            )
                        tests.append(row)
                        test_ids.add(row["id"])
                    except (ValueError, TypeError, SyntaxError) as error:
                        issues.append(str(error) + ": " + repr(row)[:200])
                for row in value.get("not_testable", []):
                    if (
                        isinstance(row, dict)
                        and isinstance(row.get("requirement_ids"), list)
                        and row["requirement_ids"]
                        and all(
                            isinstance(r, str) and r in requirement_ids
                            for r in row["requirement_ids"]
                        )
                        and isinstance(row.get("reason"), str)
                        and row["reason"].strip()
                    ):
                        not_testable.append(row)
                    else:
                        issues.append("Invalid not_testable entry")
                if len(value["tests"]) > self.config["max_tests"]:
                    issues.append("Test count limit exceeded")
            except (ValueError, TypeError) as error:
                issues.append(str(error))
            covered = {
                r for row in tests + not_testable for r in row["requirement_ids"]
            }
            missing = sorted(requirement_ids - covered)
            if missing:
                issues.append("Uncovered requirements: " + ", ".join(missing))
            if not tests:
                issues.append("No executable generated tests")
            suite = {
                "tests": tests,
                "not_testable": not_testable,
                "uncovered_requirement_ids": missing,
            }
            # Mechanical issues replace the LLM review
            review = (
                "VERDICT: REVISE\n" + "\n".join(issues)
                if issues
                else env.llm(
                    fill(
                        TEST_REVIEW,
                        spec=frozen_spec,
                        tests=json.dumps(suite, ensure_ascii=False),
                    )
                ).strip()
            )
            verdicts = set(
                re.findall(
                    r"^\s*[*`# -]*(?:VERDICT\s*:\s*)?(PASS|REVISE)\b",
                    "\n".join(review.splitlines()[:5]),
                    re.IGNORECASE | re.MULTILINE,
                )
            )
            approved = {v.lower() for v in verdicts} == {"pass"} and not issues
            suite.update(
                review_approved=approved,
                review=review,
                validation_issues=issues,
                selected_test_version=version,
            )
            print(
                "TEST REVIEW:",
                version,
                json.dumps(suite, ensure_ascii=False),
                flush=True,
            )
            rank = (not approved, len(missing), len(issues), -len(tests), -version)
            if best is None or rank < best[0]:
                best = (rank, suite)
            previous = raw
            if approved:
                break
        if json.dumps(spec, ensure_ascii=False, sort_keys=True) != frozen_spec:
            raise RuntimeError("Frozen specification changed during test review")
        print("FROZEN TESTS:", json.dumps(best[1], ensure_ascii=False), flush=True)
        return best[1]

    def _implement_with_tests(self, env, entry_point, spec, tests):
        frozen_spec = json.dumps(spec, ensure_ascii=False, sort_keys=True)
        frozen_tests = json.dumps(tests, ensure_ascii=False, sort_keys=True)
        best, feedback, previous, seen = None, "", "", set()
        for attempt in range(1, self.config["max_code_attempts"] + 1):
            try:
                raw = env.llm(
                    fill(
                        CODE_GENERATOR,
                        entry_point=entry_point,
                        protocol=spec["protocol"],
                        spec=frozen_spec,
                        tests=frozen_tests,
                        previous=previous,
                        feedback=feedback,
                    )
                )
            except LimitsExceededException:
                if best is None:
                    raise
                break
            try:
                code = _validate_and_parse_evalplus_result(raw)
                format_issue = (
                    ""
                    if raw.strip().startswith("```python")
                    and raw.strip().endswith("```")
                    and raw.count("```") == 2
                    else "Return one complete Python block only."
                )
            except ValueError:
                code, format_issue = raw, "Missing Python fenced block."
            execution = _execute_suite(
                env,
                code,
                entry_point,
                tests["tests"],
                self.config["test_timeout"],
                format_issue,
            )
            passed = {r["id"] for r in execution["checks"] if r["status"] == "passed"}
            eligible = execution["status"] == "ok"
            if (
                best is None
                or eligible
                and (not best["eligible"] or passed > best["passed"])
            ):
                best = {
                    "raw": raw,
                    "code": code,
                    "execution": execution,
                    "passed": passed,
                    "eligible": eligible,
                    "attempt": attempt,
                }
            print(
                "CODE ATTEMPT:",
                attempt,
                json.dumps(execution, ensure_ascii=False),
                flush=True,
            )
            if (
                eligible
                and execution["checks"]
                and all(r["status"] == "passed" for r in execution["checks"])
            ):
                break
            if (
                code in seen
                or not eligible
                or attempt == self.config["max_code_attempts"]
            ):
                break
            seen.add(code)
            failures = [
                r for r in best["execution"]["checks"] if r["status"] != "passed"
            ]
            feedback = fill(
                CODE_FEEDBACK,
                failures=json.dumps(failures, ensure_ascii=False),
                passed=sorted(best["passed"]),
            )
            if best["attempt"] != attempt:
                latest = [r for r in execution["checks"] if r["status"] != "passed"]
                feedback += fill(
                    CODE_FEEDBACK_LATEST,
                    failures=json.dumps(latest, ensure_ascii=False),
                )
            previous = best["raw"]
            print("CODE FEEDBACK:", feedback, flush=True)
        if best is None:
            raise RuntimeError("No implementation generated")
        print(
            "SELECTED CODE:",
            json.dumps(
                {
                    "attempt": best["attempt"],
                    "passed": sorted(best["passed"]),
                    "tests_review_approved": tests["review_approved"],
                    "uncovered": tests["uncovered_requirement_ids"],
                }
            ),
            flush=True,
        )
        return best["raw"]


def _execute_suite(env, code, entry_point, tests, timeout, format_issue=""):
    payload = json.dumps(
        {
            "source": code,
            "entry_point": entry_point,
            "tests": tests,
            "timeout": timeout,
            "format_issue": format_issue,
        },
        ensure_ascii=True,
    )
    script = (
        "import json\n_payload = json.loads(" + repr(payload) + ")\n" + TEST_HARNESS
    )
    output = ""
    for _ in range(2):
        try:
            output = env.exec_code(script)
        except Exception as error:
            output = type(error).__name__ + ": " + str(error)
        for line in reversed(output.splitlines()):
            if line.startswith("V8_RUN_RESULT="):
                try:
                    result = json.loads(line.split("=", 1)[1])
                    expected = {r["id"] for r in tests} | {"S_FORMAT", "S_SYNTAX"}
                    if (
                        result.get("status") == "ok"
                        and isinstance(result.get("checks"), list)
                        and expected <= {r["id"] for r in result["checks"]}
                    ):
                        return result
                except (ValueError, KeyError, TypeError):
                    pass
    return {
        "status": "execution_unavailable",
        "checks": [],
        "output_excerpt": output[-4000:],
    }

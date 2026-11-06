# SPDX-FileCopyrightText: 2026 Sihyun Ahn <sihyun.ahn@kaist.ac.kr>
# SPDX-FileCopyrightText: 2026 Hyukwon Kwon <gerbera3090@kaist.ac.kr>
# SPDX-FileCopyrightText: 2026 Shin Yoo <shin.yoo@kaist.ac.kr>
#
# SPDX-License-Identifier: MIT

"""SHW: a multi-agent system for clarifying underspecified coding tasks.

Role agents share a memory and act on the environment only through tools
(llm, decide, ask_human, run_candidates, run_tests). An orchestrator runs them as
a state machine: a defect detector (contradiction -> ambiguity -> final gate)
finds a defect, a questioner asks the user about it, and a spec writer, test
designer and coder turn the clarified task into code that is repaired with real
test failures.

Team: SHW
Team Members: Sihyun Ahn (KAIST), Hyukwon Kwon (KAIST), Shin Yoo (KAIST)
Main Contact: gerbera3090@kaist.ac.kr (Hyukwon Kwon)
"""

from __future__ import annotations

import ast
import difflib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Collection

from clarify.baselines import ClarificationAlgorithmBase
from clarify.env import (
    ClarificationEnvironment,
    LimitsExceededException,
    TooManyQuestionException,
)
from clarify.runtime import _validate_and_parse_evalplus_result

########################################################################
# Prompts (`{name}` slots are filled by `fill`)
########################################################################

# From ClarifyGPT
DEFAULT_MBPP_TEMPLATE = """
Please provide a self-contained Python script implementing `{entry_point}` that solves the following problem:

{prompt}

Enclose your solution in ```python and ```.
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
    "Extract the behavioral properties of this task in two groups. "
    "(1) At most 12 properties explicitly stated or entailed by the task, each with a "
    "verbatim source quote. Do not assume unmentioned laws. "
    "(2) At most 8 facts a correct implementation needs that the task may not "
    "establish, each with an empty quote. Start with the core: what exactly the "
    "function computes and returns, the meaning of each vague or overloaded word, and "
    "the number, order and format of the arguments. Add edge cases (empty, zero, "
    "negative or unusual values) only after the core, and only if typical inputs "
    "reach them. "
    "Use English names/meanings. Return a single Python list of dictionaries with "
    "name, quote and meaning in ```python fences."
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

PROPERTY_DETERMINED = (
    "Do the task text, signature and examples fix this property for every valid input, "
    "so that all correct implementations agree on it? Conventions any reasonable "
    "programmer would follow count as fixed. {property}"
)

PROPERTY_DETERMINED_CRITERIA = {
    "determined": "The task fixes the behavior for every valid input.",
    "undetermined": "Correct implementations can return different outputs.",
    "irrelevant": "The property does not affect outputs on valid inputs.",
}

OMISSION_SELECTION = (
    "A model judged these properties of the task undetermined; the judgment is a hint. "
    "Pick the ONE whose resolution most changes the outputs of a correct implementation "
    "on valid inputs. Ignore performance, style, invalid inputs and facts the source, "
    "signature or examples already settle. Prefer a fact that changes outputs on "
    "typical inputs, such as those in the examples, over one that matters only for "
    "edge cases (empty, zero, negative, unusual types or characters). "
    "Prior user answers settle only the issue "
    "they resolve; do not re-ask it. "
    "Return Ambiguity: yes/no and Description: source evidence, two plausible behaviors, "
    "and ONE question asking for ONE independent missing fact."
    "\nTASK:\n{task}\nUNDETERMINED PROPERTIES:\n{properties}"
)

# Single-prompt omission check (default; also the fallback of the property-based one)
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

# Final gate
BASE_LLM_JUDGE = (
    "Automated checks found no contradiction or ambiguity in this task, so it will be "
    "implemented without asking the user. Double-check that it truly has no defect. "
    "A defect is a contradiction (two explicit statements that cannot both hold for the "
    "same valid input), an ambiguity (a statement whose plausible readings give different "
    "outputs), or an omission (a fact a correct implementation needs that the description, "
    "signature and examples do not establish). Ignore stylistic choices, invalid inputs "
    "and details any reasonable programmer would settle the same way. Are you sure there "
    "is no defect? Return Defect: yes/no and Description: source evidence and ONE question "
    "asking for ONE missing fact."
    "\nTASK:\n{task}"
)

# Gate for every question after the first one about the task's meaning
FOLLOW_UP_GATE = (
    "The user has already answered the clarification turns appended to this task. "
    "Decide whether a defect remains that those answers do not settle: a contradiction, "
    "an ambiguity or a missing fact that changes the outputs on typical inputs. Answers "
    "settle what they address; do not count those issues again. Ignore edge cases "
    "(empty, zero, negative or invalid inputs), stylistic choices and details any "
    "reasonable programmer would settle the same way. Return Defect: yes/no and "
    "Description: source evidence and ONE question asking for ONE missing fact."
    "\nTASK:\n{task}"
)

# Asked first when the task gives no signature
SIGNATURE_QUESTION = "Which parameters does {entry_point} take, in what order, and of which types?"

# Clarification
CLARIFICATION_HISTORY = (
    "\nPrevious clarification turns (answers are authoritative within their scope):\n"
    "{clarifications}"
)

QUESTION_PROMPT = (
    "Use the task and fallible analysis to ask ONE consequential clarification "
    "question about ONE independent fact. Recheck the source and previous answers. "
    "Prefer what the task leaves most open among the number, types and shape of the "
    "arguments, the exact type and format of the result, and the core rule; ask about "
    "empty, zero, negative or invalid inputs only when those are settled. State the "
    "behavior you would otherwise implement, with one small example call and its "
    "result, and ask whether it is intended or the most plausible alternative is. "
    "Do not ask whether generated code is correct, ask for tests, or repeat an "
    "answered fact. Write plain text without backticks. Return only the question, "
    "or NONE if no grounded question remains."
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
    "SPECIFICATION. Consolidate the task and actual clarification answers into ONE "
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

PRECLEAN = (
    "The task below may contain one sentence or clause that cannot be reconciled with "
    "the rest: an impossible performance or implementation limit, a demand to return "
    "numbers or booleans as text, a kind of input the rest never uses, or a trailing "
    "clause that reverses the main statement. If it does, return the task with only "
    "that text removed in one ```text block, changing nothing else. Missing details, "
    "vague wording and unusual but consistent demands are not such text. Otherwise "
    "return NONE."
    "\nTASK:\n{task}"
)

SPEC_REWRITE = (
    "Rewrite the task description for `{entry_point}` into one complete and consistent "
    "specification that incorporates the user's clarification answers. Where an answer "
    "conflicts with the original text or its examples, the answer wins; keep everything "
    "else, including the function name `{entry_point}`, its parameters, and the examples "
    "that are consistent with the answers (fix or drop the others). Output only the "
    "rewritten specification."
    "\nTASK:\n{task}\nCLARIFICATION Q/A:\n{clarifications}"
)

# Tests
TEST_GENERATOR = (
    "Generate tests from ONLY the frozen specification. No candidate "
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
    "Compare ONLY the frozen specification and proposed tests; no "
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
    "Implement `{entry_point}` in ONE complete ```python block "
    "without surrounding prose. Follow the frozen specification and clarified "
    "facts in their exact scope. Tests are an executable interpretation, not "
    "permission to hard-code examples or ignore the specification. Preserve "
    "already-passed checks. Do not edit tests or disable assertions. "
    "\nPROTOCOL:\n{protocol}\nSPECIFICATION:\n{spec}"
    "\nFROZEN TEST PLAN:\n{tests}\nPREVIOUS BEST CODE:\n{previous}"
    "\nACTUAL FAILURES AND FEEDBACK:\n{feedback}"
)

CODE_FEEDBACK = "FAILURES OF PREVIOUS BEST CODE:\n{failures}\nPASSED CHECKS TO PRESERVE:\n{passed}"

CODE_FEEDBACK_LATEST = "\nFAILURES OF LATEST REJECTED TRIAL:\n{failures}"

########################################################################
# Execution harnesses
########################################################################

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

# Appended to the final code: accepts calls that pass one collection instead of
# several values (or the reverse) or extra trailing arguments, plus name variants.
CALL_ADAPTER = r"""


def _shw_adapt(_target):
    import functools as _functools
    import inspect as _inspect

    try:
        _signature = _inspect.signature(_target)
    except (TypeError, ValueError):
        return _target
    _globals = _target.__globals__

    def _binds(args):
        try:
            _signature.bind(*args)
            return True
        except TypeError:
            return False

    def _alternatives(args):
        yield (list(args),)
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            yield tuple(args[0])
        for size in range(len(args) - 1, 0, -1):
            yield args[:size]

    @_functools.wraps(_target)
    def _adapted(*args, **kwargs):
        # Recursive calls inside the target go straight to it
        previous = _globals.get(_target.__name__)
        _globals[_target.__name__] = _target
        try:
            if kwargs or _binds(args):
                return _target(*args, **kwargs)
            for alternative in _alternatives(args):
                if _binds(alternative):
                    return _target(*alternative)
            return _target(*args, **kwargs)
        finally:
            _globals[_target.__name__] = previous

    return _adapted


{entry_point} = _shw_adapt({entry_point})
for _alias in {aliases}:
    globals().setdefault(_alias, {entry_point})
"""

########################################################################
# Auxiliary Functions
########################################################################

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
CLEAN_SPEC_FIELDS = (
    "entry_point",
    "protocol",
    "requirements",
    "examples",
    "unresolved",
    "assumptions",
)
LITERAL_ERRORS = (ValueError, SyntaxError, IndexError, AttributeError, TypeError)


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


def parse_python_list(response: str) -> list:
    """Like `parse_python_literal`, but [] unless the response holds a list."""
    try:
        value = parse_python_literal(response)
    except LITERAL_ERRORS:
        return []
    return value if isinstance(value, list) else []


def parse_json(response: str) -> Any:
    return json.loads(response.strip().removeprefix("```json").removesuffix("```"))


def parse_verdict(response: str, label: str) -> bool:
    """Reads `<label>: yes/no`, also when decorated as `**<label>:** yes`."""
    verdict = re.search(label + r"\W*(yes|no)\b", response, re.IGNORECASE)
    return bool(verdict and verdict.group(1).lower() == "yes")


def to_json(value: Any, **kwargs: Any) -> str:
    return json.dumps(value, ensure_ascii=False, **kwargs)


def cites(refs: Any, known: Collection[str]) -> bool:
    """True if `refs` is a nonempty list of known IDs."""
    return (
        isinstance(refs, list)
        and bool(refs)
        and all(isinstance(ref, str) and ref in known for ref in refs)
    )


def format_call(entry_point: str, args: tuple) -> str:
    return f"{entry_point}({', '.join(repr(arg) for arg in args)})"


EXAMPLE_RESULT = re.compile(
    r"\s*(?:==|->|=>|\u279e|\u2192|returns?|should (?:return|be))\s*:?\s*",
    re.IGNORECASE,
)


def _split_call(text: str) -> tuple[str, str] | None:
    """Splits `name(...) rest` after the parenthesis that closes the call."""
    depth, quote = 0, None
    for i, char in enumerate(text):
        if quote:
            if char == quote and text[i - 1] != "\\":
                quote = None
        elif char in "'\"":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
            if depth == 0:
                return text[: i + 1], text[i + 1 :]
    return None


def _literal(text: str) -> tuple[bool, Any]:
    try:
        value = ast.literal_eval(text.strip().rstrip(".,;").strip())
        ast.literal_eval(repr(value))  # must also be writable into a test
        return True, value
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return False, None


def parse_examples(text: str, entry_point: str) -> list[tuple[tuple, Any]]:
    """Calls of the entry point with literal arguments and a stated literal result,
    written as doctests or as `f(...) == / -> / returns <result>`."""
    examples = []
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        line = raw.strip().removeprefix("assert ").strip()
        doctest = line.startswith(">>>")
        line = line.removeprefix(">>>").strip()
        if not line.startswith(entry_point + "("):
            continue
        split = _split_call(line)
        if split is None:
            continue
        call, rest = split
        if doctest and not rest.strip():
            following = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not following or following.startswith(">>>"):
                continue
            ok, expected = _literal(following)
        else:
            match = EXAMPLE_RESULT.match(rest)
            if not match or not match.end():
                continue
            ok, expected = _literal(rest[match.end() :])
        try:
            node = ast.parse(call, mode="eval").body
            if not isinstance(node, ast.Call) or node.keywords:
                continue
            args = tuple(ast.literal_eval(arg) for arg in node.args)
            ast.literal_eval(repr(args))
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
            continue
        if ok and (args, expected) not in examples:
            examples.append((args, expected))
    return examples[:8]


def is_pure_deletion(original: str, edited: str, entry_point: str) -> bool:
    """True if `edited` only removes text, at most half of it, and keeps every
    example, definition line and mention of the entry point."""
    removed = 0
    matcher = difflib.SequenceMatcher(a=original, b=edited, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            removed += i2 - i1
        elif tag != "equal" and (original[i1:i2].strip() or edited[j1:j2].strip()):
            return False
    kept = {line.strip() for line in edited.splitlines()}
    essential = [
        line.strip()
        for line in original.splitlines()
        if line.strip().startswith((">>>", "def ", "assert "))
    ]
    return (
        0 < removed <= len(original) / 2
        and all(line in kept for line in essential)
        and parse_examples(edited, entry_point) == parse_examples(original, entry_point)
        and (entry_point not in original or entry_point in edited)
    )


def has_signature(prompt: str) -> bool:
    """True if the task defines any function; variants may rename the entry point."""
    return re.search(r"(?m)^\s*(?:async\s+)?def\s+\w+\s*\(", prompt) is not None


def with_call_adapter(response: str, entry_point: str) -> str:
    """The final answer with CALL_ADAPTER appended, if it defines the entry point."""
    try:
        code = _validate_and_parse_evalplus_result(response)
        tree = ast.parse(code)
    except (ValueError, SyntaxError):
        return response
    if not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry_point
        for node in tree.body
    ):
        return response
    snake = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", entry_point).lower()
    aliases = sorted({entry_point.lower(), snake} - {entry_point})
    adapter = CALL_ADAPTER.replace("{entry_point}", entry_point).replace("{aliases}", repr(aliases))
    return "```python\n" + code.rstrip() + "\n" + adapter + "```"


def decompose_prompt(
    problem: dict[str, Any],
    method: str = "heuristic",
    llm: Callable[[str], str] | None = None,
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
        if llm is None:
            raise ValueError("LLM decomposition requires an llm")
        elements = _decompose_with_llm(description, problem["entry_point"], llm)
        if elements:
            return context, elements

    return context, _decompose_with_heuristic(description)


def _decompose_with_llm(description: str, entry_point: str, llm: Callable[[str], str]) -> list[str]:
    response = llm(fill(DECOMPOSE_PROMPT, prompt=description.strip(), entry_point=entry_point))
    elements = parse_python_list(response)
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


########################################################################
# Multi-agent infrastructure
########################################################################


@dataclass
class SharedMemory:
    """Shared memory that all agents read from and write to."""

    problem: dict[str, Any]
    clarifications: list[tuple[str, str]] = field(default_factory=list)
    finding: str | None = None
    spec: dict[str, Any] | None = None
    tests: dict[str, Any] | None = None
    code: str | None = None
    clean_task: str | None = None
    spec_task: str | None = None
    trace: list[dict[str, str]] = field(default_factory=list)
    started: float = field(default_factory=time.monotonic)

    @property
    def task(self) -> str:
        """The latest specification, or original task, with clarification history."""
        task = self.render_spec_task() if self.spec is not None else self.problem["prompt"]
        if self.clarifications:
            task += fill(
                CLARIFICATION_HISTORY,
                clarifications=to_json(self.clarifications),
            )
        return task

    def render_spec_task(self) -> str:
        """Render the spec as task text while preserving the original code context."""
        context, _ = decompose_prompt(self.problem)
        if any(row["id"] == "RAW_TASK_FALLBACK" for row in self.spec["requirements"]):
            context = DOCSTRING_SLOT
        elements = [f"Function: {self.problem['entry_point']}"]
        elements.extend(row["requirement"] for row in self.spec["requirements"])
        elements.extend(
            example["case"]
            for example in self.spec["examples"]
            if isinstance(example, dict) and isinstance(example.get("case"), str)
        )
        for name in ("unresolved", "assumptions"):
            if self.spec[name]:
                elements.append(
                    f"{name.upper()} (not established requirements): " + to_json(self.spec[name])
                )
        return compose_prompt(context, elements)

    @property
    def current_problem(self) -> dict[str, Any]:
        return {"prompt": self.task, "entry_point": self.problem["entry_point"]}

    @property
    def clean_spec(self) -> dict[str, Any]:
        """The spec without traces of the resolved defect (superseded statements,
        raw Q/A, validation issues); answers remain as ANSWER_n requirements, and
        the task rewritten with the answers keeps the original's other details."""
        spec = {key: self.spec[key] for key in CLEAN_SPEC_FIELDS}
        if self.clean_task is not None:
            spec["task"] = self.clean_task
        return spec


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable[..., Any]

    @property
    def definition(self) -> dict[str, Any]:
        """The tool in the OpenAI function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters),
                },
            },
        }


def run_candidates(
    exec_code: Callable[[str], str],
    sources: list[str],
    inputs: list[tuple],
    entry_point: str,
) -> list[list[str]] | None:
    """Outputs of every candidate on every input, or None if the sandbox failed."""
    script = (
        f"_sources = {sources!r}\n"
        f"_inputs = {inputs!r}\n"
        f"_entry_point = {entry_point!r}\n"
        f"{BEHAVIOR_HARNESS}"
    )
    output = exec_code(script)
    for line in output.splitlines():
        if line.startswith("__BEHAVIORS__"):
            return json.loads(line[len("__BEHAVIORS__") :])
    return None


def exception_name(error: BaseException) -> str:
    """Class name of an exception, e.g. 'ValueError' (from "<class 'ValueError'>")."""
    return str(type(error)).split("'")[1].rsplit(".", 1)[-1]


def run_tests(
    exec_code: Callable[[str], str],
    code: str,
    entry_point: str,
    tests: list[dict[str, Any]],
    timeout: float,
    format_issue: str = "",
) -> dict[str, Any]:
    """Static checks and generated tests on one candidate, retried once."""
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
    script = "import json\n_payload = json.loads(" + repr(payload) + ")\n" + TEST_HARNESS
    output = ""
    for _ in range(2):
        try:
            output = exec_code(script)
        except Exception as error:
            output = exception_name(error) + ": " + str(error)
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


class ToolBox:
    """Environment capabilities exposed to agents as tools; every call is traced."""

    def __init__(self, env: ClarificationEnvironment, memory: SharedMemory):
        self.memory = memory
        entry_point = memory.problem["entry_point"]
        tools = (
            Tool(
                "llm",
                "Query the language model.",
                {"prompt": {"type": "string"}},
                lambda prompt: env.llm(prompt),
            ),
            Tool(
                "decide",
                "Answer structured choice questions with the decision model.",
                {"questions": {"type": "object"}, "context": {"type": "object"}},
                lambda questions, context: env.decide(questions=questions, context=context),
            ),
            Tool(
                "ask_human",
                "Ask the user one clarification question and return the answer.",
                {"question": {"type": "string"}},
                lambda question: env.ask_human(question),
            ),
            Tool(
                "run_candidates",
                "Run candidate solutions on test inputs in the sandbox and return "
                "the output of each candidate on each input.",
                {
                    "sources": {"type": "array", "items": {"type": "string"}},
                    "inputs": {"type": "array", "items": {"type": "array"}},
                },
                lambda sources, inputs: run_candidates(env.exec_code, sources, inputs, entry_point),
            ),
            Tool(
                "run_tests",
                "Run static checks and generated tests on a candidate in the "
                "sandbox and return the result of each check.",
                {
                    "code": {"type": "string"},
                    "tests": {"type": "array", "items": {"type": "object"}},
                    "timeout": {"type": "number"},
                    "format_issue": {"type": "string"},
                },
                lambda code, tests, timeout, format_issue: run_tests(
                    env.exec_code, code, entry_point, tests, timeout, format_issue
                ),
            ),
        )
        self.tools = {tool.name: tool for tool in tools}

    @property
    def definitions(self) -> list[dict[str, Any]]:
        return [tool.definition for tool in self.tools.values()]

    def call(self, agent: str, name: str, **arguments: Any) -> Any:
        self.memory.trace.append({"agent": agent, "tool": name})
        return self.tools[name].function(**arguments)


class Agent:
    """An agent with one role that acts on the world only through tools."""

    name = "agent"

    def __init__(self, tools: ToolBox, config: dict[str, Any]):
        self.tools = tools
        self.config = config

    def call(self, tool: str, **arguments: Any) -> Any:
        return self.tools.call(self.name, tool, **arguments)

    def llm(self, prompt: str) -> str:
        return self.call("llm", prompt=prompt)

    def out_of_time(self, limit: str) -> bool:
        """True once the task has run longer than `config[limit]` seconds."""
        elapsed = time.monotonic() - self.tools.memory.started
        if elapsed <= self.config[limit]:
            return False
        print(f"TIME LIMIT: {limit} ({elapsed:.0f}s)", flush=True)
        return True

    @property
    def entry_point(self) -> str:
        return self.tools.memory.problem["entry_point"]

    def fill(self, template: str, **values: Any) -> str:
        """Fills a prompt template; `{entry_point}` is always available."""
        return fill(template, entry_point=self.entry_point, **values)


########################################################################
# Agents: defect detection
########################################################################


class DefectDetector(Agent):
    """Finds a defect of the task (contradiction, ambiguity or omission)."""

    name = "defect_detector"

    def __init__(self, tools: ToolBox, config: dict[str, Any], test_designer: TestDesigner):
        self.tools = tools
        self.config = config
        self.test_designer = test_designer
        self.properties: dict[str, list[dict[str, str]] | None] = {}

    def detect(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Runs the checks in order; the first one that finds a defect wins."""
        checks = [
            self.dd_conflict_check,
            self.property_conflict_check,
            self.property_omission_check,
        ]
        if self.config["final_gate"]:
            checks.append(self.base_llm_judge)

        for i, check in enumerate(checks):
            if i and self.out_of_time("detect_time_limit"):
                break
            result = check(problem)
            if result is not None and result[0]:
                return result

        return (False, "")

    def dd_conflict_check(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Delta-debugging -like approach.
        Drops prose elements one by one (and all examples together) and reports the drops that change the behavior of the generated solution.
        """

        context, elements = decompose_prompt(problem, self.config["decomposition"], self.llm)
        if len(elements) < 2:
            return (False, None)

        inputs = self.test_designer.generate_inputs(problem)
        if not inputs:
            return (False, None)

        is_example = [e.startswith((">>>", "assert ")) for e in elements]
        groups = [[i] for i, example in enumerate(is_example) if not example][
            : self.config["max_dropped_elements"]
        ]
        examples = [i for i, example in enumerate(is_example) if example]
        if examples and len(examples) < len(elements):
            groups.append(examples)

        variants = [elements] + [
            [e for i, e in enumerate(elements) if i not in group] for group in groups
        ]
        sources = [self.generate_solution(compose_prompt(context, v)) for v in variants]
        behaviors = self.run_candidates(sources, inputs)
        if behaviors is None:
            return (False, None)

        reference = behaviors[0]
        findings = []
        for group, behavior in zip(groups, behaviors[1:], strict=True):
            if behavior == reference:
                continue
            k = next(k for k, (a, b) in enumerate(zip(reference, behavior, strict=True)) if a != b)
            dropped = f'"{elements[group[0]]}"' if len(group) == 1 else "all examples"
            findings.append(
                f"Dropping {dropped} changes {format_call(self.entry_point, inputs[k])} "
                f"from {reference[k]} to {behavior[k]}."
            )

        print(
            "DELTA DEBUGGING:",
            to_json(
                {
                    "elements": elements,
                    "inputs": repr(inputs),
                    "sources": sources,
                    "behaviors": behaviors,
                    "findings": findings,
                }
            ),
            flush=True,
        )
        if not findings:
            return (False, None)
        return self.judge(
            "DELTA VERIFICATION",
            "Contradiction",
            DELTA_VERIFICATION,
            task=problem["prompt"],
            findings="\n".join(findings),
        )

    def generate_solution(self, prompt: str) -> str:
        response = self.llm(self.fill(DEFAULT_MBPP_TEMPLATE, prompt=prompt))
        try:
            return _validate_and_parse_evalplus_result(response)
        except ValueError:
            return ""

    def run_candidates(self, sources: list[str], inputs: list[tuple]) -> list[list[str]] | None:
        return self.call("run_candidates", sources=sources, inputs=inputs)

    def property_conflict_check(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Asks the decision model whether stated properties conflict pairwise."""
        prompt = problem["prompt"]
        properties = self.extract_properties(problem)
        if properties is None:
            return (False, None)
        properties = [p for p in properties if p["quote"].strip()][:12]
        pairs = [(i, j) for i in range(len(properties)) for j in range(i + 1, len(properties))]
        conflicts = []
        for start in range(0, len(pairs), 64):
            batch = pairs[start : start + 64]
            questions = {
                f"pair_{i}_{j}": {
                    "type": "choice",
                    "instructions": fill(
                        PROPERTY_PAIR,
                        properties=to_json([properties[i], properties[j]]),
                    ),
                    "criteria": PROPERTY_PAIR_CRITERIA,
                }
                for i, j in batch
            }
            try:
                answers = self.call("decide", questions=questions, context={"task": prompt})
            except LimitsExceededException:
                raise
            except Exception as error:
                # Missing or unsupported decision model
                print("PROPERTY PAIRS UNAVAILABLE:", error, flush=True)
                return (False, None)
            print("PROPERTY PAIRS:", to_json(answers), flush=True)
            if not isinstance(answers, dict):
                continue
            for i, j in batch:
                answer = answers.get(f"pair_{i}_{j}", {})
                if isinstance(answer, dict) and answer.get("choice") == "conflict":
                    conflicts.append([properties[i], properties[j]])
        if not conflicts:
            return (False, None)
        return self.judge(
            "PROPERTY CONFLICT",
            "Contradiction",
            PROPERTY_CONFLICT_VERIFICATION,
            task=prompt,
            conflicts=to_json(conflicts),
        )

    def property_omission_check(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Looks for the unresolved choice that most changes a correct implementation."""
        if self.config["omission_check"] == "properties":
            return self.property_determination_check(problem)
        return self.judge("PROPERTY OMISSION", "Ambiguity", AMBIGUITY_CHECK, task=problem["prompt"])

    def property_determination_check(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Asks the decision model which properties the task leaves undetermined,
        then picks the one that most changes a correct implementation."""
        prompt = problem["prompt"]
        properties = self.extract_properties(problem)
        if not properties:
            return self.judge("PROPERTY OMISSION", "Ambiguity", AMBIGUITY_CHECK, task=prompt)
        questions = {
            f"property_{i}": {
                "type": "choice",
                "instructions": fill(PROPERTY_DETERMINED, property=to_json(p)),
                "criteria": PROPERTY_DETERMINED_CRITERIA,
            }
            for i, p in enumerate(properties)
        }
        try:
            answers = self.call("decide", questions=questions, context={"task": prompt})
        except LimitsExceededException:
            raise
        except Exception as error:
            # Missing or unsupported decision model
            print("PROPERTY DETERMINATION UNAVAILABLE:", error, flush=True)
            return self.judge("PROPERTY OMISSION", "Ambiguity", AMBIGUITY_CHECK, task=prompt)
        print("PROPERTY DETERMINATION:", to_json(answers), flush=True)
        if not isinstance(answers, dict):
            answers = {}
        undetermined = [
            p
            for i, p in enumerate(properties)
            if isinstance(answer := answers.get(f"property_{i}"), dict)
            and answer.get("choice") == "undetermined"
        ]
        if not undetermined:
            return (False, None)
        return self.judge(
            "PROPERTY OMISSION",
            "Ambiguity",
            OMISSION_SELECTION,
            task=prompt,
            properties=to_json(undetermined),
        )

    def extract_properties(self, problem: dict[str, Any]) -> list[dict[str, str]] | None:
        """Stated (quoted) and open (empty quote) properties of the task, extracted
        once per prompt and shared by the conflict and omission checks."""
        prompt = problem["prompt"]
        if prompt in self.properties:
            return self.properties[prompt]
        response = self.llm(self.fill(PROPERTY_EXTRACTION, task=prompt))
        source = " ".join(prompt.split())
        try:
            properties = parse_python_literal(response)
            if not isinstance(properties, list):
                raise ValueError("Expected a list of properties")
            properties = [
                p
                for p in properties
                if isinstance(p, dict)
                and all(isinstance(p.get(k), str) for k in ("name", "quote", "meaning"))
                and p["name"].strip()
                and p["meaning"].strip()
                # Quotes must be verbatim; open properties have none
                and " ".join(p["quote"].split()) in source
            ][:20]
            print("PROPERTIES:", to_json(properties), flush=True)
        except LITERAL_ERRORS as error:
            print("PROPERTY EXTRACTION UNAVAILABLE:", error, flush=True)
            properties = None
        self.properties[prompt] = properties
        return properties

    def follow_up_check(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Stricter check for questions after the first one about the task's meaning."""
        return self.judge("FOLLOW-UP GATE", "Defect", FOLLOW_UP_GATE, task=problem["prompt"])

    def base_llm_judge(self, problem: dict[str, Any]) -> tuple[bool, str | None]:
        """Final gate for tasks that no other check flagged."""
        return self.judge("FINAL GATE", "Defect", BASE_LLM_JUDGE, task=problem["prompt"])

    def judge(self, log_label: str, verdict: str, template: str, **values: Any) -> tuple[bool, str]:
        """Asks for a `<verdict>: yes/no` judgment and logs the response."""
        response = self.llm(self.fill(template, **values))
        print(f"{log_label}:", response, flush=True)
        return (parse_verdict(response, verdict), response)


########################################################################
# Agents: clarification and implementation
########################################################################


class Questioner(Agent):
    """Turns the detected defect into one question and asks the user."""

    name = "questioner"

    def ask(self, memory: SharedMemory) -> bool:
        """Returns False when no new grounded question remains."""
        question = self.llm(
            fill(QUESTION_PROMPT, task=memory.task, analysis=memory.finding)
        ).strip()
        if (
            question.upper() == "NONE"
            or not question
            or any(
                " ".join(question.lower().split()) == " ".join(q.lower().split())
                for q, _ in memory.clarifications
            )
        ):
            return False
        self.send(memory, question)
        return True

    def ask_signature(self, memory: SharedMemory) -> None:
        """Asks for the parameters of an entry point that the task does not declare."""
        self.send(memory, self.fill(SIGNATURE_QUESTION))

    def send(self, memory: SharedMemory, question: str) -> None:
        answer = self.call("ask_human", question=question)
        memory.clarifications.append((question, answer))
        print(
            "CLARIFICATION:",
            to_json([question, answer]),
            flush=True,
        )


class SpecWriter(Agent):
    """Consolidates the task and the answers into a frozen specification."""

    name = "spec_writer"

    def write(self, memory: SharedMemory) -> dict[str, Any]:
        problem, clarifications = memory.problem, memory.clarifications
        task = memory.spec_task or problem["prompt"]
        sources = {
            f"T{i}": line.strip()
            for i, line in enumerate((line for line in task.splitlines() if line.strip()), 1)
        }
        sources.update({f"A{i}": a for i, (_, a) in enumerate(clarifications, 1)})
        prompt = self.fill(
            SPEC_PROMPT,
            protocol=CODE_PROTOCOL,
            sources=to_json(sources),
            clarifications=to_json(clarifications),
        )
        errors, spec = [], None
        for attempt in range(2):
            raw = self.llm(prompt + (fill(SPEC_CORRECTION, errors=errors) if errors else ""))
            try:
                value = parse_json(raw)
                if not isinstance(value, dict) or not isinstance(value.get("requirements"), list):
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
                        or not cites(row.get("sources"), sources)
                    ):
                        errors.append("Invalid requirement or source citation: " + repr(row))
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
                        or not cites(example.get("sources"), sources)
                    ):
                        errors.append("Invalid example/source citation")
                spec = {
                    "entry_point": self.entry_point,
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
                "entry_point": self.entry_point,
                "protocol": CODE_PROTOCOL,
                "requirements": [
                    {
                        "id": "RAW_TASK_FALLBACK",
                        "requirement": task,
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
        print("FROZEN SPECIFICATION:", to_json(spec), flush=True)
        return spec

    def rewrite(self, memory: SharedMemory) -> str:
        """The task rewritten into one consistent text that follows the answers."""
        task = self.llm(
            self.fill(
                SPEC_REWRITE,
                task=memory.spec_task or memory.problem["prompt"],
                clarifications=to_json(memory.clarifications),
            )
        ).strip()
        print("REWRITTEN TASK:", task, flush=True)
        return task

    def preclean(self, memory: SharedMemory) -> str | None:
        """The task without a sentence that cannot hold with the rest, if the LLM
        finds one and its edit is a verified pure deletion."""
        task = memory.problem["prompt"]
        response = self.llm(self.fill(PRECLEAN, task=task))
        match = re.search(r"```(?:text)?[ \t]*\n(.*?)```", response, re.DOTALL)
        if not match:
            return None
        cleaned = match.group(1).strip("\n")
        if not is_pure_deletion(task, cleaned, self.entry_point):
            print("PRECLEAN REJECTED:", cleaned, flush=True)
            return None
        print("PRECLEANED TASK:", cleaned, flush=True)
        return cleaned


class TestDesigner(Agent):
    """Writes tests from the frozen specification, reviews and revises them.
    Also provides oracle-free probe inputs to the DefectDetector."""

    name = "test_designer"

    def example_tests(self, memory: SharedMemory) -> list[dict[str, Any]]:
        """Checks for the examples stated in the (rewritten) task."""
        task = memory.clean_task or memory.spec_task or memory.problem["prompt"]
        tests = []
        for i, (args, expected) in enumerate(parse_examples(task, self.entry_point), 1):
            call = format_call(self.entry_point, args)
            code = (
                "def check(fn, source, tree):\n"
                f"    args, expected = {args!r}, {expected!r}\n"
                "    result = fn(*args)\n"
                "    close = isinstance(expected, float) and isinstance(result, (int, float))\n"
                "    assert result == expected or close and abs(result - expected) <= 1e-6 * max(1.0, abs(expected)), "
                f"{call + ' should return ' + repr(expected) + ', got '!r} + repr(result)\n"
            )
            tests.append(
                {
                    "id": f"example_{i}",
                    "requirement_ids": ["EXAMPLES"],
                    "kind": "functional",
                    "description": f"Stated example: {call} == {expected!r}",
                    "code": code,
                }
            )
        print("EXAMPLE CHECKS:", to_json([t["description"] for t in tests]), flush=True)
        return tests

    def generate_inputs(self, problem: dict[str, Any], num_inputs: int = 10) -> list[tuple]:
        response = self.llm(
            self.fill(GEN_TEST_INPUTS, prompt=problem["prompt"], num_inputs=num_inputs)
        )
        inputs = parse_python_list(response)
        return [args if isinstance(args, tuple) else (args,) for args in inputs][:num_inputs]

    def design(self, memory: SharedMemory) -> dict[str, Any]:
        spec = memory.clean_spec
        frozen_spec = to_json(spec, sort_keys=True)
        requirement_ids = {r["id"] for r in spec["requirements"]}
        prompt = fill(TEST_GENERATOR, max_tests=self.config["max_tests"], spec=frozen_spec)
        best, previous, review = None, "", ""
        for version in range(1, self.config["max_test_versions"] + 1):
            if version > 1 and self.out_of_time("test_time_limit"):
                break
            raw = self.llm(
                prompt + (fill(TEST_REVISION, previous=previous, review=review) if previous else "")
            )
            issues, tests, not_testable, test_ids = [], [], [], set()
            try:
                value = parse_json(raw)
                if not isinstance(value, dict) or not isinstance(value.get("tests"), list):
                    raise ValueError("Expected a tests list")
                for row in value["tests"][: self.config["max_tests"]]:
                    try:
                        if (
                            not isinstance(row, dict)
                            or not isinstance(row.get("id"), str)
                            or not row["id"]
                            or row["id"] in test_ids
                            or not cites(row.get("requirement_ids"), requirement_ids)
                            or row.get("kind") not in {"functional", "property", "static"}
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
                                and not (isinstance(n.test, ast.Constant) and n.test.value is True)
                                for n in ast.walk(check)
                            )
                            or any(
                                isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
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
                        and cites(row.get("requirement_ids"), requirement_ids)
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
            covered = {r for row in tests + not_testable for r in row["requirement_ids"]}
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
            # Mechanical issues replace the review
            review = (
                "VERDICT: REVISE\n" + "\n".join(issues)
                if issues
                else self.review(frozen_spec, suite)
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
                to_json(suite),
                flush=True,
            )
            rank = (not approved, len(missing), len(issues), -len(tests), -version)
            if best is None or rank < best[0]:
                best = (rank, suite)
            previous = raw
            if approved:
                break
        if to_json(spec, sort_keys=True) != frozen_spec:
            raise RuntimeError("Frozen specification changed during test review")
        print("FROZEN TESTS:", to_json(best[1]), flush=True)
        return best[1]

    def review(self, frozen_spec: str, suite: dict[str, Any]) -> str:
        return self.llm(
            fill(
                TEST_REVIEW,
                spec=frozen_spec,
                tests=to_json(suite),
            )
        ).strip()


class Coder(Agent):
    """Implements the specification and repairs it with real test failures."""

    name = "coder"

    def implement(self, memory: SharedMemory) -> str:
        spec, tests = memory.clean_spec, memory.tests
        frozen_spec = to_json(spec, sort_keys=True)
        frozen_tests = to_json(tests, sort_keys=True)
        best, feedback, previous, seen = None, "", "", set()
        for attempt in range(1, self.config["max_code_attempts"] + 1):
            if attempt > 1 and self.out_of_time("code_time_limit"):
                break
            try:
                raw = self.llm(
                    self.fill(
                        CODE_GENERATOR,
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
            execution = self.call(
                "run_tests",
                code=code,
                tests=tests["tests"],
                timeout=self.config["test_timeout"],
                format_issue=format_issue,
            )
            passed = {r["id"] for r in execution["checks"] if r["status"] == "passed"}
            eligible = execution["status"] == "ok"
            if best is None or eligible and (not best["eligible"] or passed > best["passed"]):
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
                to_json(execution),
                flush=True,
            )
            if (
                eligible
                and execution["checks"]
                and all(r["status"] == "passed" for r in execution["checks"])
            ):
                break
            if code in seen or not eligible or attempt == self.config["max_code_attempts"]:
                break
            seen.add(code)
            failures = [r for r in best["execution"]["checks"] if r["status"] != "passed"]
            feedback = fill(
                CODE_FEEDBACK,
                failures=to_json(failures),
                passed=sorted(best["passed"]),
            )
            if best["attempt"] != attempt:
                latest = [r for r in execution["checks"] if r["status"] != "passed"]
                feedback += fill(
                    CODE_FEEDBACK_LATEST,
                    failures=to_json(latest),
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


########################################################################
# Orchestrator
########################################################################

MODE_DETECT, MODE_ASK, MODE_SPECIFY, MODE_TEST, MODE_CODE, MODE_DONE = (
    "DETECT",
    "ASK",
    "SPECIFY",
    "TEST",
    "CODE",
    "DONE",
)


class Orchestrator:
    """Runs the agents as a state machine over a shared memory.

    DETECT -> ASK -> refresh spec -> DETECT ... (while questions remain)
           -> SPECIFY -> TEST -> CODE -> DONE
    """

    def __init__(
        self,
        env: ClarificationEnvironment,
        problem: dict[str, Any],
        config: dict[str, Any],
    ):
        self.env = env
        self.config = config
        self.memory = SharedMemory(problem)
        self.tools = ToolBox(env, self.memory)
        self.mode = MODE_DETECT
        self.signature_checked = False
        self.questions_on_meaning = 0

        self.test_designer = TestDesigner(self.tools, config)
        self.detector = DefectDetector(self.tools, config, self.test_designer)
        self.questioner = Questioner(self.tools, config)
        self.spec_writer = SpecWriter(self.tools, config)
        self.coder = Coder(self.tools, config)

    def run(self) -> str:
        while self.mode != MODE_DONE:
            self.step()
        print("AGENT TRACE:", json.dumps(self.memory.trace), flush=True)
        return self.memory.code

    def step(self) -> None:
        if self.mode == MODE_DETECT:
            """
            * Detect: find one defect to ask about
            """
            if not self.env.can_ask():
                self.mode = MODE_SPECIFY
                return
            if not self.signature_checked:
                # Without a signature the arguments are a guess, so ask for them first
                self.signature_checked = True
                if not has_signature(self.memory.problem["prompt"]):
                    try:
                        self.questioner.ask_signature(self.memory)
                    except (TooManyQuestionException, LimitsExceededException):
                        self.mode = MODE_SPECIFY
                    return
            try:
                if self.questions_on_meaning >= 1:
                    if self.detector.out_of_time("detect_time_limit"):
                        self.mode = MODE_SPECIFY
                        return
                    detected, finding = self.detector.follow_up_check(self.memory.current_problem)
                else:
                    detected, finding = self.detector.detect(self.memory.current_problem)
            except (TooManyQuestionException, LimitsExceededException):
                self.mode = MODE_SPECIFY
                return
            self.memory.finding = finding
            self.mode = MODE_ASK if detected else MODE_SPECIFY

        elif self.mode == MODE_ASK:
            """
            * Ask: one question about the finding
            """
            try:
                asked = self.questioner.ask(self.memory)
                self.questions_on_meaning += asked
                if asked and self.env.can_ask():
                    self.memory.spec = self.spec_writer.write(self.memory)
            except (TooManyQuestionException, LimitsExceededException):
                asked = False
            self.mode = MODE_DETECT if asked else MODE_SPECIFY

        elif self.mode == MODE_SPECIFY:
            self.memory.spec_task = self.spec_writer.preclean(self.memory)
            self.memory.spec = self.spec_writer.write(self.memory)
            if self.memory.clarifications:
                self.memory.clean_task = self.spec_writer.rewrite(self.memory)
            self.mode = MODE_TEST

        elif self.mode == MODE_TEST:
            self.memory.tests = self.test_designer.design(self.memory)
            self.memory.tests["tests"] += self.test_designer.example_tests(self.memory)
            self.mode = MODE_CODE

        elif self.mode == MODE_CODE:
            self.memory.code = self.coder.implement(self.memory)
            self.memory.code = with_call_adapter(
                self.memory.code, self.memory.problem["entry_point"]
            )
            self.mode = MODE_DONE


########################################################################
# Clarifier
########################################################################


class SHWClarifier(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {
        "decomposition": "llm",  # "llm"
        "max_dropped_elements": 6,
        "final_gate": True,  # base_llm_judge when no other check fires
        "omission_check": "single",  # "single": one holistic prompt | "properties": per-property determination,
        "max_test_versions": 3,
        "max_code_attempts": 4,
        "max_tests": 24,
        "test_timeout": 0.5,
        # Seconds after the task start at which a stage stops early, since the
        # SDK restarts a task that runs longer than 300 seconds
        "detect_time_limit": 90,
        "test_time_limit": 150,
        "code_time_limit": 210,
    }

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        return Orchestrator(env, problem, self.config).run()

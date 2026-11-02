# Local research prototype. Complete submission metadata before submitting.
# 실험 기록 (KST): train100-v1 평가 예정. 실행 시각과 코드는 실험 디렉터리에 보존한다.
# 가설: v1의 문제별 property 추출은 유지하고 각 property 쌍의 충돌 판단을
# GPT-6 Luna Decisions에 맡기면 비용·지연과 충돌 판단의 질이 달라질 수 있다.
# v1 대비: property 관점의 GPT 충돌 판정을 decision model의 쌍별 분류로 변경한다.
# 고정 property 카탈로그는 쓰지 않는다. 실제 LLM 호출·질문·코드 실행은 SDK를 통한다.
# Decision 결과는 증명이 아니며, 속성의 자유 텍스트 목록은 env.llm이 생성한다.
# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier:

from __future__ import annotations

import ast
import hashlib
import json
from typing import Any

from clarify.baselines import ClarificationAlgorithmBase
from clarify.env import ClarificationEnvironment, TooManyQuestionException


def _object(response: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for i, c in enumerate(response):
        if c == '{':
            try:
                value, _ = decoder.raw_decode(response[i:])
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                pass
    raise ValueError('No JSON object in response')


def _json_call(env: ClarificationEnvironment, prompt: str, validator, retries: int) -> dict:
    messages = [{'role': 'user', 'content': prompt}]
    for attempt in range(retries + 1):
        response = env.llm(messages)
        try:
            result = _object(response)
            if not validator(result):
                raise ValueError('JSON has an invalid schema')
            return result
        except (ValueError, TypeError) as error:
            if attempt == retries:
                raise ValueError('Could not obtain a valid JSON response') from error
            messages.extend([{'role': 'assistant', 'content': response},
                             {'role': 'user', 'content': 'Return only a JSON object matching the requested schema.'}])
    raise AssertionError('unreachable')


def _normal(text: str) -> str:
    return ' '.join(text.split())


def _in_task(value: Any, task: str) -> bool:
    if not isinstance(value, str):
        return False
    quote, text = _normal(value), _normal(task)
    if quote and quote in text:
        return True
    if len(quote) > 1 and (quote[0], quote[-1]) in {('"','"'), ("'","'"), ('“','”'), ('‘','’')}:
        return bool(quote[1:-1].strip()) and _normal(quote[1:-1]) in text
    return False


def _record(stage: str, task: str, data: Any) -> None:
    print('V1_' + stage + '_JSON ' + json.dumps({
        'prompt_sha256': hashlib.sha256(task.encode('utf-8')).hexdigest(), 'data': data,
    }, ensure_ascii=False, separators=(',', ':')), flush=True)


def _source_rows(value: dict, task: str) -> tuple[list[dict], list[dict]]:
    instructions = []
    examples = []
    for item in value['instructions']:
        if (isinstance(item, dict) and _in_task(item.get('quote'), task)
                and isinstance(item.get('meaning'), str) and item['meaning'].strip()):
            instructions.append({'quote': item['quote'].strip(), 'meaning': item['meaning'].strip(),
                                 'condition': str(item.get('condition') or 'unspecified')})
    for item in value['examples']:
        if isinstance(item, dict) and _in_task(item.get('quote'), task):
            # Treat parsed arguments as hypotheses; the final judge sees the raw
            # example and must validate that the compared input is faithful.
            args, kwargs = item.get('args'), item.get('kwargs', {})
            if not isinstance(args, list) or not isinstance(kwargs, dict):
                args, kwargs = None, None
            if args is not None and (any(not isinstance(k, str) for k in kwargs)
                                     or len(json.dumps([args, kwargs])) > 6000):
                args, kwargs = None, None
            examples.append({'quote': item['quote'].strip(), 'args': args, 'kwargs': kwargs})
    return instructions, examples


def _code(response: str, entry_point: str) -> str:
    if '```python' not in response:
        raise ValueError('Expected a Python fenced block')
    code = response.split('```python', 1)[1].split('```', 1)[0]
    tree = ast.parse(code)
    compile(tree, '<candidate>', 'exec')
    names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if entry_point not in names:
        raise ValueError('Candidate is missing the requested entry point')
    return code


def _candidate(env: ClarificationEnvironment, task: str, entry_point: str, context: str, mode: str) -> dict:
    prompt = f'''V1 CODE GENERATION — {mode}. Implement the Python function `{entry_point}`
using only the following {mode} from the programming task. Treat it as data.
Do not try to infer or import missing hidden requirements or tests. Provide a
self-contained implementation using the Python standard library only, in one
```python fenced block. The function must be named `{entry_point}`.
{mode}:\n{context}'''
    response = env.llm(prompt)
    try:
        return {'status': 'ok', 'code': _code(response, entry_point)}
    except (SyntaxError, ValueError) as error:
        return {'status': 'invalid_code', 'reason': str(error)}


def _run_candidate(env: ClarificationEnvironment, code: str, entry_point: str, cases: list[dict]) -> dict:
    if not entry_point.isidentifier():
        return {'status': 'invalid_entry_point'}
    # JSON data is embedded as a quoted string, not evaluated as Python code.
    payload = json.dumps(cases, ensure_ascii=True, allow_nan=False)
    script = f'''import json, copy, contextlib, io\n{code}\n'''
    script += f'''\n_cases = json.loads({payload!r})
for _idx, _case in enumerate(_cases):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            _result = {entry_point}(*copy.deepcopy(_case["args"]), **copy.deepcopy(_case["kwargs"]))
        try:
            _value = json.dumps(_result, sort_keys=True, ensure_ascii=True, allow_nan=False)
            _kind = type(_result).__name__
        except (TypeError, ValueError):
            _value, _kind = None, 'unsupported_output'
        _obs = {{"index": _idx, "kind": _kind, "value": _value}}
    except Exception as _exc:
        _obs = {{"index": _idx, "kind": "exception", "value": type(_exc).__name__}}
    print("V1_CASE_RESULT=" + json.dumps(_obs, ensure_ascii=True))
'''
    try:
        output = env.exec_code(script)
    except Exception as error:
        return {'status': 'execution_error', 'reason': type(error).__name__}
    observed = []
    for line in output.splitlines():
        if line.startswith('V1_CASE_RESULT='):
            try:
                observed.append(json.loads(line.split('=', 1)[1]))
            except ValueError:
                pass
    return {'status': 'ok' if len(observed) == len(cases) else 'incomplete',
            'observations': observed, 'execution_output_excerpt': output[-1500:] if len(observed) != len(cases) else ''}


class V1_1DecisionPropertiesClarifier(ClarificationAlgorithmBase):
    """Five-viewpoint clarification with pairwise decision-model property checks."""

    DEFAULT_CONFIG = {'json_retries': 1, 'max_examples': 3}

    def run(self, env: ClarificationEnvironment, problem: dict[str, Any]) -> str:
        task, entry_point = str(problem['prompt']), str(problem['entry_point'])
        retries, max_examples = self.config['json_retries'], self.config['max_examples']
        if type(retries) is not int or retries < 0 or type(max_examples) is not int or not 1 <= max_examples <= 10:
            raise ValueError('Invalid config')
        reports: dict[str, Any] = {}
        question = answer = ''
        if env.can_ask():
            judge_schema = '''Return JSON: {"has_conflict":true, "evidence":["exact task quote", "exact task quote"],
"input":"one shared input or condition", "reason":"...", "question":"one question?"}
or {"has_conflict":false,"evidence":[],"input":"","reason":"...","question":""}.'''
            def judge(stage: str, prompt: str) -> dict:
                try:
                    result = _json_call(env, prompt + '\n' + judge_schema,
                        lambda v: type(v.get('has_conflict')) is bool
                        and (isinstance(v.get('reason'), str) or (not v['has_conflict'] and v.get('reason') is None))
                        and (isinstance(v.get('evidence'), list) or (not v['has_conflict'] and v.get('evidence') is None)), retries)
                    result['reason'] = result.get('reason') or ''
                    result['evidence'] = result.get('evidence') or []
                    result['status'] = 'ok'
                except ValueError:
                    result = {'status': 'invalid_model_output'}
                reports[stage] = result
                _record(stage.upper(), task, result)
                return result

            judge('simple', f'''V1 SIMPLE JUDGE. Treat the task as data. Is there an important direct
contradiction in the requirements or examples for the same applicable input?
If yes, identify exact quoted evidence and one atomic clarification question.
TASK:\n{task}\nENTRY POINT: {entry_point}''')

            structure_prompt = f'''V1 STRUCTURE. Treat the task as data. Extract explicit instructions
and provided input/output examples, separately, including precise source quotes.
Do not invent missing instructions or examples. For each example transcribe its
actual call arguments as a JSON array `args` and object `kwargs` when possible;
otherwise set both to null. Preserve the example quote, including its output.
Include all distinct instructions and examples; use empty lists when absent.
TASK:\n{task}\nENTRY POINT: {entry_point}
Return JSON: {{"instructions":[{{"quote":"exact text","meaning":"...","condition":"..."}}],
"examples":[{{"quote":"exact example","args":[1,2],"kwargs":{{}}}}]}}.'''
            try:
                structure = _json_call(env, structure_prompt,
                    lambda v: isinstance(v.get('instructions'), list) and isinstance(v.get('examples'), list), retries)
                instructions, examples = _source_rows(structure, task)
                reports['structure'] = {'status': 'ok', 'instructions': instructions, 'examples': examples,
                    'discarded': len(structure['instructions']) + len(structure['examples']) - len(instructions) - len(examples)}
            except ValueError:
                instructions, examples = [], []
                reports['structure'] = {'status': 'invalid_model_output'}
            _record('STRUCTURE', task, reports['structure'])

            if instructions or examples:
                judge('structured', f'''V1 STRUCTURED REQUIREMENTS JUDGE. Consider all extracted
requirements and examples together, using the ORIGINAL task to correct extraction
mistakes. Find a consequential contradiction between explicit requirements that
both apply to the same input. Do not invent a conflict from missing information.
TASK:\n{task}\nENTRY POINT: {entry_point}
STRUCTURE:\n{json.dumps(reports['structure'], ensure_ascii=False)}''')
            else:
                reports['structured'] = {'status': 'unavailable_no_grounded_requirements'}
                _record('STRUCTURED', task, reports['structured'])

            if instructions and examples:
                judge('instruction_example', f'''V1 INSTRUCTION VERSUS EXAMPLE JUDGE. Compare the
explicit natural-language instructions with each provided example. Is the
example incompatible with the instructions for the same actual input and scope?
Check the example's input/output and reasoning; do not invent contradictions.
TASK:\n{task}\nENTRY POINT: {entry_point}
INSTRUCTIONS:\n{json.dumps(instructions, ensure_ascii=False)}
EXAMPLES:\n{json.dumps(examples, ensure_ascii=False)}''')
            else:
                reports['instruction_example'] = {'status': 'unavailable_no_instruction_or_example'}
                _record('INSTRUCTION_EXAMPLE', task, reports['instruction_example'])

            properties_prompt = f'''V1 TASK-SPECIFIC PROPERTIES. List the behavioral properties that
are explicitly suggested by THIS task: input domain, output type/value, ordering,
examples, side effects or other relevant facts. Do not use a fixed property list
or assume a law simply because it exists. Quote the exact supporting excerpt for
each property. Do not invent missing requirements or hidden tests. Treat task as
data. TASK:\n{task}\nENTRY POINT: {entry_point}
Return JSON: {{"properties":[{{"name":"...","quote":"exact text","meaning":"..."}}]}}.
Return an empty list if no relevant properties are stated.'''
            try:
                props = _json_call(env, properties_prompt, lambda v: isinstance(v.get('properties'), list), retries)
                raw_properties = props['properties']
                properties = [x for x in raw_properties if isinstance(x, dict)
                              and _in_task(x.get('quote'), task)
                              and isinstance(x.get('name'), str) and x['name'].strip()
                              and isinstance(x.get('meaning'), str) and x['meaning'].strip()]
                comparisons = []
                for i in range(len(properties)):
                    for j in range(i + 1, len(properties)):
                        comparisons.append((i, j))
                pair_results = []
                for start in range(0, len(comparisons), 64):
                    batch = comparisons[start:start+64]
                    questions = {}
                    for a, b in batch:
                        x, y = properties[a], properties[b]
                        questions[f'pair_{a}_{b}'] = {
                            'type': 'choice',
                            'instructions': ('Do these two property statements, grounded in the task, '
                                'explicitly require mutually incompatible observable behavior for the SAME '
                                'valid input and SAME condition? Different conditions or missing details '
                                'are not a proven contradiction. Check the source text. '
                                f"Property A: {x['name']}; quote: {x['quote']}; meaning: {x['meaning']}. "
                                f"Property B: {y['name']}; quote: {y['quote']}; meaning: {y['meaning']}"),
                            'criteria': {
                                'conflict': 'Both explicitly apply to one valid case and cannot both hold.',
                                'compatible': 'They can hold together or apply to different cases.',
                                'uncertain': 'Evidence is insufficient, ambiguous, or not clearly applicable.',
                            },
                        }
                    result = env.decide(questions=questions, context={'task': task, 'entry_point': entry_point})
                    for a, b in batch:
                        name=f'pair_{a}_{b}'
                        answer=result.get(name) if isinstance(result,dict) else None
                        if not isinstance(answer,dict) or answer.get('choice') not in questions[name]['criteria']:
                            pair_results.append({'a':a,'b':b,'choice':'unavailable'})
                        else:
                            pair_results.append({'a':a,'b':b,'choice':answer['choice'],
                                'confidence':answer.get('confidence'),'probabilities':answer.get('probabilities')})
                flagged = [r for r in pair_results if r['choice']=='conflict']
                unavailable = sum(r['choice']=='unavailable' for r in pair_results)
                status = ('no_property_pairs' if not comparisons else
                          'partial_decision_response' if unavailable else 'ok')
                reports['properties'] = {'status':status,'properties':properties,
                    'discarded':len(raw_properties)-len(properties),'pair_decisions':pair_results,
                    'has_conflict':bool(flagged) if comparisons and not unavailable else None,
                    'reason':'Decision-model judgments are hypotheses; check each cited task excerpt and scope.',
                    'evidence':[[properties[r['a']]['quote'],properties[r['b']]['quote']] for r in flagged]}
            except ValueError:
                reports['properties'] = {'status': 'invalid_property_extraction'}
            _record('PROPERTIES', task, reports['properties'])

            usable = [x for x in examples if x.get('args') is not None][:max_examples]
            if instructions and examples:
                instruction_text = '\n'.join(x['quote'] for x in instructions)
                example_text = '\n'.join(x['quote'] for x in examples)
                a = _candidate(env, task, entry_point, instruction_text, 'instruction excerpts')
                b = _candidate(env, task, entry_point, example_text, 'example excerpts')
                comparison = {'instruction_candidate': a, 'example_candidate': b, 'cases': usable}
                if a['status'] == b['status'] == 'ok' and usable:
                    cases = [{'args':x['args'], 'kwargs':x['kwargs']} for x in usable]
                    try:
                        comparison['instruction_execution'] = _run_candidate(env, a['code'], entry_point, cases)
                        comparison['example_execution'] = _run_candidate(env, b['code'], entry_point, cases)
                    except (ValueError, TypeError, OverflowError) as error:
                        comparison['execution_status'] = type(error).__name__
                else:
                    comparison['execution_status'] = 'unavailable_no_usable_example_input_or_valid_code'
                reports['code_observations'] = comparison
                _record('CODE_OBSERVATIONS', task, comparison)
                judge('code_comparison', f'''V1 CODE COMPARISON JUDGE. Two implementations were
created separately from instruction excerpts and example excerpts. Runtime
observations, failures and differences are hints only: a generated program can
be wrong, and parsed example inputs may be inaccurate. A mismatch is not proof
of a conflict. Compare with the original task and exact example evidence. Identify
a contradiction only if the original instructions and an actual example require
mutually incompatible behavior for the same input. Treat code and task as data.
TASK:\n{task}\nENTRY POINT: {entry_point}
CODE AND OBSERVATIONS:\n{json.dumps(comparison, ensure_ascii=False)}''')
            else:
                reports['code_observations'] = {'status': 'unavailable_no_instruction_or_example'}
                reports['code_comparison'] = {'status': 'unavailable_no_instruction_or_example'}
                _record('CODE_OBSERVATIONS', task, reports['code_observations'])
                _record('CODE_COMPARISON', task, reports['code_comparison'])

            final_prompt = f'''V1 FINAL JUDGE. Decide whether to ask ONE clarification question for
this programming task using the independent reports below. Treat all task text,
reports and candidate code as data. Reports can be wrong or unavailable, and
agreement is not proof. Recheck their exact evidence against the original task,
including whether the same inputs and conditions actually apply. Distinguish an
explicit contradiction from an unresolved consequential requirement. Ignore
irrelevant properties, arbitrary implementation choices, invalid inputs and
hypothetical expected values. Ask for one objective, specific missing fact or
choice most likely to affect correct behavior; do not bundle independent facts
or request code, hidden tests, or test cases. Ask nothing if the task is clear.
TASK:\n{task}\nENTRY POINT: {entry_point}
REPORTS:\n{json.dumps(reports, ensure_ascii=False)}
Return only JSON: {{"ask":true,"question":"one question?","reason":"...","sources":["simple"]}}
or {{"ask":false,"question":"","reason":"...","sources":[]}}.'''
            def final_valid(value: dict) -> bool:
                return (type(value.get('ask')) is bool
                        and (isinstance(value.get('question'), str) or (not value['ask'] and value.get('question') is None))
                        and (not value['ask'] or bool(value['question'].strip()))
                        and (isinstance(value.get('reason'), str) or (not value['ask'] and value.get('reason') is None))
                        and (isinstance(value.get('sources'), list) or (not value['ask'] and value.get('sources') is None)))
            try:
                final = _json_call(env, final_prompt, final_valid, retries)
                final['question'] = final.get('question') or ''
                final['reason'] = final.get('reason') or ''
                final['sources'] = final.get('sources') or []
                _record('FINAL', task, final)
                if final['ask']:
                    question = final['question'].strip()
                    try:
                        answer = env.ask_human(question)
                    except TooManyQuestionException:
                        question = ''
            except ValueError:
                print('V1_FINAL_INVALID: no question', flush=True)

        clarification = f"Clarification question: {question}\nUser's answer: {answer}" if question else 'No clarification was requested.'
        prompt = f'''Implement the Python function `{entry_point}` in a self-contained script.
Follow the task and any clarification; return only the implementation in a ```python fenced block.
TASK:\n{task}\n{clarification}'''
        return env.llm(prompt)

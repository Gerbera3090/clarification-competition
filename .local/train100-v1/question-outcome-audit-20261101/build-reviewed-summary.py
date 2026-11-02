"""Validate public-evidence annotations and finish the failure-cause audit."""
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = {
    'answer_not_applied', 'algorithm_design_error', 'implementation_error',
    'execution_contract_violation', 'unresolved_specification',
    'answer_oracle_mismatch', 'instruction_oracle_mismatch',
    'evaluation_failure', 'insufficient_evidence',
}
LABELS = {
    'answer_not_applied': '답변 미반영',
    'unresolved_specification': '남은 명세',
    'answer_oracle_mismatch': '답변·채점 불일치',
    'instruction_oracle_mismatch': '공개 지시·채점 불일치',
    'algorithm_design_error': '알고리즘 설계 오류',
    'implementation_error': '구현 오류',
    'execution_contract_violation': '실행·제출 조건 위반',
    'evaluation_failure': '평가 문제',
    'insufficient_evidence': '근거 부족',
}


def read(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


for name in ('summary.json', 'cases.jsonl'):
    backup = ROOT / ('before-full-review-' + name)
    if not backup.exists():
        shutil.copyfile(ROOT / name, backup)
summary = json.loads((ROOT / 'before-full-review-summary.json').read_text())
cases = read(ROOT / 'before-full-review-cases.jsonl')
new_inputs = read(ROOT / 'review-input.jsonl')
refresh_inputs = read(ROOT / 'review-refresh-input.jsonl')
new_notes = []
for path in sorted(ROOT.glob('review-annotations*.jsonl')):
    new_notes.extend(read(path))
refresh_notes = read(ROOT / 'review-refresh-annotations.jsonl')
assert len(new_inputs) == len(new_notes) == 123
assert len(refresh_inputs) == len(refresh_notes) == 7
assert len({n['case_id'] for n in new_notes + refresh_notes}) == 130
notes_by_id = {n['case_id']: n for n in new_notes + refresh_notes}
by_case = {}
source_cache = {}
for source in new_inputs + refresh_inputs:
    note = notes_by_id[source['case_id']]
    assert note['category'] in CATEGORIES
    assert note['adherence'] in {'applied_supported', 'violated_supported', 'unclear'}
    assert note['confidence'] in {'high', 'medium', 'low'}
    assert 2 <= len(note['evidence']) <= 4 and note['reason'] and note['limits']
    path = Path(source['source'])
    source_cache.setdefault(str(path), read(path))
    raw = source_cache[str(path)][source['line'] - 1]
    actual = hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert actual == source['record_sha256'], source['case_id']
    by_case[(source['algorithm'], source['task_id'])] = (note, source)

reviewed = []
counts = Counter()
by_algorithm = {}
origins = Counter()
for case in cases:
    if case['bucket'] != 'high_score_fail':
        continue
    key = (case['algorithm'], case['task_id'])
    if key in by_case:
        note, source = by_case[key]
        origin = 'regraded_failure_refresh' if note['case_id'].startswith('RF') else 'new_case_review'
    else:
        assert 'prior_failure_analysis' in case, key
        note = dict(case['prior_failure_analysis'])
        origin = 'unchanged_prior_review'
        note['adherence'] = ('violated_supported' if note['category'] == 'answer_not_applied'
                             else 'applied_supported' if note['category'] == 'answer_oracle_mismatch'
                             else 'unclear')
    assert note['category'] in CATEGORIES
    path = Path(case['source'])
    source_cache.setdefault(str(path), read(path))
    raw = source_cache[str(path)][case['line'] - 1]
    assert raw['task_id'] == case['task_id'] and raw['algorithm'] == case['algorithm']
    assert raw['success'] is False and str(raw['clarification_history'][0][2]) == '3'
    analysis = {**note, 'report_bucket': note['category']}
    case['failure_analysis'] = analysis
    case['failure_review_origin'] = origin
    case['failure_review_status'] = 'reviewed'
    case['semantic_adherence'] = note['adherence']
    case['semantic_adherence_scope'] = 'Only the explicit fact asked; not proof of full specification compliance.'
    record = {**case, 'prompt': raw['prompt'], 'code': raw['prompt_result'],
              'test_result': raw['test_result'],
              'record_sha256': hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    reviewed.append(record)
    counts[note['category']] += 1
    by_algorithm.setdefault(case['algorithm'], Counter())[note['category']] += 1
    origins[origin] += 1

assert len(reviewed) == 352 and sum(counts.values()) == 352
assert origins == {'new_case_review': 123, 'regraded_failure_refresh': 7, 'unchanged_prior_review': 222}
for source in summary['sources']:
    assert sha(Path(source['path'])) == source['sha256'], source['path']
for algorithm in summary['algorithms']:
    name = algorithm['algorithm']
    rows = [r for r in reviewed if r['algorithm'] == name]
    assert len(rows) == algorithm['high_score_failures']
    algorithm['reviewed_high_score_failures'] = len(rows)
    algorithm['unreviewed_high_score_failures'] = 0
    algorithm['failure_categories'] = dict(by_algorithm.get(name, {}))
    algorithm['confirmed_answer_not_applied_primary_cause'] = [
        {'task_id':r['task_id'], 'source':r['source'], 'line':r['line'], 'evidence':r['failure_analysis']['reason']}
        for r in rows if r['failure_analysis']['category'] == 'answer_not_applied'
    ]
    algorithm['confirmed_secondary_answer_violation'] = [
        {'task_id':r['task_id'], 'source':r['source'], 'line':r['line'], 'evidence':r['failure_analysis']['reason']}
        for r in rows if r['failure_analysis']['category'] != 'answer_not_applied'
        and r['failure_analysis']['adherence'] == 'violated_supported'
    ]
summary.update(
    analysis_date='2026-11-02',
    phase='completed_high_score_failure_cause_review',
    failure_review={'total':352, 'reviewed':352, 'unreviewed':0,
                    'origins':dict(origins), 'categories':dict(counts), 'labels':LABELS,
                    'confidence':dict(Counter(r['failure_analysis']['confidence'] for r in reviewed)),
                    'primary_answer_not_applied':counts['answer_not_applied'],
                    'secondary_answer_violation_confirmed':sum(
                        r['failure_analysis']['category'] != 'answer_not_applied'
                        and r['failure_analysis']['adherence'] == 'violated_supported' for r in reviewed),
                    'uncertain_cause':counts['insufficient_evidence']},
    verification={'source_hashes_match':True, 'all_high_score_failures_have_causal_annotation':True,
                  'generated_code_reexecuted':False, 'provider_api_calls':0,
                  'canonical_solutions_or_reference_prompts_used':False,
                  'original_results_modified':False},
    limitations=[
        'High/low question quality remains the saved simulated-user score, not a new independent score.',
        'All 352 high-score failures have a primary-cause review. Other 548 outcomes were not newly reviewed for semantic adherence.',
        'A reviewed case may still have insufficient evidence; reviewed is not the same as certain.',
        'Primary cause concerns the first recorded failure; independent answer violations are recorded separately.',
        'Adherence describes the asked fact only. It does not certify every user requirement.',
        'Case judgments are evidence-based annotations, not formal proofs or population-level causal estimates.',
    ],
)
(ROOT / 'reviewed-failures.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in reviewed))
(ROOT / 'cases.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in cases))
write(ROOT / 'summary.json', summary)
print('REVIEWED',len(reviewed),'CATEGORIES',dict(counts),'ORIGINS',dict(origins))
for row in summary['algorithms']:
    print(row['algorithm'],row['reviewed_high_score_failures'],row['failure_categories'],
          'secondary violations',len(row['confirmed_secondary_answer_violation']))

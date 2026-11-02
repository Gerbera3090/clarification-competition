"""Join reviewed annotations, verify provenance, and render the offline report."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
LABELS = {
    'answer_not_applied': '답변을 코드에 반영하지 못함',
    'algorithm_design_error': '알고리즘 설계 오류',
    'implementation_error': '구현 오류',
    'execution_contract_violation': '실행 또는 제출 조건 위반',
    'unresolved_specification': '관련 명세가 아직 미해결',
    'answer_oracle_mismatch': '사용자 답변과 채점 기대값 불일치',
    'instruction_oracle_mismatch': '명확한 공개 지시와 채점 기대값 불일치',
    'evaluation_failure': '평가 호출 또는 환경 불일치',
    'insufficient_evidence': '실패 원인을 판별할 증거 부족',
    'invalid_answer': '3점 판정이지만 유효한 답변 없음',
}
MAIN = list(LABELS)[:4]
STATUSES = {'complete_supported': '기록상 관련 명세 해소를 확인',
            'partial': '관련 누락이나 충돌이 남음',
            'answer_oracle_conflict': '공개 계약과 채점 사이 충돌',
            'unknown': '명세 전체의 해소 여부 미확인',
            'invalid_answer': '답변이 비었거나 절단됨'}


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def jsonl(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


def link(source, label='원본 결과'):
    return f'[{label}]({source["path"]}:{source["line"]})'


def esc(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def main():
    cases = read(OUT / 'cases.jsonl')
    inventory = json.loads((OUT / 'inventory.json').read_text())
    metadata = json.loads((OUT / 'public-metadata.json').read_text())
    annotations = []
    for group in inventory['groups']:
        path = OUT / f'output-{group}.jsonl'
        rows = read(path)
        expected = [c['case_id'] for c in cases if c['group'] == group]
        assert [r['case_id'] for r in rows] == expected, f'Incomplete annotations: {group}'
        annotations.extend(rows)
    assert len({r['case_id'] for r in annotations}) == len(cases)
    lookup = {r['case_id']: r for r in annotations}
    required = {'case_id', 'category', 'clarification_status', 'confidence', 'reason', 'evidence', 'secondary_findings', 'limits'}
    source_lines = {}
    for case in cases:
        a = lookup[case['case_id']]
        assert required <= set(a)
        assert a['category'] in LABELS and a['category'] != 'invalid_answer'
        assert a['clarification_status'] in STATUSES
        assert a['confidence'] in {'high', 'medium', 'low'}
        assert 2 <= len(a['evidence']) <= 4
        for source in case['all_sources']:
            path = source['path']
            if path not in source_lines:
                source_lines[path] = Path(path).read_text().splitlines()
            row = json.loads(source_lines[path][source['line'] - 1])
            digest = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            assert digest == case['record_sha256'], f'Source record changed: {case["case_id"]}'

    merged = []
    for case in cases:
        a = lookup[case['case_id']]
        bucket = 'invalid_answer' if a['clarification_status'] == 'invalid_answer' else a['category']
        merged.append({**case, 'public_metadata': metadata[case['case_id']],
                       'classification': {**a, 'report_bucket': bucket}})
    answered = [r for r in merged if r['classification']['clarification_status'] != 'invalid_answer']
    four = [r for r in answered if r['classification']['category'] in MAIN]
    confirmed = [r for r in answered if r['classification']['clarification_status'] == 'complete_supported']
    assert all(r['classification']['category'] in MAIN for r in confirmed)
    partition = Counter(r['classification']['report_bucket'] for r in merged)
    four_counts = Counter(r['classification']['category'] for r in four)
    confirmed_counts = Counter(r['classification']['category'] for r in confirmed)

    # Inventory denominators are exact saved records, not independent reruns.
    all_records = {}
    changed_files = []
    for item in inventory['files']:
        path = Path(item['path'])
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            changed_files.append(str(path))
        for line in data.decode().splitlines():
            if line.strip():
                row = json.loads(line)
                digest = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                all_records[digest] = row
    algorithms = {}
    for algorithm in sorted({r['algorithm'] for r in merged}):
        subset = [r for r in merged if r['algorithm'] == algorithm]
        algorithms[algorithm] = dict(Counter(r['classification']['report_bucket'] for r in subset))
    summary = {
        'analysis_date': '2026-10-30',
        'scope': inventory['scope'], 'selection': inventory['selection'],
        'deduplication': inventory['deduplication'],
        'source_result_files': len(inventory['files']),
        'unique_evaluated_records_current_files': len(all_records),
        'selected_source_rows': inventory['selected_source_rows'],
        'unique_selected_records': len(merged),
        'unique_tasks_selected': len({r['task_id'] for r in merged}),
        'nonempty_meaningful_answer_records': len(answered),
        'invalid_answer_records': len(merged) - len(answered),
        'four_category_records': len(four), 'four_category_counts': dict(four_counts),
        'clarification_complete_supported_records': len(confirmed),
        'clarification_complete_supported_counts': dict(confirmed_counts),
        'report_partition': dict(partition),
        'clarification_status_counts': dict(Counter(r['classification']['clarification_status'] for r in merged)),
        'confidence_counts': dict(Counter(r['classification']['confidence'] for r in merged)),
        'by_algorithm': algorithms,
        'changed_source_files_since_snapshot': changed_files,
        'verification': {'all_assigned_cases_reviewed': True, 'all_source_records_match_sha256': True,
                         'all_sources_retained': True, 'generated_code_reexecuted': False,
                         'reference_solutions_or_hidden_requirements_used': False},
    }
    jsonl(OUT / 'classified.jsonl', merged)
    jsonl(OUT / 'four-categories.jsonl', four)
    jsonl(OUT / 'clarified-confirmed-failures.jsonl', confirmed)
    write_json(OUT / 'summary.json', summary)

    lines = [
        '# Clarification 후 코드 실패 분류', '',
        f'로컬 실행 결과 {len(inventory["files"])}개 파일에서 질문 품질 3점과 최종 채점 실패가 함께 기록된 사례를 검토했다. '
        f'배치와 합본의 동일 레코드를 합치면 {len(merged)}건이며, 서로 다른 문제 {summary["unique_tasks_selected"]}개를 포함한다. '
        '같은 문제의 다른 실행은 별도 레코드다.', '',
        f'답변이 비었거나 실질적인 정보를 담지 못한 {len(merged)-len(answered)}건을 제외하면, '
        f'네 범주의 코드 결함을 설명할 수 있는 사례는 {len(four)}건이다. '
        f'그중 기록상 관련 명세의 해소까지 확인된 사례는 {len(confirmed)}건이다. '
        '나머지 코드 결함 사례에도 해소하지 않은 요구사항이 함께 남아 있을 수 있다.', '',
        '## 요청한 네 범주의 집계', '',
        '| 실패 범주 | 관련 명세 해소까지 확인 | 유효 답변 후 코드 결함 확인 |',
        '|---|---:|---:|',
    ]
    for category in MAIN:
        lines.append(f'| {LABELS[category]} | {confirmed_counts[category]} | {four_counts[category]} |')
    lines += [f'| 합계 | {len(confirmed)} | {len(four)} |', '',
              '왼쪽 열은 오른쪽 열의 부분집합이다. 명세 해소 확인은 해당 실패를 설명하는 데 필요한 공개 지시와 답변이 일관되고 충분한지를 기준으로 한다. '
              '어떤 자연어 명세의 완전성을 형식적으로 증명했다는 뜻은 아니다.', '',
              '## 네 범주에 넣지 않은 사례', '',
              '| 구분 | 건수 |', '|---|---:|']
    outside = [
        ('관련 명세가 아직 미해결', partition['unresolved_specification']),
        ('사용자 답변과 채점 기대값 불일치', partition['answer_oracle_mismatch']),
        ('명확한 공개 지시와 채점 기대값 불일치', partition['instruction_oracle_mismatch']),
        ('평가 호출 또는 환경 불일치', partition['evaluation_failure']),
        ('실패 원인을 판별할 증거 부족', partition['insufficient_evidence']),
        ('3점 판정이지만 유효한 답변 없음', partition['invalid_answer']),
    ]
    for label, count in outside:
        lines.append(f'| {label} | {count} |')
    lines += ['',
              '답변이나 지시와 채점의 불일치는 기록에 보이는 특정 입력과 기대값에 한정한다. '
              '사용자의 기만이나 숨은 의도를 가정하지 않는다. 공개 entry_point와 생성 함수명이 일치하는데 평가자가 다른 이름을 호출한 경우도 코드의 이름 오류로 세지 않았다.', '',
              '## 관련 명세 해소까지 확인한 사례', '',
              '| 사례 | 문제 | 알고리즘 | 분류 | 관찰된 원인 | 출처 |',
              '|---|---|---|---|---|---|']
    for r in confirmed:
        a = r['classification']
        lines.append(f'| {r["case_id"]} | {r["task_id"]} | {r["algorithm"]} | {LABELS[a["category"]]} | {esc(a["reason"])} | {link(r["source"])} |')
    lines += ['', '## 알고리즘별 집계', '',
              '| 알고리즘 | 후보 | 답변 미반영 | 설계 | 구현 | 실행 조건 | 명세 미해결 | 답변 또는 지시와 채점 불일치 | 평가 불일치 | 증거 부족 | 답변 무효 |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for algorithm, counts in algorithms.items():
        counts = Counter(counts)
        values = [sum(counts.values()), *[counts[k] for k in MAIN], counts['unresolved_specification'],
                  counts['answer_oracle_mismatch'] + counts['instruction_oracle_mismatch'],
                  counts['evaluation_failure'], counts['insufficient_evidence'], counts['invalid_answer']]
        lines.append('| ' + algorithm + ' | ' + ' | '.join(str(v) for v in values) + ' |')
    lines += ['', '## 판정 기준', '',
              '질문 점수 3점은 필요한 사실 하나를 잘 물었다는 기록이며, 필요한 명확화를 모두 끝냈다는 증명이 아니다. '
              '명확화 상태와 코드의 실패 원인을 별도 축으로 기록했다.', '',
              '실패 원인은 기록된 첫 assertion 또는 예외를 설명하는 원인을 우선했다. '
              '질문 답변이 실패 행동을 직접 규정했는데 코드가 이를 어기면 답변 미반영으로, '
              '그 외에는 틀린 전체 풀이 전략과 국소적인 코드 결함을 구분했다. '
              '정확한 정수를 실수 Binet 근사만으로 계산하는 전략은 설계 오류로 통일했다. '
              '같은 코드 형태도 해당 실행에서 어떤 사실을 질문했는지에 따라 분류가 달라질 수 있다.', '',
              '코드와 실패 로그만으로 설계와 구현의 경계를 단정할 수 없거나 실제 실패 입력이 생략된 사례는 신뢰도와 한계에 표시했다. '
              '원래 코드나 테스트를 수정하거나 다시 실행하지 않았고, 참조 구현이나 별도의 숨은 요구사항을 판정에 공급하지 않았다.', '',
              '범위는 .local에 저장된 평가 완료 로컬 실행이다. 저장소에 동봉된 docs/data/raw의 리더보드 결과와 채점되지 않은 output 파일은 포함하지 않았다. '
              '원본 결과는 보존하고 모든 중복 출처 위치와 원본 레코드 해시를 남겼다.', '',
              '## 결과 파일', '',
              f'- [전체 분류 JSONL]({OUT / "classified.jsonl"})',
              f'- [네 범주의 코드 결함 JSONL]({OUT / "four-categories.jsonl"})',
              f'- [명세 해소까지 확인한 실패 JSONL]({OUT / "clarified-confirmed-failures.jsonl"})',
              f'- [집계 JSON]({OUT / "summary.json"})',
              f'- [원본 파일 목록과 해시]({OUT / "inventory.json"})', '',
              '## 사례별 판정', '',
              '각 사례는 주분류 하나와 별도 명확화 상태를 갖는다. 추가 결함은 주된 실패 원인에 합산하지 않고 별도 관찰로 남겼다.', '']
    for category in list(LABELS):
        subset = [r for r in merged if r['classification']['report_bucket'] == category]
        if not subset:
            continue
        lines += [f'### {LABELS[category]}', '']
        for r in subset:
            a = r['classification']
            lines += [f'#### {r["case_id"]} {r["task_id"].replace("/", " ")} {r["algorithm"]}', '',
                      f'{link(r["source"])} · 명확화 상태: {STATUSES[a["clarification_status"]]} · 판정 신뢰도: {a["confidence"]}', '',
                      a['reason'], '', '근거:', '']
            lines += ['- ' + str(item).replace('\n', ' ') for item in a['evidence']]
            if a['secondary_findings']:
                lines += ['', '추가 관찰:', ''] + ['- ' + item for item in a['secondary_findings']]
            if a['limits']:
                lines += ['', '판정 한계: ' + a['limits']]
            if a['clarification_status'] == 'invalid_answer':
                lines += ['', '유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 ' + LABELS[a['category']] + '이다.']
            lines += ['']
    report = '\n'.join(lines)
    (OUT / 'REPORT.md').write_text(report)
    assert sum(partition.values()) == len(merged)
    assert sum(four_counts.values()) == len(four)
    assert sum(confirmed_counts.values()) == len(confirmed)
    assert len(read(OUT / 'classified.jsonl')) == len(cases)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

"""Replay all registered frozen train100 responses, without any LLM calls."""

from __future__ import annotations

import concurrent.futures
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from clarify.runtime import init_evalplus_evaluator
from experiment_tools import compare_train100 as compare

BENCHMARK = ROOT / '.local/train100-v1'
OUTPUT = Path(__file__).resolve().parent
WORKERS = 4


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, path)


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def without_grade(row):
    return {k: v for k, v in row.items() if k not in {'success', 'test_result'}}


def main():
    # The complete before-state remains available even after updating the main comparison.
    before = OUTPUT / 'before'
    before.mkdir(exist_ok=True)
    registry_path = BENCHMARK / 'comparison-registry.json'
    for name in ('comparison-registry.json', 'COMPARISON.md', 'comparison.json', 'pairwise.json'):
        target = before / name
        if not target.exists():
            shutil.copyfile(BENCHMARK / name, target)
    registry = json.loads((before / 'comparison-registry.json').read_text())
    _, expected = compare._expected(BENCHMARK)
    runtime_path = ROOT / 'clarify/runtime.py'
    metadata = {
        'manifest_sha256': digest(BENCHMARK / 'manifest.json'),
        'source_registry_sha256': digest(before / 'comparison-registry.json'),
        'runtime_sha256': digest(runtime_path),
        'workers': WORKERS,
        'llm_calls': 0,
        'docker_image_id': subprocess.check_output(
            ['docker', 'image', 'inspect', 'ganler/evalplus', '--format', '{{.Id}}'], text=True
        ).strip(),
        'sources': [{'label': entry['label'], 'path': entry['results_path'],
                     'sha256': entry['results_sha256']} for entry in registry['entries']],
    }
    meta_path = OUTPUT / 'regrade.json'
    if meta_path.exists():
        if json.loads(meta_path.read_text()) != metadata:
            raise ValueError('Regrade inputs or evaluator changed; choose a fresh directory.')
    else:
        write_json(meta_path, metadata)
        shutil.copyfile(runtime_path, OUTPUT / 'runtime.py.snapshot')

    originals = {}
    completed = {}
    partial_paths = {}
    for entry in registry['entries']:
        path = Path(entry['results_path'])
        if digest(path) != entry['results_sha256']:
            raise ValueError(f'Source results changed: {path}')
        source, _, _ = compare._validate(path, expected)
        label = entry['label']
        originals[label] = source
        folder = OUTPUT / label
        folder.mkdir(exist_ok=True)
        partial_paths[label] = folder / 'partial.jsonl'
        saved = rows(partial_paths[label]) if partial_paths[label].exists() else []
        by_task = {row['task_id']: row for row in source}
        completed[label] = {}
        for row in saved:
            task_id = row['task_id']
            if (task_id in completed[label]
                    or without_grade(row) != without_grade(by_task[task_id])
                    or not isinstance(row.get('success'), bool)):
                raise ValueError(f'Invalid resumed result: {label}/{task_id}')
            completed[label][task_id] = row

    print(f'Initialize evaluator; {len(originals)} runs / {len(originals) * 100} responses.', flush=True)
    evaluator = init_evalplus_evaluator(expected)
    assert all(evaluator.partial(row).entry_point == row['entry_point'] for row in expected)

    def evaluate(label, original):
        response = original['prompt_result']
        if '```python' not in response:
            response = f'```python\n{response.strip()}\n```'
        success, status = evaluator.evaluate(original, response)
        return label, dict(original, success=success, test_result=status)

    def progress():
        done = sum(len(values) for values in completed.values())
        state = {'completed': done, 'total': len(originals) * 100,
                 'updated_at_utc': datetime.now(timezone.utc).isoformat(),
                 'runs': {label: {'completed': len(values),
                                  'passed': sum(row['success'] for row in values.values())}
                          for label, values in completed.items()}}
        write_json(OUTPUT / 'progress.json', state)
        return done

    progress()
    jobs = [(label, row) for label, source in originals.items() for row in source
            if row['task_id'] not in completed[label]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(evaluate, label, row) for label, row in jobs]
        for future in concurrent.futures.as_completed(futures):
            label, result = future.result()
            with partial_paths[label].open('a') as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + '\n')
                handle.flush()
            completed[label][result['task_id']] = result
            done = progress()
            if done % 25 == 0 or len(completed[label]) == 100:
                print(f'PROGRESS {done}/{len(originals) * 100}: {label} '
                      f'{len(completed[label])}/100', flush=True)

    if digest(runtime_path) != metadata['runtime_sha256']:
        raise ValueError('Runtime changed during regrading; comparison not published.')
    new_registry = json.loads(json.dumps(registry))
    summaries = []
    for entry in new_registry['entries']:
        label = entry['label']
        source = originals[label]
        result = [completed[label][row['task_id']] for row in source]
        path = OUTPUT / label / 'results.jsonl'
        path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in result))
        compare._validate(path, expected)
        changed = [{'task_id': old['task_id'], 'before': old['success'], 'after': new['success'],
                    'before_test_result': old['test_result'], 'after_test_result': new['test_result']}
                   for old, new in zip(source, result) if old['success'] != new['success']]
        summaries.append({'label': label, 'algorithm': entry['algorithm'],
                          'before': compare._metric(source), 'after': compare._metric(result),
                          'changes': changed})
        old_path, old_hash = entry['results_path'], entry['results_sha256']
        entry.update(results_path=str(path), results_sha256=digest(path))
        entry['evaluation'] = {'runtime_sha256': metadata['runtime_sha256'],
                               'source_results_path': old_path, 'source_results_sha256': old_hash,
                               'regrade_metadata': str(meta_path)}

    new_registry['evaluation'] = {'runtime_sha256': metadata['runtime_sha256'], 'llm_calls': 0,
                                  'regrade_metadata': str(meta_path)}
    write_json(OUTPUT / 'summary.json', summaries)
    write_json(OUTPUT / 'comparison-registry.json', new_registry)
    shutil.copyfile(BENCHMARK / 'manifest.json', OUTPUT / 'manifest.json')
    compare.render(OUTPUT, new_registry, expected)
    ordered = sorted(summaries, key=lambda item: compare.EXPECTED.index(item['algorithm']))
    lines = ['# Entry point 수정 후 train100 재채점', '',
             '- 등록된 9회 실행의 900개 응답을 수정된 채점기로 모두 다시 실행했다.',
             '- 생성 코드·질문·답변·기존 모델 비용은 보존했다. 추가 모델 호출은 0회다.',
             f'- 평가 코드 SHA256: `{metadata["runtime_sha256"]}`', '',
             '| 알고리즘 | 이전 통과 | 재채점 통과 | 변화 | 이전 TDS | 재채점 TDS |',
             '|---|---:|---:|---:|---:|---:|']
    for item in ordered:
        a, b = item['before'], item['after']
        lines.append(f'| {compare.DISPLAY[item["algorithm"]]} | {a["pass"]}/100 | {b["pass"]}/100 | '
                     f'{b["pass"] - a["pass"]:+d} | {a["tds"]:.4f} | {b["tds"]:.4f} |')
    lines += ['', '## 통과 여부가 바뀐 문제', '', '| 실행 | 문제 | 이전 | 재채점 |', '|---|---|---|---|']
    for item in ordered:
        for change in item['changes']:
            lines.append(f'| {item["label"]} | {change["task_id"]} | '
                         f'{"통과" if change["before"] else "실패"} | '
                         f'{"통과" if change["after"] else "실패"} |')
    lines += ['', '## 이름 오류 수정 후에도 실패한 사례', '']
    for item in ordered:
        label = item['label']
        for task_id in ('Mbpp/770', 'Mbpp/763', 'Mbpp/166'):
            row = completed[label][task_id]
            if not row['success']:
                lines.append(f'- {label} / {task_id}: `{row["test_result"].splitlines()[-2]}`')
    lines += ['', f'- [재채점 실행 간 비교]({OUTPUT / "COMPARISON.md"})',
              f'- [수정 전 비교표]({before / "COMPARISON.md"})',
              f'- [전체 변경 기록]({OUTPUT / "summary.json"})']
    (OUTPUT / 'REGRADE_COMPARISON.md').write_text('\n'.join(lines) + '\n')
    with (BENCHMARK / 'comparison.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if digest(registry_path) != metadata['source_registry_sha256']:
            raise ValueError('Registry changed during regrading; separate reports are complete, main not replaced.')
        write_json(registry_path, new_registry)
        compare.render(BENCHMARK, new_registry, expected)
    shutil.copyfile(OUTPUT / 'REGRADE_COMPARISON.md', BENCHMARK / 'REGRADE_COMPARISON.md')
    print('COMPLETE:', OUTPUT / 'REGRADE_COMPARISON.md', flush=True)
    for item in ordered:
        print(item['algorithm'], item['before']['pass'], '->', item['after']['pass'],
              'TDS', round(item['after']['tds'], 4), flush=True)


if __name__ == '__main__':
    main()

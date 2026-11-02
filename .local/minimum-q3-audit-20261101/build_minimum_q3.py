"""Validate and assemble the high-end-judgment minimum-Q3 reference artifact.

No model API, simulator, code generation, or evaluation is called here.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERSION = "train100-minimum-q3-v1"
CRITERIA = {"criticality", "search_space", "leakage", "atomicity", "objectivity"}
STATUS = {
    "finite": "최소값 추정 가능",
    "unrecoverable_from_hidden": "현재 참조로 필요한 답을 식별할 수 없음",
    "oracle_mismatch": "의도와 채점 동작의 불일치",
    "uncertain": "판정 보류",
}


def read(path):
    return [json.loads(s) for s in Path(path).read_text(encoding="utf-8").splitlines() if s.strip()]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    inputs = {r["task_id"]: r for r in read(HERE / "inputs100.jsonl")}
    annotation_paths = sorted(HERE.glob("minq3-*.jsonl"))
    assert len(annotation_paths) == 4, "All four 25-row strata must finish before assembly"
    annotations = [r for p in annotation_paths for r in read(p)]
    assert len(annotations) == len(inputs) == 100
    assert len({r["task_id"] for r in annotations}) == 100
    assert {r["task_id"] for r in annotations} == set(inputs)
    manifest = json.loads((HERE / "manifest.json").read_text())
    adjudications = json.loads((HERE / "adjudications.json").read_text())
    for relpath, expected in manifest["source_files"].items():
        assert digest(ROOT / relpath) == expected, f"Input changed: {relpath}"
    rows = []
    for a in sorted(annotations, key=lambda r: r["index"]):
        a.update(adjudications.get("overrides", {}).get(a["task_id"], {}))
        src = inputs[a["task_id"]]
        assert src["index"] == a["index"]
        assert src["prompt_sha256"] == hashlib.sha256(src["prompt"].encode()).hexdigest()
        n = a["minimum_q3_estimate"]
        assert n is None or (type(n) is int and n >= 0)
        assert a["resolution_status"] in STATUS
        assert a["confidence"] in {"high", "medium", "low"}
        assert a["minimality_argument_ko"] and a["change_explanation"]
        assert isinstance(a["inferred_without_question"], list)
        if n is not None:
            assert a["resolution_status"] == "finite"
            assert len(a["optimal_questions"]) == n
            assert not a["after_answers_remaining_gaps"]
            assert [q["order"] for q in a["optimal_questions"]] == list(range(1, n + 1))
            fact_ids = [q["fact_id"] for q in a["optimal_questions"]]
            assert len(set(fact_ids)) == n
            for q in a["optimal_questions"]:
                assert q["question_en"] and q["question_ko"] and q["expected_answer_ko"]
                assert q["hidden_support"] in {"explicit", "implicit"}
                assert q["hidden_evidence_ko"]
                assert set(q["quality_checks"]) == CRITERIA
                assert all(c["pass"] is True and c["reason_ko"] for c in q["quality_checks"].values())
        else:
            assert a["resolution_status"] != "finite"
            assert not a["optimal_questions"], "Do not present an unsupported route as an optimal Q3 sequence"
            assert a["after_answers_remaining_gaps"]
        row = {"schema_version": VERSION,
               "count_kind": "best_high_end_judgment_point_estimate_not_proved_or_scored",
               **{k: src[k] for k in ("index", "task_id", "dataset", "source", "source_file", "entry_point", "prompt_sha256", "reference_sha256")},
               **a, "status_label_ko": STATUS[a["resolution_status"]],
               "prompt": src["prompt"],
               "source_evidence_ref": {"path": str(HERE / "inputs100.jsonl"), "line": src["index"]},
               "actual_quality_scores_observed": False,
               "code_generation_pass_rate_measured": False}
        row["join_key"] = f"{row['task_id']}::{row['prompt_sha256']}"
        row["required_fact_ids"] = [q["fact_id"] for q in row["optimal_questions"]]
        row["unrestricted_target_information_estimate"] = row["ideal_requirement_minimum"]
        rows.append(row)
    assert [r["index"] for r in rows] == list(range(1, 101))
    output = HERE / "minimum_q3_100.jsonl"
    output.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    distribution = collections.Counter("unknown" if r["minimum_q3_estimate"] is None else str(r["minimum_q3_estimate"]) for r in rows)
    finite = [r for r in rows if r["minimum_q3_estimate"] is not None]
    q_total = sum(r["minimum_q3_estimate"] for r in finite)
    by_stratum = {}
    for r in rows:
        key = f"{r['dataset']}/{r['source']}"
        by_stratum.setdefault(key, collections.Counter())["unknown" if r["minimum_q3_estimate"] is None else str(r["minimum_q3_estimate"])] += 1
    changes = [{"task_id": r["task_id"], "prior_lower_bound": r["prior_count"], "minimum_q3_estimate": r["minimum_q3_estimate"], "reason_ko": r["change_explanation"]}
               for r in rows if r["prior_count"] != r["minimum_q3_estimate"]]
    summary = {
        "version": VERSION, "assessment_date": "2026-11-01", "total_rows": 100,
        "distribution": dict(distribution), "finite_rows": len(finite), "unknown_rows": 100 - len(finite),
        "finite_required_q3_question_sum": q_total,
        "finite_mean": q_total / len(finite) if finite else None,
        "by_stratum": {k: dict(v) for k, v in by_stratum.items()},
        "resolution_statuses": dict(collections.Counter(r["resolution_status"] for r in rows)),
        "confidence": dict(collections.Counter(r["confidence"] for r in rows)),
        "question_hidden_support": dict(collections.Counter(q["hidden_support"] for r in finite for q in r["optimal_questions"])),
        "changed_count": len(changes), "changed_rows": changes,
        "budget_coverage": {str(b): {"rows_with_finite_estimate_at_most_budget": sum(r["minimum_q3_estimate"] <= b for r in finite),
                                     "finite_denominator": len(finite), "all_rows_denominator": 100,
                                     "meaning": "coverage of the judgment reference, not a pass-rate upper bound"} for b in range(4)},
        "unknown_task_ids": [r["task_id"] for r in rows if r["minimum_q3_estimate"] is None],
        "nonzero_task_ids": [r["task_id"] for r in rows if r["minimum_q3_estimate"]],
        "artifact_sha256": digest(output), "manifest_sha256": digest(HERE / "manifest.json"),
        "annotation_sha256": {p.name: digest(p) for p in annotation_paths},
        "adjudications_sha256": digest(HERE / "adjudications.json"),
        "definition_ko": "공개 문제와 예시·수학·Python 관례 및 답변 후의 추론을 최대한 사용하고도 남는, 정확히 한 사실을 묻는 Q3 적격 질문 수의 고성능 모델 판단값.",
        "null_definition_ko": "현재 참조·평가 근거로 합법적인 Q3 경로의 유한 최소값을 확정하지 못함. 0이나 수학적 무한대가 아님.",
        "ideal_requirement_minimum_definition_ko": "Q3 적격성이나 현재 참조의 답변 가능성을 요구하지 않은 목표 동작의 독립 정보 수 추정. 정상 수학 명세의 질문 수가 아니며 Q3 총합에 포함하지 않음.",
        "limitations_ko": [
            "실제 simulator의 QUALITY를 측정한 값이 아니라 다섯 기준에 대한 모델 판단이다.",
            "최소값은 강한 추론 정책과 명시한 관례에 조건부이며 수학적 최소값 증명이 아니다.",
            "0은 정보 확인이 필요 없다는 판단이고 모델이 반드시 올바른 코드를 생성한다는 뜻은 아니다.",
            "null 사례를 제외한 질문 수 합계에 임의의 대체값을 더하지 않는다.",
            "이전 감사의 질문 후보 수/하한과 목적이 달라졌다. 차이는 행별 설명에 기록했다.",
        ],
    }
    write_json(HERE / "summary.json", summary)
    lookup = {r["join_key"]: {k: r[k] for k in ("task_id", "prompt_sha256", "minimum_q3_estimate", "resolution_status", "confidence", "required_fact_ids", "index")}
              for r in rows}
    write_json(HERE / "minimum_q3_lookup.json", {"version": VERSION, "rows": lookup})
    write_json(HERE / "changes.json", changes)
    lines = ["ECC 100제 최소 Q3 질문 수 판단 기준", "",
             f"0개: {distribution['0']}문제", f"1개: {distribution['1']}문제", f"2개: {distribution['2']}문제",
             f"3개 이상: {sum(int(n) >= 3 and c or 0 for n, c in distribution.items() if n != 'unknown')}문제",
             f"현재 근거로 유한 최소값 미확정: {distribution['unknown']}문제", "",
             f"유한값을 판단한 {len(finite)}문제의 필요한 질문 합계: {q_total}개.",
             f"이전 정적 감사의 하한에서 숫자 또는 미확정 상태가 달라진 문제: {len(changes)}개.", "",
             summary["definition_ko"], summary["null_definition_ko"], *summary["limitations_ko"], "",
             "문제별 최소값 요약", "번호 | 문제 | 최소 Q3 | 확신 | 현재 상태"]
    for r in rows:
        n = "미확정" if r["minimum_q3_estimate"] is None else str(r["minimum_q3_estimate"])
        lines.append(f"{r['index']:03d} | {r['task_id']} | {n} | {r['confidence']} | {r['status_label_ko']}")
    lines += ["", "문제별 필요한 정보와 최소 질문 순서", ""]
    for r in rows:
        n = "미확정(null)" if r["minimum_q3_estimate"] is None else str(r["minimum_q3_estimate"])
        lines += [f"{r['index']:03d}. {r['task_id']} | 최소 Q3 {n} | {r['dataset']}/{r['source']} | 확신 {r['confidence']}",
                  "최소 판단: " + r["minimality_argument_ko"],
                  "이전 판정과 차이: " + r["change_explanation"]]
        if r["optimal_questions"]:
            for q in r["optimal_questions"]:
                lines += [f"Q{q['order']} [{q['fact_id']}]: {q['question_ko']}",
                          "English: " + q["question_en"], "예상 답: " + q["expected_answer_ko"],
                          f"참조 근거({q['hidden_support']}): {q['hidden_evidence_ko']}"]
                for criterion, assessment in q["quality_checks"].items():
                    lines.append(f"  {criterion}: 적격 판단 — {assessment['reason_ko']}")
        elif r["minimum_q3_estimate"] == 0:
            lines.append("질문: 없음. 필요한 내용은 아래 추론으로 결정된다.")
        else:
            lines.append("실행 가능한 Q3 질문 순서를 확정하지 않았다. 아래의 부족한 정보는 0개로 처리하지 않는다.")
        if r["required_facts"]:
            lines.append("확인이 필요한 목표 정보:")
            for fact in r["required_facts"]:
                lines.append("  - " + str(fact.get("fact_ko", fact)))
        if r["inferred_without_question"]:
            lines.append("질문 없이 추론할 정보:")
            for inference in r["inferred_without_question"]:
                lines.append("  - " + (inference if isinstance(inference, str) else json.dumps(inference, ensure_ascii=False)))
        if r["after_answers_remaining_gaps"]:
            lines.append("남는 정보 또는 근거 부족:")
            lines.extend("  - " + str(gap) for gap in r["after_answers_remaining_gaps"])
        if r.get("root_adjudication_ko"):
            lines.append("최종 조정: " + r["root_adjudication_ko"])
        if r.get("interpretive_alternative_minimums"):
            lines.append("추론 정책에 따른 대안: " + json.dumps(r["interpretive_alternative_minimums"], ensure_ascii=False))
        for proposed in r.get("target_questions", []):
            lines.append("목표 정보 질문(현재 Q3 경로에서 제외): " + proposed.get("question_ko", str(proposed)))
        lines += ["", "=" * 72, ""]
    (HERE / "REPORT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "MINIMUM_COUNTS.txt").write_text("\n".join(lines[:lines.index("문제별 필요한 정보와 최소 질문 순서")]) + "\n", encoding="utf-8")
    usage = ["ECC 최소 Q3 판단 자료 사용법", "",
             "minimum_q3_100.jsonl: 100행의 전체 판단, 질문 순서, 예상 답, Q3 다섯 기준, 추론·최소 근거.",
             "minimum_q3_lookup.json: 기존 결과와 합칠 수 있는 간략 조회 자료.",
             "MINIMUM_COUNTS.txt: 100개 최소값 표.", "REPORT.txt: 최소값 표와 모든 근거·질문.",
             "changes.json: 이전 하한과 바뀐 문제 및 이유.", "summary.json: 분포, 합계, 확신, 예산별 포함 개수.", "",
             "기존 result JSONL의 task_id와 prompt의 SHA256을 모두 맞춰 join_key로 연결한다.",
             "task_id만 같고 문제 변형이 다른 실행에는 같은 값을 적용하지 않는다.", "",
             "join_key = result['task_id'] + '::' + hashlib.sha256(result['prompt'].encode('utf-8')).hexdigest()", "",
             "질문 수만 비교해서 어떤 정보를 얻었는지 판정할 수는 없다. required_fact_ids와 실제 질문·답을 의미적으로 비교한다.",
             "실제 Q3 개수가 기준보다 적어도 추론/우연으로 통과할 수 있고, 많아도 필요한 사실을 놓칠 수 있다.",
             "0인데 실패한 사례는 정보 누락 이외의 구현·추론 실패를 조사할 후보가 된다.",
             "null은 별도 정보 근거/평가 정합성 문제로 분류하고 under-asking에 자동 포함하지 않는다.",
             "실제 simulator의 QUALITY=3 기록은 이 기준의 예상 답 정확성이나 충분성을 증명하지 않는다.", ""]
    (HERE / "HOW_TO_USE.txt").write_text("\n".join(usage), encoding="utf-8")
    print(json.dumps({"distribution": dict(distribution), "finite_rows": len(finite), "questions": q_total, "changed_rows": len(changes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

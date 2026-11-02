"""Assemble reviewed annotations without querying a model or changing a benchmark."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LABELS = {
    "no_question_needed": "질문 불필요",
    "one_atomic_question": "정확한 답 하나면 정보상 충분",
    "multiple_independent_requirements": "한 답 뒤에도 독립 조건이 남음",
    "spec_test_mismatch": "원래 의도와 채점 동작의 불일치",
    "uncertain": "판정 보류",
}


def read(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    manifest_path = ROOT / ".local/train100-v1/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    inputs = {r["task_id"]: r for p in HERE.glob("input-*.jsonl") for r in read(p)}
    annotations = [r for p in sorted(HERE.glob("annotations-*.jsonl")) for r in read(p)]
    assert len(inputs) == len(annotations) == 100
    assert len({r["task_id"] for r in annotations}) == 100
    assert set(inputs) == {r["task_id"] for r in annotations}
    ordered = []
    for a in sorted(annotations, key=lambda r: r["index"]):
        original = inputs[a["task_id"]]
        assert a["status"] in LABELS
        if a["status"] == "no_question_needed":
            assert not a.get("question_en") and not a.get("question_ko")
            assert a["minimum_questions_lower_bound"] == 0
        if a["status"] == "one_atomic_question":
            assert a.get("question_en") and a.get("question_ko")
            assert not a.get("remaining_after_answer_ko")
            assert a["minimum_questions_lower_bound"] == 1
        if a["status"] == "multiple_independent_requirements":
            assert a["minimum_questions_lower_bound"] >= 2
            assert a.get("remaining_after_answer_ko")
        row = {**original, **a, "status_label_ko": LABELS[a["status"]],
               "assessment_kind": "offline_static_semantic_review",
               "single_question_pass_experiment_performed": False,
               "expected_answer_kind": "offline_test_target_not_actual_simulator_reply"}
        row["all_atomic_questions"] = [
            {k: gap.get(k) for k in ("id", "question_en", "question_ko", "expected_answer_ko")}
            for gap in a.get("independent_requirements", []) if gap.get("question_en")
        ]
        ordered.append(row)
    (HERE / "audit100.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered), encoding="utf-8")
    counts = collections.Counter(r["status"] for r in ordered)
    by_stratum = {}
    for r in ordered:
        key = f"{r['dataset']}/{r['source']}"
        by_stratum.setdefault(key, collections.Counter())[r["status"]] += 1
    summary = {
        "scope": "frozen train100-v1; 100 distinct train task IDs",
        "manifest_sha256": sha(manifest_path), "counts": dict(counts),
        "by_stratum": {k: dict(v) for k, v in by_stratum.items()},
        "atomic_questions_extracted": sum(len(r["all_atomic_questions"]) for r in ordered),
        "information_sufficient_with_at_most_one_correct_atomic_answer": counts["no_question_needed"] + counts["one_atomic_question"],
        "definitions": {
            "one_atomic_question": "A precise answer reveals one independent behavioral fact. Blanket full-spec recovery is excluded.",
            "sufficient": "Conditional on a correct answer and a correct implementation; observed test-relevant ambiguity is resolved in static review.",
            "multiple_independent_requirements": "One answer does not determine all observed independent requirements; guessing can still pass.",
            "minimum_questions_lower_bound": "Conservative static fact-count estimate under the annotation interpretation, not an information-theoretic theorem.",
            "spec_test_mismatch": "Original intended behavior/reference and active evaluation disagree; generic injected contradiction alone is not this status.",
            "no_question_needed": "No critical non-inferable ambiguity found for current evaluator behavior; not a universal claim over untested inputs.",
        },
        "limitations_ko": [
            "이 목록은 테스트와 참조를 본 사후 진단이며 참가 알고리즘에 공급할 수 있는 질문 정답지가 아니다.",
            "예상 답은 실제 가상 사용자에게 받은 응답이 아니다. 참조가 모호하거나 가상 사용자가 틀리면 한 질문 충분 판정도 실제 통과를 보장하지 않는다.",
            "추출 질문으로 새 코드 생성·채점 실험은 수행하지 않았다. 기존 알고리즘 성적을 이 질문들의 성공률로 제시하지 않는다.",
            "25개씩 균형을 맞춘 표본으로 전체 train·validation의 비율을 추정하지 않는다.",
        ],
        "provenance": {str(p.relative_to(ROOT)): sha(p) for p in sorted(HERE.glob("annotations-*.jsonl"))},
    }
    inventory_path = HERE / "corpus-inventory.json"
    if inventory_path.exists():
        summary["corpus_inventory_file"] = str(inventory_path)
        summary["corpus_inventory_sha256"] = sha(inventory_path)
    verification_path = HERE / "example-verification.json"
    if verification_path.exists():
        verification = json.loads(verification_path.read_text())
        summary["illustrative_checks"] = {"file": str(verification_path), "cases": len(verification["cases"]),
                                           "all_expected_outcomes": all(c["expected_pass"] == c["actual_pass"] for c in verification["cases"]),
                                           "method": "analyst-authored code in current Docker evaluator; no user or LLM calls"}
    draft_path = HERE / "draft-questions.jsonl"
    if draft_path.exists():
        annotated = {(r["task_id"], r["prompt_sha256"], r["entry_point"]): r for r in ordered}
        drafts = read(draft_path)
        assert len(drafts) == 8731
        index = {r["row_key"]: r for r in read(HERE / "corpus-index.jsonl")}
        assert len(index) == len(drafts) and set(index) == {r["row_key"] for r in drafts}
        full = []
        coverage = collections.Counter()
        for d in drafts:
            source = index[d["row_key"]]
            a = annotated.get((source["task_id"], source["prompt_sha256"], source["entry_point"]))
            row = {k: d[k] for k in ("row_key", "task_id", "split", "source_variant", "source_file", "source_line", "entry_point")}
            row.update(prompt_sha256=source["prompt_sha256"], corpus_index_ref=d["corpus_index_ref"])
            if a:
                status = "reviewed_frozen100" if a["source_file"] == d["source_file"] else "same_prompt_review_inherited"
                row.update(analysis_status=status, sufficiency_status=a["status"],
                           question_en=a.get("question_en"), question_ko=a.get("question_ko"),
                           expected_answer_ko=a.get("expected_answer_ko"), all_atomic_questions=a["all_atomic_questions"],
                           minimum_questions_lower_bound=a["minimum_questions_lower_bound"],
                           remaining_after_answer_ko=a["remaining_after_answer_ko"], confidence=a["confidence"],
                           reviewed_annotation_ref={"path": str(HERE / "audit100.jsonl"), "line": a["index"]},
                           human_answer_source_may_differ=(source.get("effective_hidden_requirements") != a.get("reference_prompt")))
            else:
                status = "algorithmic_draft_unreviewed" if d.get("question") else "pending_semantic_review"
                row.update(analysis_status=status, sufficiency_status="not_assessed", question_en=d.get("question"),
                           question_ko=None, expected_answer_evidence=d.get("expected_answer_evidence"),
                           expected_answer_evidence_ref=d.get("expected_answer_evidence_ref"),
                           candidate_questions=d.get("candidate_questions", []),
                           atomicity="atomicity_unverified", pending_reason=d.get("pending_reason"),
                           necessity="not_assessed", test_alignment="not_assessed")
            coverage[status] += 1
            full.append(row)
        assert coverage["reviewed_frozen100"] == 100
        (HERE / "all-questions.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in full), encoding="utf-8")
        full_text = ["전체 train validation 질문 후보와 검토 상태", "",
                     "고정 100제만 개별 검토했다. 나머지 자동 후보는 원자성·필수성·충분성이 미확정이다.",
                     "질문이 없는 미검토 행은 질문 불필요 판정이 아니다.", ""]
        for r in full:
            full_text.append(f"{r['split']} | {r['task_id']} | {r['source_variant']} | {r['analysis_status']}")
            if r["sufficiency_status"] != "not_assessed":
                full_text.append(f"판정: {LABELS[r['sufficiency_status']]}")
                full_text.append("질문: " + (r.get("question_ko") or "필수 질문 없음 또는 명세·채점 불일치로 질문을 확정하지 않음"))
            else:
                full_text.append("미검토 질문 후보: " + (r.get("question_en") or "미확정; 의미 검토 필요"))
            full_text.append(f"출처: {r['source_file']}:{r['source_line']}")
            full_text.append("")
        (HERE / "all-questions.txt").write_text("\n".join(full_text) + "\n", encoding="utf-8")
        summary["full_expansion"] = {"rows": len(full), "coverage": dict(coverage),
                                     "source_splits": dict(collections.Counter(r["split"] for r in full)),
                                     "selected_candidates_before_manual_overrides": sum(bool(r.get("question")) for r in drafts),
                                     "warning_ko": "개별 확정은 고정 100제뿐이며, 나머지는 미검토 후보 또는 의미 검토 대기 상태다.",
                                     "corpus_index_sha256": sha(HERE / "corpus-index.jsonl"), "draft_sha256": sha(draft_path)}
    save(HERE / "summary.json", summary)
    report = ["단일 질문으로 테스트 요구사항을 확정할 수 있는가", "", "고정 train100-v1의 100문제를 개별 검토했다.",
              "하나의 문장이나 한 번의 메시지가 아니라, 답이 정확히 하나의 독립 사실인 질문을 기준으로 삼았다.", ""]
    for status, label in LABELS.items():
        report.append(f"{label}: {counts[status]}개")
    report += ["", "판정 해석", *summary["limitations_ko"],
               "여러 조건이 남는 문제도 남은 선택을 추론하거나 우연히 맞히면 통과할 수 있다. 여기서 불충분은 한 답으로 명세를 확정할 수 없다는 뜻이다.",
               "원자 질문 수 하한은 명세 해석에 따른 보수적인 정적 판단이다. 수학적인 최소 질문 수 증명이나 모델 성공률이 아니다.",
               "조건을 이미 합리적으로 추론할 수 있거나 현재 테스트가 구별하지 않으면 질문 수를 늘리지 않았다.",
               "성능·루프 사용·입력 변이 같은 조건도 평가가 측정하지 않으면 독립적인 필수 질문에서 제외했다.",
               "", "출처", f"고정 표본 manifest: {manifest_path}", f"manifest SHA256: {summary['manifest_sha256']}",
               "평가 기준: clarify/env.py의 CRITICALITY, SEARCH SPACE, LEAKAGE, ATOMICITY, OBJECTIVITY 및 clarify/runtime.py의 실제 oracle.",
               "평가 데이터가 있는 ID는 현재 EvalPlus 입력·canonical·특수 oracle을 우선하고, 없는 MBPP ID는 test_cases를 사용했다.",
               "", "문제별 질문과 예상 답"]
    if summary.get("full_expansion"):
        expansion = summary["full_expansion"]
        insertion = ["", "전체 데이터로의 확장", "train 7,961행 + validation 770행 = 8,731행을 누락 없이 색인했다.",
                     expansion["warning_ko"], f"단계별 행 수: {dict(expansion['coverage'])}",
                     "전체 행별 결과: all-questions.jsonl. 원본·실효 요구사항·채점 출처: corpus-index.jsonl.",
                     "자동 후보는 문장 차이 기반으로 생성되어 원자성·필수성·충분성 판정이 없으며, 필요하지 않은 질문이나 누락이 있을 수 있다.",
                     "train 원본 MBPP 565행은 가상 사용자에게 제공되는 숨은 요구사항이 [REDACTED]다. validation은 전체에 기존 clarification overlay가 적용된다.", ""]
        report[report.index("문제별 질문과 예상 답"):report.index("문제별 질문과 예상 답")] = insertion
    if summary.get("illustrative_checks"):
        position = report.index("문제별 질문과 예상 답")
        report[position:position] = ["예시의 현재 채점 검증", "HumanEval/43: 위치가 다르면 같은 값도 허용하는 구현은 통과, 서로 다른 값만 허용하는 구현은 실패했다.",
                                    "HumanEval/149: 리스트를 반환해도 동률을 역알파벳순으로 처리하면 실패했고, 알파벳순 구현은 통과했다.",
                                    "직접 작성한 네 구현을 현재 Docker evaluator로 확인했다. 가상 사용자나 생성 모델의 한 질문 실험은 아니다.", ""]
    compact = ["100제 질문 목록", "", "예상 답은 사후 테스트 기준이며 실제 가상 사용자 응답이 아니다.",
               "질문 불필요에는 억지로 질문을 만들지 않았다. 여러 조건이 남는 문제는 모든 원자 질문 후보를 함께 기록했다.", ""]
    for r in ordered:
        heading = f"{r['index']:03d}. {r['task_id']} | {r['dataset']}/{r['source']} | {r['status_label_ko']}"
        q = r.get("question_ko") or "없음"
        ans = r.get("expected_answer_ko") or "해당 없음"
        lines = [heading, f"대표 질문: {q}", f"예상 답: {ans}"]
        if len(r["all_atomic_questions"]) > 1:
            lines.append("각 독립 조건의 질문:")
            for gap in r["all_atomic_questions"]:
                lines += [f"  - {gap['question_ko']}", f"    답: {gap['expected_answer_ko']}"]
        if r.get("remaining_after_answer_ko"):
            lines += ["대표 질문에 답한 뒤 남는 조건:"] + [f"  - {s}" for s in r["remaining_after_answer_ko"]]
        lines.append(f"판단: {r['rationale_ko']}")
        lines.append(f"질문 수 하한 추정: {r.get('minimum_questions_lower_bound')} | 확신: {r['confidence']}")
        compact += lines + [""]
        report += lines + ["근거:"] + [f"  - {e}" for e in r.get("test_evidence_ko", [])] + ["", "공개 문제:", r["prompt"].strip(), "", "=" * 72, ""]
    (HERE / "REPORT.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    (HERE / "questions100.txt").write_text("\n".join(compact) + "\n", encoding="utf-8")
    print(json.dumps({"counts": dict(counts), "atomic_questions": summary["atomic_questions_extracted"], "outputs": ["audit100.jsonl", "summary.json", "REPORT.txt", "questions100.txt"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

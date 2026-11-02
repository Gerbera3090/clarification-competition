#!/usr/bin/env python3
"""Produce explicitly unreviewed clarification drafts from corpus-index.jsonl.

Offline research artifact only. Reads public prose and the effective simulated
user evidence; deliberately never reads test inputs, outputs or canonical code.
Textual differences are candidate evidence, not proof of ambiguity, necessity,
atomicity, quality score, or one-question test sufficiency.
"""
from __future__ import annotations

import argparse
import collections
import difflib
import hashlib
import json
import re
from pathlib import Path

VERSION = "prose-clause-draft-v2-public-knowledge-filter"
DEFAULT_DIR = Path(__file__).resolve().parent
TYPE_PATTERNS = [
    ("dictionary", r"\b(?:dictionary|dict|dictionaries)\b"),
    ("tuple", r"\btuples?\b"),
    ("list", r"\b(?:list|array)s?\b"),
    ("string", r"\bstrings?\b"),
    ("boolean", r"\b(?:bool(?:ean)?|true\s+(?:or|and|/)\s+false)\b"),
    ("integer", r"\b(?:integer|int)s?\b"),
    ("float", r"\b(?:float|floating[- ]point)\b"),
]
IMPL = re.compile(
    r"\b(?:algorithm|implementation|implement|complexity|recurs\w*|loops?|"
    r"built[- ]in|libraries|library|sorting operations|comprehensions?|"
    r"bitwise operators?|code must|code should|use (?:map|filter|lambda))\b|O\s*\(", re.I
)
UNSAFE_Q = re.compile(
    r"\b(?:test(?:s|case| cases)?|reference (?:implementation|solution)|"
    r"canonical|example|sample (?:input|output)|for (?:the )?input|"
    r"function name|entry.point|signature|which algorithm|how (?:to|should I) implement)\b|"
    r">>>|assert\s+\w|[\[\{].{0,100}[\]\}].*(?:return|output|result)", re.I
)


def norm(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def prose_clauses(value: str | None) -> list[dict]:
    """Extract short natural-language clauses with source line locations.

    Imports, signatures, code, doctest inputs/outputs, assertions, examples,
    and literal expected values are not converted to questions.
    """
    if not value:
        return []
    clauses = []
    collecting = []
    first_line = 1
    example_mode = False

    def flush() -> None:
        nonlocal collecting
        if not collecting:
            return
        joined = re.sub(r"\s+", " ", " ".join(collecting)).strip(" \t\"'`")
        collecting = []
        # Only sentence/semicolon boundaries; arbitrary comma fragments often
        # lose the subject or condition and would create misleading questions.
        for piece in re.split(r"(?<=[.!?;])\s+(?=[A-Z])|;\s*", joined):
            piece = piece.strip(" \t\"'`;.-*")
            if len(re.findall(r"[A-Za-z]+", piece)) < 4:
                continue
            if len(piece) > 550 or UNSAFE_Q.search(piece):
                continue
            if re.match(r"^(?:Note|Examples?|Input|Output|Restrictions|Constraints|Variables)\s*:?$", piece, re.I):
                continue
            clauses.append({"text": piece, "line": first_line})

    for lineno, raw in enumerate(value.splitlines(), 1):
        line = raw.strip()
        # Formatting variants sometimes put prose directly after an opening
        # fence (```Write ...). The prose is still public information.
        if line.startswith("```"):
            line = re.sub(r"^```(?:python\b)?\s*", "", line).strip()
            if not line:
                flush()
                continue
        # Preserve docstrings that begin on the signature line, but not the
        # signature itself. Ordinary signatures are excluded entirely.
        if re.match(r"^(?:from\s+\w+\s+import|import\s|def\s|class\s|@)", line):
            flush()
            if '"""' in line:
                line = line.split('"""', 1)[1]
            else:
                continue
        line = line.replace('"""', '').replace("'''", '').strip()
        if not line:
            flush()
            continue
        if re.match(r"^(?:Examples?|For example|\[input/output\]|Sample|>>>|assert\b)", line, re.I):
            flush()
            example_mode = True
            continue
        if example_mode:
            # A known prose section can resume after examples, but literal
            # outputs and the text of example explanations stay excluded.
            if re.match(r"^(?:Note\s*:|Additional constraints\s*:|Restrictions\s*:|Constraints\s*:|The function|This function|If |Return |Given )", line, re.I):
                example_mode = False
            else:
                continue
        if re.match(r"^(?:return\s+\w+\(|[\[\]{}()]|True\b|False\b|None\b|[-+]?\d+(?:\.\d+)?\s*$|['\"]|#|```)", line):
            flush()
            continue
        if "==" in line or "=>" in line or "➞" in line or "$_CONTRACT_$" in line:
            flush()
            continue
        # Code-like statements outside a docstring are not natural requirements.
        if re.match(r"^(?:for |while |if .*:\s*$|else:|print\(|[\w.]+\s*=)", line):
            flush()
            continue
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line)
        if not collecting:
            first_line = lineno
        collecting.append(line)
        if re.search(r"[.!?;]$", line):
            flush()
    flush()
    return clauses


def overlap(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()


def matched(public: list[dict], clause: dict) -> tuple[dict | None, float]:
    if not public:
        return None, 0.0
    best = max(public, key=lambda item: overlap(item["text"], clause["text"]))
    return best, overlap(best["text"], clause["text"])


def return_types(text: str) -> list[str]:
    # A whole sentence mentioning an input list and a returned integer must
    # not be interpreted as a list return. Restrict matches to return phrases.
    regions = re.findall(r"\breturn(?:s|ed)?\b([^.;\n]{0,150})", text, re.I)
    found = []
    for region in regions:
        if re.match(r"\s+(?:true|false)\b", region, re.I):
            if "boolean" not in found:
                found.append("boolean")
            continue
        if re.match(r"\s+none\b", region, re.I):
            continue
        # Restrict noun-type claims to the direct object or explicit 'as a
        # string' form. A downstream input-domain noun is not a return type.
        explicit_as = re.search(r"\bas\s+(?:an?\s+)?(string|integer|float|list|tuple|dictionary|boolean)\b", region, re.I)
        if explicit_as:
            label = explicit_as.group(1).lower()
            if label not in found:
                found.append(label)
            continue
        region = re.split(r"\b(?:if|when|for|where|such that|is|of|that|with|containing|in)\b", region, maxsplit=1, flags=re.I)[0]
        region = " ".join(region.split()[:5])
        for label, pattern in TYPE_PATTERNS:
            if re.search(pattern, region, re.I) and label not in found:
                found.append(label)
    return found


def known_public_output_types(prompt: str, public: list[dict]) -> set[str]:
    text = " ".join(c["text"] for c in public)
    found = set(return_types(text))
    for head in re.findall(r"\b(?:output|return value|result)\s+(?:(?:must|should|will)\s+)?(?:also\s+)?(?:be|is)\s+([^.;]{0,60})", text, re.I):
        for label, pattern in TYPE_PATTERNS:
            if re.match(r"\s*(?:an?\s+|the\s+)?" + pattern, head, re.I):
                found.add(label)
    # Signatures are public evidence for suppression, never a source from
    # which to generate a clarification question. Only the outer container
    # type is used (List[str] does not imply a string return).
    aliases = {"list": "list", "array": "list", "tuple": "tuple", "str": "string",
               "string": "string", "int": "integer", "integer": "integer",
               "bool": "boolean", "boolean": "boolean", "dict": "dictionary",
               "dictionary": "dictionary", "float": "float"}
    for annotation in re.findall(r"\bdef\s+[^\n]*?->\s*([^:\n]+)", prompt):
        annotation = annotation.strip()
        if annotation.startswith("Union[") or annotation.startswith("Optional["):
            options = annotation.split("[", 1)[1].rstrip("]").split(",")
        else:
            options = annotation.split("|")
        for option in options:
            outer = re.match(r"(?:typing\.)?([A-Za-z_]+)", option.strip())
            if outer and outer.group(1).lower() in aliases:
                found.add(aliases[outer.group(1).lower()])
    return found


def behavior_tokens(text: str) -> list[str]:
    text = text.lower().replace("’", "'")
    text = re.sub(r"^.*?\b(?:function|routine|procedure|program)\b\s*(?:that\s+)?(?:to\s+)?", "", text)
    text = re.sub(r"\bdetermine how many\b|\bfind (?:the )?number of\b", "count", text)
    replacements = {"determine": "find", "calculate": "compute", "calculates": "compute",
                    "erase": "remove", "delete": "remove", "deletes": "remove",
                    "characters": "character", "charcter": "character", "charcters": "character",
                    "elements": "element", "values": "value", "numbers": "number",
                    "strings": "string", "lists": "list", "arrays": "list", "array": "list",
                    "tuples": "tuple", "integers": "integer", "int": "integer",
                    "bool": "boolean", "max": "maximum", "min": "minimum",
                    "largest": "maximum", "smallest": "minimum"}
    ignored = {"write", "create", "python", "pythn", "programming", "language", "a", "an", "the",
               "given", "provided", "specified", "input", "to", "of", "in", "from", "for", "its", "it", "is", "be"}
    return [replacements.get(t, t) for t in re.findall(r"[a-z0-9]+", text) if t not in ignored]


def obvious_behavior_paraphrase(reference: str, public: str) -> bool:
    left, right = behavior_tokens(reference), behavior_tokens(public)
    if not left or not right:
        return False
    # Keep changes of quantifier, sign, boundary, order and numeric constant.
    # A one-word difference here can be precisely the required clarification.
    critical = {"minimum", "maximum", "left", "right", "first", "last", "odd", "even",
                "ascending", "descending", "true", "false", "none", "empty", "nonempty",
                "inclusive", "exclusive", "greater", "less", "longest", "shortest", "equal",
                "different", "distinct", "duplicate", "duplicates", "overlap", "overlapping",
                "not", "no", "all", "any", "exactly", "each", "positive", "negative", "zero"}
    if ({t for t in left if t in critical or t.isdigit()}
            != {t for t in right if t in critical or t.isdigit()}):
        return False
    if left == right:
        return True
    # Reject tiny spelling/inflection/function-word differences, without
    # attempting an expansive or semantic synonym dictionary.
    sequence_similarity = difflib.SequenceMatcher(None, " ".join(left), " ".join(right), autojunk=False).ratio()
    left_set, right_set = set(left), set(right)
    jaccard = len(left_set & right_set) / len(left_set | right_set)
    return sequence_similarity >= 0.91 or jaccard >= 0.88


def question_for_clause(text: str, public_text: str, entry: str) -> tuple[str | None, str | None, int]:
    """Conservative single-topic templates; all remain atomicity-unverified."""
    if IMPL.search(text):
        return None, "implementation_or_complexity_clause", 0
    lower = text.lower()
    types = return_types(text)
    if len(types) == 1 and return_types(public_text) != types:
        return f"For {entry}, should the return value have the {types[0]} type?", "return_type", 95
    if re.search(r"\bduplicat\w*\b", lower):
        return f"For {entry}, how should duplicate input values be handled?", "duplicate_policy", 85
    if "case sensitive" in lower or "case-sensitive" in lower or "case insensitive" in lower or "case-insensitive" in lower:
        return f"For {entry}, should matching be case-sensitive?", "case_sensitivity", 85
    if re.search(r"same length|tie(?:s|d)?\b|equal (?:length|value)", lower) and re.search(r"sort|order|alphabet", lower):
        return f"For {entry}, what ordering should resolve equal-key ties?", "tie_break_order", 90
    if re.search(r"original order|order.*(?:preserv|maintain)|(?:preserv|maintain).*order", lower):
        return f"For {entry}, should the result preserve the input order?", "order_preservation", 85
    if "ascending" in lower or "descending" in lower or "alphabetical" in lower:
        if "length" in lower:
            return f"For {entry}, should the result be ordered by increasing element length?", "length_order", 80
        directions = [v for v in ["ascending", "descending", "alphabetical"] if v in lower]
        if len(directions) == 1:
            return f"For {entry}, should the result use {directions[0]} order?", "result_order", 80
    if re.search(r"overlap(?:p?ing)?", lower):
        return f"For {entry}, should overlapping occurrences be counted?", "overlap_counting", 85
    if re.search(r"\bempty\b", lower) and re.search(r"return|result|output", lower):
        return f"For {entry}, what value should be returned for an empty input?", "empty_input_result", 90
    if re.search(r"\b(?:odd|even)\b", lower) and "natural number" in lower:
        parity = "odd" if re.search(r"\bodd\b", lower) else "even"
        return f"For {entry}, should the selected natural numbers be {parity}?", "number_parity", 90
    if re.search(r"\bleft\b.*\binsertion|\binsertion\b.*\bleft\b", lower):
        return f"For {entry}, should insertion occur before existing equal values?", "insertion_tie_side", 90
    if re.search(r"\bright\b.*\binsertion|\binsertion\b.*\bright\b", lower):
        return f"For {entry}, should insertion occur after existing equal values?", "insertion_tie_side", 90
    # Positive confirmation of a short declarative behavioral rule is useful
    # for deleted/incomplete prose, provided it is not a whole-task request.
    cleaned = re.sub(r"^(?:The function should |The function must |This function should |The function |It )", "", text, flags=re.I).strip(" .")
    target = re.sub(r"^(?:Write|Create) (?:an? )?(?:python )?(?:function|routine) to ", "", cleaned, flags=re.I)
    if target != cleaned:
        target_words = re.findall(r"\b\w+\b", target)
        if (5 <= len(target_words) <= 19
                and not re.search(r"\b(?:and|also|while|whereas|however|moreover|using|algorithm|approach|method)\b", target, re.I)
                and re.match(r"^(?:find|check|count|compute|replace|remove|return|determine|locate|convert|calculate|filter|move|rotate|sort|reverse|extract|concatenate|split|sum|multiply)\b", target, re.I)):
            return f"For {entry}, should the function {target[0].lower() + target[1:]}?", "behavioral_target_confirmation", 40
    words = re.findall(r"\b\w+\b", cleaned)
    if not 5 <= len(words) <= 23:
        return None, "clause_too_broad_or_fragmentary", 0
    if re.search(r"\b(?:and|also|while|whereas|however|moreover)\b", cleaned, re.I):
        return None, "potentially_multiple_independent_facts", 0
    if re.match(r"^(?:Write|Create|Implement|Given|Knowing|Input|Your task)\b", cleaned, re.I):
        return None, "whole_task_or_context_clause", 0
    if re.search(r"\b(?:return|output|count|exclude|include|retain|preserve|match|accept|support|contain|assume|must|should)\b", cleaned, re.I):
        return f'For {entry}, is this behavioral rule intended: "{cleaned}"?', "single_clause_confirmation", 45
    return None, "no_safe_specific_behavioral_template", 0


def qa_candidate(question: str, entry: str) -> tuple[str | None, str | None]:
    question = re.sub(r"\s+", " ", question).strip()
    if not question or len(question) > 480:
        return None, "qa_question_empty_or_too_long"
    if UNSAFE_Q.search(question) or IMPL.search(question):
        return None, "qa_question_requests_examples_tests_or_implementation"
    if question.count("?") != 1 or re.search(r"(?:^|\s)\d+[.)]\s", question):
        return None, "qa_question_not_a_single_question"
    if re.search(r"all (?:the )?(?:requirements|behaviors|constraints)|full specification|entire specification", question, re.I):
        return None, "qa_question_requests_multiple_requirements"
    if not re.match(r"^(?:Should|What|Which|How|Is|Are|Does|Do|Can|Must|When|If|For)\b", question, re.I):
        return None, "qa_question_requires_manual_rephrasing"
    # Existing question is evidence only; an apparent single question may
    # still elicit several facts, hence no atomicity claim is made.
    return f"For {entry}, {question[0].lower() + question[1:]}", None


def generate(row: dict, index_path: Path, index_line: int) -> dict:
    public = prose_clauses(row.get("prompt"))
    hidden_kind = row["hidden_requirements_source"]["kind"]
    overlay = row.get("effective_clarifications")
    effective = row.get("effective_hidden_requirements")
    reference = effective if hidden_kind == "reference_prompt" else None
    hidden = prose_clauses(reference)
    candidates = []
    clauses = []
    entry = row.get("entry_point") or row["task_id"]
    evidence = row["hidden_requirements_source"]
    public_output_types = known_public_output_types(row.get("prompt") or "", public)
    public_conflict_marker = bool(re.search(
        r"\b(?:but|however|instead|contradict\w*|whereas|yet|while also|must additionally|always return)\b",
        row.get("prompt") or "", re.I))
    suppressed = {}

    def add(question: str, topic: str, answer: str, source: dict, priority: int) -> None:
        if topic == "return_type":
            requested = re.search(r"have the (\w+) type", question)
            if requested and public_output_types == {requested.group(1)}:
                suppressed[question] = "return_type_already_explicit_publicly_without_conflict"
                return
        if topic in {"behavioral_target_confirmation", "single_clause_confirmation"} and not public_conflict_marker:
            if any(obvious_behavior_paraphrase(answer, c["text"]) for c in public):
                suppressed[question] = "behavior_already_public_as_obvious_paraphrase"
                return
        if question in {c["question"] for c in candidates}:
            return
        cid = "candidate-" + hashlib.sha256(question.encode()).hexdigest()[:12]
        candidates.append({
            "candidate_id": cid, "question": question, "topic": topic,
            "expected_answer_evidence": answer, "evidence_ref": source,
            "atomicity": "atomicity_unverified", "sufficiency": "not_assessed",
            "quality": "not_assessed", "test_alignment": "not_assessed",
            "ranking_priority": priority,
        })

    if overlay is not None:
        for position in range(0, len(overlay), 2):
            q = str(overlay[position])
            answer = str(overlay[position + 1]) if position + 1 < len(overlay) else ""
            proposed, reason = qa_candidate(q, entry)
            ref = {"source": evidence, "question_index": position, "answer_index": position + 1 if answer else None}
            clauses.append({"kind": "existing_qa", "public_clause": None, "evidence_clause": q,
                            "answer_evidence": answer, "evidence_ref": ref,
                            "candidate_question": proposed, "pending_reason": reason})
            if proposed and answer:
                add(proposed, "existing_qa_behavior", answer, ref, 100)
    elif reference:
        for clause in hidden:
            public_match, similarity = matched(public, clause)
            if public_match and norm(public_match["text"]) == norm(clause["text"]):
                continue
            public_text = public_match["text"] if public_match else ""
            proposed, topic_or_reason, priority = question_for_clause(clause["text"], public_text, entry)
            # Near-identical paraphrases offer no evidence that information is
            # absent; leave them pending instead of manufacturing a question.
            if similarity >= 0.96:
                proposed, topic_or_reason = None, "near_exact_textual_change_only"
            ref = {"source": evidence, "effective_reference_line": clause["line"]}
            clauses.append({"kind": "reference_prose_delta", "public_clause": public_text or None,
                            "public_line": public_match["line"] if public_match else None,
                            "evidence_clause": clause["text"], "evidence_ref": ref,
                            "normalized_similarity": round(similarity, 5),
                            "candidate_question": proposed,
                            "pending_reason": None if proposed else topic_or_reason})
            if proposed:
                add(proposed, topic_or_reason, clause["text"], ref, priority)
        # Keep the reverse diff as well. In contradictory variants the
        # original sentence may survive unchanged next to a conflicting added
        # sentence; a reference-only deletion diff would miss that conflict.
        hidden_normalized = {norm(c["text"]) for c in hidden}
        for public_clause in public:
            if norm(public_clause["text"]) in hidden_normalized:
                continue
            hidden_match, similarity = matched(hidden, public_clause)
            proposed, topic_or_reason, priority = None, "public_addition_requires_semantic_review", 0
            if IMPL.search(public_clause["text"]):
                topic_or_reason = "implementation_or_complexity_clause"
            elif hidden_match and similarity >= 0.35:
                proposed, topic_or_reason, priority = question_for_clause(hidden_match["text"], public_clause["text"], entry)
            if similarity >= 0.96:
                proposed, topic_or_reason = None, "near_exact_textual_change_only"
            ref = {"source": evidence,
                   "effective_reference_line": hidden_match["line"] if hidden_match else None}
            clauses.append({"kind": "public_prose_addition_or_replacement",
                            "public_clause": public_clause["text"], "public_line": public_clause["line"],
                            "evidence_clause": hidden_match["text"] if hidden_match else None,
                            "evidence_ref": ref, "normalized_similarity": round(similarity, 5),
                            "candidate_question": proposed,
                            "pending_reason": None if proposed else topic_or_reason})
            if proposed and hidden_match:
                add(proposed, topic_or_reason, hidden_match["text"], ref, priority)
        # Reference prose may agree with the first public clause while public
        # additions contradict it. Detect return-type and opposite-word changes
        # without promoting arbitrary instruction deletion to a requirement.
        public_text = " ".join(c["text"] for c in public)
        hidden_text = " ".join(c["text"] for c in hidden)
        public_types, hidden_types = return_types(public_text), return_types(hidden_text)
        if len(hidden_types) == 1 and set(public_types) != set(hidden_types):
            matching_clauses = [c for c in hidden if hidden_types[0] in return_types(c["text"])]
            if matching_clauses:
                c = matching_clauses[0]
                add(f"For {entry}, should the return value have the {hidden_types[0]} type?", "return_type",
                    c["text"], {"source": evidence, "effective_reference_line": c["line"]}, 98)

    for clause in clauses:
        proposed = clause.get("candidate_question")
        if proposed in suppressed:
            clause["rejected_candidate_question"] = proposed
            clause["candidate_question"] = None
            clause["pending_reason"] = suppressed[proposed]
    candidates.sort(key=lambda c: (-c["ranking_priority"], c["candidate_id"]))
    selected = candidates[0] if candidates else None
    if not row.get("sdk_preprocess_usable", True):
        pending = "excluded_from_sdk_preprocessing"
    elif overlay is not None and not overlay:
        pending = "effective_clarifications_empty_no_hidden_fact_evidence"
    elif hidden_kind == "absent_redacted" or (overlay is None and not reference):
        pending = "effective_reference_missing_or_redacted"
    elif selected:
        pending = None
    elif overlay is not None:
        pending = "existing_qa_requires_behavioral_and_atomicity_review"
    elif norm(row.get("prompt") or "") == norm(reference or ""):
        pending = "exact_reference_no_textual_delta_not_a_no_question_verdict"
    elif [norm(c["text"]) for c in public] == [norm(c["text"]) for c in hidden]:
        pending = "no_prose_delta_signature_format_or_examples_only"
    elif not hidden:
        pending = "effective_reference_has_no_safe_prose_clause"
    else:
        pending = "textual_delta_requires_semantic_review"

    return {
        "row_key": row["row_key"], "task_id": row["task_id"], "split": row["split"],
        "source_variant": row["source_variant"], "source_file": row["source_file"],
        "source_line": row["source_line"], "entry_point": row.get("entry_point"),
        "draft_generator": VERSION, "annotation_status": "algorithmic_draft_unreviewed",
        "atomicity": "atomicity_unverified", "sufficiency": "not_assessed",
        "necessity": "not_assessed", "test_alignment": "not_assessed",
        "sdk_preprocess_usable": row.get("sdk_preprocess_usable"),
        "hidden_requirements_source": evidence,
        "question": selected["question"] if selected else None,
        "selected_candidate_id": selected["candidate_id"] if selected else None,
        "expected_answer_evidence": selected["expected_answer_evidence"] if selected else None,
        "expected_answer_evidence_ref": selected["evidence_ref"] if selected else None,
        "candidate_count": len(candidates), "candidate_questions": candidates,
        "candidate_clauses": clauses, "pending_reason": pending,
        "public_explicit_output_types": sorted(public_output_types),
        "suppressed_candidate_count": len(suppressed),
        "suppressed_candidates": [{"question": question, "reason": reason} for question, reason in suppressed.items()],
        "review_notes": [
            "Candidate ranking is a textual heuristic, not estimated pass probability.",
            "Expected answer evidence may contain multiple facts or disagree with tests; it is not a validated answer.",
            "No tests, canonical implementation, simulator or model calls were used to draft this question.",
            "A null question means pending review, not proof that no clarification is needed.",
        ],
        "corpus_index_ref": {"path": str(index_path), "line": index_line},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_DIR / "corpus-index.jsonl")
    parser.add_argument("--output", type=Path, default=DEFAULT_DIR / "draft-questions.jsonl")
    parser.add_argument("--summary", type=Path, default=DEFAULT_DIR / "draft-questions-summary.json")
    args = parser.parse_args()
    counts = collections.Counter()
    topics = collections.Counter()
    by_source = collections.Counter()
    count = 0
    # Materialize and validate the whole snapshot before opening the output.
    # Another inventory worker may be rebuilding the input atomically or in
    # place; incomplete input must not destroy an existing complete draft.
    input_bytes = args.input.read_bytes()
    parsed = [(i, json.loads(line)) for i, line in enumerate(input_bytes.decode("utf-8").splitlines(), 1) if line.strip()]
    temporary_output = args.output.with_name(args.output.name + ".tmp")
    with temporary_output.open("w", encoding="utf-8") as out:
        for index_line, row in parsed:
            draft = generate(row, args.input.resolve(), index_line)
            out.write(json.dumps(draft, ensure_ascii=False) + "\n")
            counts[draft["pending_reason"] or "question_candidate_present"] += 1
            topics.update(c["topic"] for c in draft["candidate_questions"])
            by_source[row["hidden_requirements_source"]["kind"]] += 1
            count += 1
    temporary_output.replace(args.output)
    summary = {
        "generator": VERSION, "rows": count, "categories": dict(counts),
        "candidate_topics": dict(topics), "hidden_requirement_sources": dict(by_source),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "limitations": [
            "Offline automatic draft; no semantic adjudication or test sufficiency verification.",
            "All candidates have atomicity_unverified and sufficiency=not_assessed.",
            "Textual paraphrases may generate unnecessary questions; incomplete prose may miss important questions.",
            "Exact reference equality does not imply a fully specified task.",
            "Existing QA fragments are evidence, not guaranteed atomic or test-consistent answers.",
            "Validation drafts are an oracle research artifact; do not feed them to a benchmark participant.",
        ],
    }
    temporary_summary = args.summary.with_name(args.summary.name + ".tmp")
    temporary_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary_summary.replace(args.summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

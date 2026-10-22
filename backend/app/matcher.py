"""Match BOM lines to parts-master items.

Order of attempts per line:
  1. item number present in master          -> exact_item_no
  2. normalized description equals master   -> exact_desc (review when several items share it)
  3. trigram candidate retrieval + rapidfuzz rescoring + attribute penalties
       score >= AUTO_THRESHOLD and a clear winner -> auto
       score >= REVIEW_THRESHOLD                  -> review
       otherwise                                  -> unmatched (candidates still kept for the user)
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from rapidfuzz import fuzz
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.normalize import SOFT_TOKENS, extract_attrs, infer_noun, normalize
from app.search import RANK_WINDOW, avoid_seq_scan

AUTO_THRESHOLD = 92.0
REVIEW_THRESHOLD = 70.0
AMBIGUITY_GAP = 1.5
TOP_CANDIDATES = 5
RETRIEVE_LIMIT = 40
MIN_CANDIDATES = 5

# attribute -> penalty when the candidate has a different value / lacks it entirely
CRITICAL_ATTRS = {
    "ptype": (35, 10),
    "dn": (30, 10),
    "sch": (25, 8),
    "cl": (25, 8),
    "m": (30, 10),
    "inch": (30, 10),
    "deg": (25, 8),
    "grade": (30, 10),
    "spec": (20, 6),
    "mm": (20, 6),
}
RELATED_PTYPE_PENALTY = 15
SCH_SUFFIX_PENALTY = 8
GRADE_CONDITION_PENALTY = 8
# end preparation of pipes and swages: soft words for retrieval, but PE vs BE is a different part
END_PREPS = {"PE", "BE", "TBE", "PBE", "TOE", "POE", "BOE", "BLE", "PLE", "TLE", "PSE", "BSE", "TSE"}
END_PREP_PENALTY = 10
NEAR_LENGTH_PENALTY = 12
NEAR_LENGTH_TOLERANCE = 0.1
FASTENER_PTYPES = {"BOLT", "STUD", "NUT", "WASHER", "S+B+W", "N+B+W", "S+N+W", "B+N+W"}
SUBTYPE_MISSING_PENALTY = 8
SUBTYPE_EXTRA_PENALTY = 2
FLAG_MISSING_PENALTY = 12
FLAG_EXTRA_PENALTY = 6
UNDERSPECIFIED_PENALTY = 3
# words in the candidate that the BOM line does not mention: small, mainly breaks ties
EXTRA_TOKEN_PENALTY = 1.5
EXTRA_TOKEN_PENALTY_CAP = 4.5
# BOM words the candidate lacks while other candidates have them
UNSUPPORTED_TOKEN_PENALTY = 3.0
UNSUPPORTED_TOKEN_PENALTY_CAP = 9.0

PART_COLS = "id, item_no, description, item_group, description_norm, attrs"
# must stay identical to the ix_parts_tokens index expression
TOKENS_SQL = "string_to_array(description_norm, ' ')"


@dataclass
class MatchResult:
    status: str
    part_id: int | None = None
    score: float | None = None
    candidates: list[dict] = field(default_factory=list)


def _score_token(tok: str) -> str:
    # SCH 40S vs SCH 40 and 6MM vs 6 are judged by the attributes, not by the text similarity
    if tok.startswith("SCH") and tok.endswith("S") and tok[3:-1].isdigit():
        return tok[:-1]
    if tok.endswith("MM") and tok[:-2].replace(".", "", 1).isdigit():
        return tok[:-2]
    return tok


def _near_length(lset: set[str], cset: set[str]) -> bool:
    if len(lset) != 1 or len(cset) != 1:
        return False
    try:
        a, b = float(next(iter(lset))), float(next(iter(cset)))
    except ValueError:
        return False
    return a > 0 and abs(a - b) / a <= NEAR_LENGTH_TOLERANCE


def _score_tokens(norm: str) -> list[str]:
    return [_score_token(t) for t in norm.split() if t not in SOFT_TOKENS]


def score_candidate(line_norm: str, line_attrs: dict, cand_norm: str, cand_attrs: dict) -> float:
    l_toks, c_toks = _score_tokens(line_norm), _score_tokens(cand_norm)
    # catalog words that follow from the rest of the line (material class, dimensional standard)
    # count only when the BOM line writes them too
    implied = set(cand_attrs.get("implied", ())) - set(l_toks)
    c_toks = [t for t in c_toks if t not in implied]
    l_str, c_str = " ".join(l_toks), " ".join(c_toks)
    base = 0.8 * fuzz.token_set_ratio(l_str, c_str) + 0.2 * fuzz.token_sort_ratio(l_str, c_str)
    extra_words = len(set(c_toks) - set(l_toks))
    penalty = min(EXTRA_TOKEN_PENALTY * extra_words, EXTRA_TOKEN_PENALTY_CAP)

    for key, (mismatch, missing) in CRITICAL_ATTRS.items():
        lv = line_attrs.get(key)
        if not lv:
            continue
        cv = cand_attrs.get(key)
        if key == "ptype":
            if not cv:
                penalty += missing
            elif lv != cv:
                related = (lv in FASTENER_PTYPES or "+" in lv) and (cv in FASTENER_PTYPES or "+" in cv)
                penalty += RELATED_PTYPE_PENALTY if related else mismatch
            continue
        lset, cset = set(lv), set(cv or ()) - implied
        if not cset:
            penalty += missing
            continue
        if lset == cset:
            continue
        if key == "mm" and _near_length(lset, cset):
            # nearest standard length (BOM 230, master 220 / 240): a suggestion for review, never auto
            penalty += NEAR_LENGTH_PENALTY
            continue
        if key == "sch" and {v.rstrip("S") for v in lset} == {v.rstrip("S") for v in cset}:
            # SCH 10S vs SCH 10: same nominal schedule, stainless vs carbon designation
            penalty += SCH_SUFFIX_PENALTY
            continue
        if key == "grade" and {v.removesuffix("N") for v in lset} == {v.removesuffix("N") for v in cset}:
            # SA516 GR 70N vs GR 70: same grade, normalized delivery condition
            penalty += GRADE_CONDITION_PENALTY
            continue
        if lset < cset:
            # the BOM line is less specific (e.g. one DN given for a reducer)
            penalty += UNDERSPECIFIED_PENALTY * len(cset - lset)
        else:
            penalty += mismatch

    l_end, c_end = END_PREPS.intersection(line_norm.split()), END_PREPS.intersection(cand_norm.split())
    if l_end and c_end and not l_end & c_end:
        penalty += END_PREP_PENALTY

    l_sub, c_sub = set(line_attrs.get("subtype", [])), set(cand_attrs.get("subtype", []))
    penalty += SUBTYPE_MISSING_PENALTY * len(l_sub - c_sub) + SUBTYPE_EXTRA_PENALTY * len(c_sub - l_sub)
    l_flags, c_flags = set(line_attrs.get("flags", [])), set(cand_attrs.get("flags", []))
    penalty += FLAG_MISSING_PENALTY * len(l_flags - c_flags) + FLAG_EXTRA_PENALTY * len(c_flags - l_flags)

    return round(max(0.0, min(100.0, base - penalty)), 1)


def _key_tokens(toks: list[str], attrs: dict) -> list[str]:
    """Tokens that identify the part: product type, grade and everything with a digit (sizes, schedule, class,
    bolt size/length, designations such as 6205 or ISMC 100, ratings such as 7.5KW)."""
    keys = set(attrs.get("ptype", "").split())
    grades = set(attrs.get("grade", []))
    for t in toks:
        if t in grades or any(c.isdigit() for c in t):
            keys.add(t)
    return [t for t in toks if t in keys]


def _unit_variant(tok: str) -> str | None:
    if tok.replace(".", "", 1).isdigit():
        return tok + "MM"
    if tok.endswith("MM") and tok[:-2].replace(".", "", 1).isdigit():
        return tok[:-2]
    return None


def _whole_token_query(db: Session, toks: list[str], norm: str) -> list[dict]:
    if not toks:
        return []
    # whole-word containment on the word-array index (ix_parts_tokens): one posting list per word instead of
    # the trigram index's several much longer ones per word
    params: dict = {"norm": norm, "window": RANK_WINDOW, "limit": RETRIEVE_LIMIT}
    words, conds = [], []
    for tok in toks:
        alt = _unit_variant(tok)
        if alt:
            # "SHAFT 55" in the BOM, "SHAFT 55MM" in the master (and the other way round)
            params[f"u{len(conds)}"] = [tok, alt]
            conds.append(f"{TOKENS_SQL} && CAST(:u{len(conds)} AS text[])")
        else:
            words.append(tok)
    if words:
        params["words"] = words
        conds.append(f"{TOKENS_SQL} @> CAST(:words AS text[])")
    rows = db.execute(
        text(f"""SELECT {PART_COLS} FROM (
                    SELECT {PART_COLS}, search_text FROM parts
                    WHERE is_active AND {' AND '.join(conds)} LIMIT :window) hits
                 ORDER BY similarity(search_text, :norm) DESC LIMIT :limit"""),
        params,
    )
    return [dict(r._mapping) for r in rows]


def _similarity_query(db: Session, norm: str, noun: str | None) -> list[dict]:
    params: dict = {"norm": f" {norm} ", "limit": RETRIEVE_LIMIT}
    noun_sql = ""
    if noun:
        noun_sql = " AND noun = :noun"
        params["noun"] = noun
    db.execute(text("SET LOCAL pg_trgm.similarity_threshold = 0.3"))
    rows = db.execute(
        text(f"""SELECT {PART_COLS} FROM parts
                 WHERE is_active AND search_text % :norm{noun_sql}
                 ORDER BY similarity(search_text, :norm) DESC LIMIT :limit"""),
        params,
    )
    return [dict(r._mapping) for r in rows]


def retrieve_candidates(db: Session, norm: str, attrs: dict) -> list[dict]:
    toks = [t for t in dict.fromkeys(norm.split()) if t not in SOFT_TOKENS]
    found: dict[int, dict] = {}
    avoid_seq_scan(db)

    def add(rows: list[dict]) -> None:
        for r in rows:
            found.setdefault(r["id"], r)

    add(_whole_token_query(db, toks, norm))
    keys = _key_tokens(toks, attrs)
    if len(found) < MIN_CANDIDATES and keys and keys != toks:
        add(_whole_token_query(db, keys, norm))
    if len(found) < MIN_CANDIDATES and len(keys) >= 3:
        # relax one identifying attribute at a time (e.g. SCH 10S in the BOM, SCH 10 in the master)
        for dropped in keys:
            add(_whole_token_query(db, [k for k in keys if k != dropped], norm))
    if not found:
        add(_similarity_query(db, norm, infer_noun(attrs)))
    return list(found.values())


def _candidate_dict(row: dict, score: float) -> dict:
    return {
        "part_id": row["id"],
        "item_no": row["item_no"],
        "description": row["description"],
        "item_group": row["item_group"],
        "score": score,
    }


def match_description(db: Session, raw_description: str) -> MatchResult:
    norm = normalize(raw_description)
    if not norm:
        return MatchResult(status="unmatched")
    attrs = extract_attrs(norm)
    rows = retrieve_candidates(db, norm, attrs)
    # BOM words that some candidates contain and others lack tell them apart (ISMB 200 vs ISLB 200);
    # words no candidate contains are noise and cost nothing
    line_toks = set(_score_tokens(norm))
    cand_toks = [set(_score_tokens(r["description_norm"])) for r in rows]
    seen = set().union(*cand_toks) if cand_toks else set()
    evidence = line_toks & seen
    scored = sorted(
        ((round(max(0.0, score_candidate(norm, attrs, r["description_norm"], r["attrs"] or {})
                    - min(UNSUPPORTED_TOKEN_PENALTY * len(evidence - toks), UNSUPPORTED_TOKEN_PENALTY_CAP)), 1), r)
         for r, toks in zip(rows, cand_toks)),
        key=lambda x: (-x[0], len(x[1]["description"]), x[1]["item_no"]),
    )
    candidates = [_candidate_dict(r, s) for s, r in scored[:TOP_CANDIDATES]]
    if not scored:
        return MatchResult(status="unmatched")

    best_score, best = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else -1.0
    clear_winner = best_score - runner_up >= AMBIGUITY_GAP
    if best_score >= AUTO_THRESHOLD and clear_winner:
        return MatchResult(status="auto", part_id=best["id"], score=best_score, candidates=candidates)
    if best_score >= REVIEW_THRESHOLD:
        return MatchResult(status="review", score=best_score, candidates=candidates)
    return MatchResult(status="unmatched", score=best_score, candidates=candidates)


def match_lines(db: Session, lines: list[tuple[str | None, str | None]]) -> list[MatchResult]:
    """lines: (raw_item_no, raw_description) pairs. Returns one MatchResult per input line, in order."""
    results: list[MatchResult | None] = [None] * len(lines)

    item_nos = {str(no).strip() for no, _ in lines if no and str(no).strip()}
    by_item_no: dict[str, dict] = {}
    if item_nos:
        rows = db.execute(text(f"SELECT {PART_COLS} FROM parts WHERE item_no = ANY(:nos)"), {"nos": list(item_nos)})
        by_item_no = {r.item_no: dict(r._mapping) for r in rows}

    norms: dict[int, str] = {}
    for i, (no, desc) in enumerate(lines):
        hit = by_item_no.get(str(no).strip()) if no else None
        if hit:
            results[i] = MatchResult("exact_item_no", hit["id"], 100.0, [_candidate_dict(hit, 100.0)])
        else:
            norm = normalize(desc)
            if norm:
                norms[i] = norm
            else:
                results[i] = MatchResult(status="unmatched")

    by_norm: dict[str, list[dict]] = {}
    if norms:
        rows = db.execute(
            text(f"SELECT {PART_COLS} FROM parts WHERE is_active AND description_norm = ANY(:norms) ORDER BY item_no"),
            {"norms": list(set(norms.values()))},
        )
        for r in rows:
            by_norm.setdefault(r.description_norm, []).append(dict(r._mapping))

    for i, norm in norms.items():
        exact = by_norm.get(norm)
        if exact and len(exact) == 1:
            results[i] = MatchResult("exact_desc", exact[0]["id"], 100.0, [_candidate_dict(exact[0], 100.0)])
        elif exact:
            results[i] = MatchResult("review", None, 100.0, [_candidate_dict(r, 100.0) for r in exact[:TOP_CANDIDATES]])
        else:
            results[i] = match_description(db, lines[i][1] or "")

    return [r or MatchResult(status="unmatched") for r in results]


PARALLEL_CHUNK = 40
PARALLEL_WORKERS = 4


def _match_chunk(chunk: list[tuple[str | None, str | None]]) -> list[MatchResult]:
    db = SessionLocal()
    try:
        return match_lines(db, chunk)
    finally:
        db.rollback()
        db.close()


def match_lines_parallel(lines: list[tuple[str | None, str | None]]) -> list[MatchResult]:
    """Same as match_lines, but large BOMs are split across several DB sessions."""
    if len(lines) <= PARALLEL_CHUNK:
        return _match_chunk(lines)
    chunks = [lines[i:i + PARALLEL_CHUNK] for i in range(0, len(lines), PARALLEL_CHUNK)]
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as pool:
        return [r for part in pool.map(_match_chunk, chunks) for r in part]


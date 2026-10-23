"""Type-ahead part search over the trigram-indexed `search_text` column."""
from __future__ import annotations

import threading
import time

from rapidfuzz import fuzz, process
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.normalize import SOFT_TOKENS, normalize

PART_COLUMNS = "id, item_no, description, item_group, uom_group, in_stock, standard_cost, avg_cost, noun"
NUMERIC_COLUMNS = ("in_stock", "standard_cost", "avg_cost")
MAX_TOKENS = 8
# Matching rows beyond this are not ranked: generic queries ("ELBOW") would otherwise score
# hundreds of thousands of rows per keystroke. Users narrow down by typing more.
RANK_WINDOW = 2000
VOCAB_TTL_SECONDS = 600
TYPO_CUTOFF = 75


def avoid_seq_scan(db: Session) -> None:
    """Parts are stored grouped by noun, so a LIMITed seq scan for a common word ("VALVE") reads every row of
    the nouns stored before it; the trigram bitmap scan stops after the first RANK_WINDOW hits instead."""
    db.execute(text("SET LOCAL enable_seqscan = off"))


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def query_tokens(q: str) -> tuple[str, list[str]]:
    norm = normalize(q)
    toks = norm.split()
    if not toks:
        norm = " ".join(q.upper().split())
        toks = norm.split()
    toks = [t for t in toks if t not in SOFT_TOKENS] or toks
    # longest tokens first: they are the most selective for the trigram index
    toks = sorted(dict.fromkeys(toks), key=len, reverse=True)[:MAX_TOKENS]
    return norm, toks


class _Vocabulary:
    """Distinct normalized tokens of the parts master, used to correct typos in queries."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens: list[str] = []
        self._loaded_at = 0.0

    def invalidate(self) -> None:
        self._loaded_at = 0.0

    def get(self, db: Session) -> list[str]:
        if time.time() - self._loaded_at > VOCAB_TTL_SECONDS:
            with self._lock:
                if time.time() - self._loaded_at > VOCAB_TTL_SECONDS:
                    rows = db.execute(text(
                        "SELECT DISTINCT tok FROM parts, unnest(string_to_array(description_norm, ' ')) AS tok "
                        "WHERE is_active"
                    ))
                    self._tokens = [r[0] for r in rows if r[0]]
                    self._loaded_at = time.time()
        return self._tokens

    def correct(self, db: Session, toks: list[str]) -> list[str]:
        vocab = self.get(db)
        out = []
        for tok in toks:
            if len(tok) < 3 or any(tok in v for v in vocab):
                out.append(tok)
                continue
            best = process.extractOne(tok, vocab, scorer=fuzz.ratio, score_cutoff=TYPO_CUTOFF)
            out.append(best[0] if best else tok)
        return out


vocabulary = _Vocabulary()


def _rows(result) -> list[dict]:
    return [dict(r._mapping) for r in result]


def _filter_sql(params: dict, group: str | None, noun: str | None) -> str:
    sql = ""
    if group:
        sql += " AND item_group = :group"
        params["group"] = group
    if noun:
        sql += " AND noun = :noun"
        params["noun"] = noun.upper()
    return sql


def _token_search(db: Session, toks: list[str], norm: str, group: str | None, noun: str | None, limit: int,
                  offset: int) -> list[dict]:
    params: dict = {"limit": limit, "offset": offset, "norm": norm, "window": RANK_WINDOW}
    conds = []
    for i, tok in enumerate(toks):
        # tokens under 3 characters yield no trigram unless anchored to a word start
        prefix = "% " if len(tok) < 3 else "%"
        params[f"t{i}"] = f"{prefix}{escape_like(tok)}%"
        conds.append(f"search_text LIKE :t{i}")
    filter_sql = _filter_sql(params, group, noun)
    res = db.execute(
        text(f"""SELECT {PART_COLUMNS}, similarity(search_text, :norm) AS score
                 FROM (SELECT {PART_COLUMNS}, search_text FROM parts
                       WHERE is_active AND {' AND '.join(conds)}{filter_sql}
                       LIMIT :window) hits
                 ORDER BY score DESC, length(description), item_no
                 LIMIT :limit OFFSET :offset"""),
        params,
    )
    return _rows(res)


def search_parts(db: Session, q: str, group: str | None = None, noun: str | None = None, limit: int = 20,
                 offset: int = 0) -> dict:
    started = time.perf_counter()
    q = (q or "").strip()
    items: list[dict] = []
    fuzzy = False
    corrected: str | None = None
    if not q:
        return {"items": [], "fuzzy": False, "corrected_query": None, "took_ms": 0}

    seen: set[int] = set()
    if q.isdigit() and offset == 0:
        params: dict = {"limit": limit, "prefix": escape_like(q) + "%"}
        filter_sql = _filter_sql(params, group, noun)
        res = db.execute(
            text(f"SELECT {PART_COLUMNS}, 1.0::float AS score FROM parts "
                 f"WHERE is_active AND item_no LIKE :prefix{filter_sql} ORDER BY item_no LIMIT :limit"),
            params,
        )
        items = _rows(res)
        seen = {i["id"] for i in items}

    norm, toks = query_tokens(q)
    if toks and len(items) < limit:
        avoid_seq_scan(db)
        found = [r for r in _token_search(db, toks, norm, group, noun, limit, offset) if r["id"] not in seen]

        if not found and not items and offset == 0:
            fixed = vocabulary.correct(db, toks)
            if fixed != toks:
                corrected = " ".join(fixed)
                found = _token_search(db, fixed, corrected, group, noun, limit, 0)
            if not found and len(toks) > 1:
                # one word the master lacks ("STUD M20 X 310": no 310 mm stud) should not empty the list
                for dropped in toks:
                    rest = [t for t in toks if t != dropped]
                    found = _token_search(db, rest, norm, group, noun, limit, 0)
                    if found:
                        corrected = " ".join(rest)
                        break
            if not found:
                fuzzy = True
                params = {"limit": limit, "norm": norm}
                filter_sql = _filter_sql(params, group, noun)
                res = db.execute(
                    text(f"""SELECT {PART_COLUMNS}, word_similarity(:norm, search_text) AS score
                             FROM parts
                             WHERE is_active AND :norm <% search_text{filter_sql}
                             ORDER BY score DESC, length(description), item_no
                             LIMIT :limit"""),
                    params,
                )
                found = _rows(res)
        items.extend(found[: max(0, limit - len(items))])

    for item in items:
        item["score"] = round(float(item["score"] or 0), 3)
        for col in NUMERIC_COLUMNS:
            item[col] = float(item[col]) if item[col] is not None else None
    return {
        "items": items,
        "fuzzy": fuzzy,
        "corrected_query": corrected,
        "took_ms": round((time.perf_counter() - started) * 1000, 1),
    }

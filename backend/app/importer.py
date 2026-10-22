"""Bulk, idempotent parts-master import: read file -> normalize -> COPY into staging -> upsert into parts."""
from __future__ import annotations

import json
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor

import psycopg

from app.config import get_settings
from app.normalize import extract_attrs, infer_noun, normalize
from app.tabular import cell_to_float, cell_to_str, detect_header_row, match_columns, read_rows

PART_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "item_no": ("item no", "item number", "item code", "part no", "part number", "material code", "code"),
    "description": ("item description", "description", "item name", "material description", "desc"),
    "in_stock": ("in stock", "stock", "qty in stock", "on hand"),
    "uom_group": ("uom group", "uom", "unit"),
    "item_group": ("item group", "group", "category"),
    "wtax_liable": ("wtax liable", "wtax"),
}

PARALLEL_THRESHOLD = 60_000
CHUNK_SIZE = 25_000

ProgressCb = Callable[[str, dict], None]


class PartsFileError(ValueError):
    pass


def _to_bool(value) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"yes", "y", "true", "1"}


def _prepare_chunk(rows: list[tuple]) -> list[tuple]:
    out = []
    for item_no, desc, in_stock, uom, group, wtax in rows:
        norm = normalize(desc)
        attrs = extract_attrs(norm)
        out.append((
            item_no,
            desc,
            norm,
            f" {norm} ",
            group,
            uom,
            in_stock,
            wtax,
            json.dumps(attrs, separators=(",", ":")),
            infer_noun(attrs),
        ))
    return out


def extract_part_rows(raw_rows: list[list]) -> tuple[list[tuple], int]:
    header_idx = detect_header_row(raw_rows, PART_COLUMN_ALIASES, ("item_no", "description"))
    if header_idx is None:
        raise PartsFileError("Could not find a header row with item number and description columns")
    cols = match_columns(raw_rows[header_idx], PART_COLUMN_ALIASES)

    def get(row: list, field: str):
        idx = cols.get(field)
        return row[idx] if idx is not None and idx < len(row) else None

    rows: list[tuple] = []
    skipped = 0
    for row in raw_rows[header_idx + 1:]:
        item_no = cell_to_str(get(row, "item_no"))
        desc = cell_to_str(get(row, "description"))
        if not item_no or not desc:
            skipped += 1
            continue
        rows.append((
            item_no[:50],
            desc,
            cell_to_float(get(row, "in_stock")),
            cell_to_str(get(row, "uom_group")),
            cell_to_str(get(row, "item_group")),
            _to_bool(get(row, "wtax_liable")),
        ))
    return rows, skipped


def _prepare_all(rows: list[tuple]) -> list[tuple]:
    if len(rows) < PARALLEL_THRESHOLD:
        return _prepare_chunk(rows)
    chunks = [rows[i:i + CHUNK_SIZE] for i in range(0, len(rows), CHUNK_SIZE)]
    prepared: list[tuple] = []
    with ProcessPoolExecutor() as pool:
        for part in pool.map(_prepare_chunk, chunks):
            prepared.extend(part)
    return prepared


UPSERT_SQL = """
INSERT INTO parts (item_no, description, description_norm, search_text, item_group, uom_group,
                   in_stock, wtax_liable, attrs, noun, is_active)
SELECT DISTINCT ON (item_no) item_no, description, description_norm, search_text, item_group, uom_group,
       in_stock, wtax_liable, attrs, noun, true
FROM parts_staging
ORDER BY item_no
ON CONFLICT (item_no) DO UPDATE SET
    description = EXCLUDED.description,
    description_norm = EXCLUDED.description_norm,
    search_text = EXCLUDED.search_text,
    item_group = EXCLUDED.item_group,
    uom_group = EXCLUDED.uom_group,
    in_stock = EXCLUDED.in_stock,
    wtax_liable = EXCLUDED.wtax_liable,
    attrs = EXCLUDED.attrs,
    noun = EXCLUDED.noun,
    is_active = true,
    updated_at = now()
WHERE parts.description IS DISTINCT FROM EXCLUDED.description
   OR parts.description_norm IS DISTINCT FROM EXCLUDED.description_norm
   OR parts.attrs IS DISTINCT FROM EXCLUDED.attrs
   OR parts.noun IS DISTINCT FROM EXCLUDED.noun
   OR parts.item_group IS DISTINCT FROM EXCLUDED.item_group
   OR parts.uom_group IS DISTINCT FROM EXCLUDED.uom_group
   OR parts.in_stock IS DISTINCT FROM EXCLUDED.in_stock
   OR parts.wtax_liable IS DISTINCT FROM EXCLUDED.wtax_liable
   OR NOT parts.is_active
RETURNING (xmax = 0) AS inserted
"""


def import_parts(data: bytes, filename: str, sheet: str | int | None = None,
                 progress: ProgressCb | None = None) -> dict:
    def report(stage: str, **info) -> None:
        if progress:
            progress(stage, info)

    t0 = time.perf_counter()
    report("reading")
    raw_rows = read_rows(data, filename, sheet)
    rows, skipped = extract_part_rows(raw_rows)
    del raw_rows
    t_read = time.perf_counter()

    report("normalizing", rows=len(rows))
    prepared = _prepare_all(rows)
    t_norm = time.perf_counter()

    report("loading", rows=len(prepared))
    with psycopg.connect(get_settings().psycopg_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """CREATE TEMP TABLE parts_staging (
                       item_no text, description text, description_norm text, search_text text,
                       item_group text, uom_group text, in_stock numeric, wtax_liable boolean, attrs jsonb,
                       noun text
                   ) ON COMMIT DROP"""
            )
            with cur.copy(
                "COPY parts_staging (item_no, description, description_norm, search_text, item_group, "
                "uom_group, in_stock, wtax_liable, attrs, noun) FROM STDIN"
            ) as copy:
                for row in prepared:
                    copy.write_row(row)
            report("upserting", rows=len(prepared))
            cur.execute(UPSERT_SQL)
            results = cur.fetchall()
            inserted = sum(1 for (ins,) in results if ins)
            updated = len(results) - inserted
        conn.commit()
        conn.execute("ANALYZE parts")
    t_db = time.perf_counter()

    stats = {
        "rows_in_file": len(rows),
        "skipped_rows": skipped,
        "duplicate_item_nos_in_file": len(rows) - len({r[0] for r in rows}),
        "inserted": inserted,
        "updated": updated,
        "unchanged": len({r[0] for r in rows}) - inserted - updated,
        "seconds": {
            "read": round(t_read - t0, 2),
            "normalize": round(t_norm - t_read, 2),
            "database": round(t_db - t_norm, 2),
            "total": round(t_db - t0, 2),
        },
    }
    report("done", **stats)
    return stats

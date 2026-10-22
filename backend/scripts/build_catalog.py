"""Replace the parts master with the generated Noun + Modifier catalog (app/catalog).

    python scripts/build_catalog.py --dry-run     counts per item group and noun, no database access
    python scripts/build_catalog.py --replace     back up, wipe and reload parts, rebuild indexes and
                                                  vocabulary tables, re-match every existing BOM
    python scripts/build_catalog.py --replace --no-backup     rebuild after catalog/normalize changes
    python scripts/build_catalog.py --rematch     only re-match the existing BOMs

The replace runs in one transaction: the old parts stay in place if anything fails before commit.
Old parts and BOM lines are first written to backups/*.csv. Item numbers are assigned sequentially
from 1000001 in catalog order, so each noun occupies one contiguous block.
"""
import argparse
import json
import sys
import time
from collections import Counter
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import islice
from pathlib import Path

import psycopg

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from app.catalog import iter_items, load  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.normalize import extract_attrs, normalize  # noqa: E402

FIRST_ITEM_NO = 1_000_001
CHUNK_SIZE = 20_000
COLUMNS = ("item_no, description, description_norm, search_text, item_group, uom_group, noun, modifiers, "
           "attrs, is_active")
INDEXES = {
    "ix_parts_item_no_prefix": "CREATE INDEX ix_parts_item_no_prefix ON parts (item_no text_pattern_ops)",
    "ix_parts_description_norm": "CREATE INDEX ix_parts_description_norm ON parts (description_norm)",
    "ix_parts_item_group": "CREATE INDEX ix_parts_item_group ON parts (item_group)",
    "ix_parts_noun": "CREATE INDEX ix_parts_noun ON parts (noun)",
    "ix_parts_modifiers": "CREATE INDEX ix_parts_modifiers ON parts USING gin (modifiers jsonb_path_ops)",
    "ix_parts_search_trgm": "CREATE INDEX ix_parts_search_trgm ON parts USING gin (search_text gin_trgm_ops)",
    "ix_parts_tokens": "CREATE INDEX ix_parts_tokens ON parts USING gin (string_to_array(description_norm, ' '))",
}


def _prepare_chunk(rows: list[tuple]) -> list[tuple]:
    out = []
    for item_no, desc, noun, group, uom, mods in rows:
        norm = normalize(desc)
        attrs = extract_attrs(norm)
        attrs["ptype"] = normalize(noun)
        implied = normalize(mods.get("STANDARD", "")).split()
        # a material class word (SS, CS, LTCS) is implied by the spec; a grade inside MOC ("SS 316") is not
        implied += [t for t in normalize(mods.get("MOC", "")).split() if t.isalpha()]
        if implied:
            attrs["implied"] = sorted(set(implied))
        out.append((item_no, desc, norm, f" {norm} ", group, uom, noun,
                    json.dumps(mods, separators=(",", ":")), json.dumps(attrs, separators=(",", ":")), True))
    return out


def _chunks() -> Iterator[list[tuple]]:
    items = ((str(FIRST_ITEM_NO + i), it.description, it.noun, it.item_group, it.uom, it.modifiers)
             for i, it in enumerate(iter_items()))
    while chunk := list(islice(items, CHUNK_SIZE)):
        yield chunk


def dry_run() -> None:
    t = time.perf_counter()
    by_group: Counter = Counter()
    by_noun: Counter = Counter()
    for it in iter_items():
        by_group[it.item_group] += 1
        by_noun[it.noun] += 1
    print(f"{sum(by_noun.values()):,} parts, {len(by_noun)} nouns, {len(by_group)} item groups "
          f"({time.perf_counter() - t:.1f}s)\n")
    for group, n in by_group.most_common():
        print(f"  {group:<32} {n:>9,}")
    print()
    for noun, n in by_noun.most_common():
        print(f"  {noun:<32} {n:>9,}")


def _backup(cur: psycopg.Cursor, table: str, stamp: str) -> Path:
    path = BACKEND / "backups" / f"{table}_backup_{stamp}.csv"
    path.parent.mkdir(exist_ok=True)
    with path.open("wb") as f, cur.copy(f"COPY (SELECT * FROM {table} ORDER BY id) TO STDOUT "
                                        "WITH (FORMAT csv, HEADER)") as copy:
        for data in copy:
            f.write(data)
    return path


def replace(backup: bool = True) -> None:
    started = time.perf_counter()
    nouns = load()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with psycopg.connect(get_settings().psycopg_dsn) as conn:
        with conn.cursor() as cur:
            old = cur.execute("SELECT count(*) FROM parts").fetchone()[0]
            if backup:
                for table in ("parts", "bom_lines"):
                    print(f"backed up {table} -> {_backup(cur, table, stamp)}")

            # TRUNCATE ... CASCADE would also empty bom_lines; detach the lines and delete instead
            cur.execute("UPDATE bom_lines SET matched_part_id = NULL, match_score = NULL, "
                        "match_status = 'unmatched', candidates = '[]'")
            cur.execute("DELETE FROM parts")
            cur.execute("ALTER SEQUENCE parts_id_seq RESTART WITH 1")
            for name in INDEXES:
                cur.execute(f"DROP INDEX IF EXISTS {name}")
            print(f"removed {old:,} old parts")

            t = time.perf_counter()
            loaded = 0
            # rows stay in catalog order: each noun is one contiguous block, which keeps the trigram index's
            # posting lists compact (search and matching avoid seq scans, see app.search.avoid_seq_scan)
            with cur.copy(f"COPY parts ({COLUMNS}) FROM STDIN") as copy, ProcessPoolExecutor() as pool:
                for rows in pool.map(_prepare_chunk, _chunks()):
                    for row in rows:
                        copy.write_row(row)
                    loaded += len(rows)
                    print(f"\r  loading {loaded:,} parts", end="", flush=True)
            print(f"\rloaded {loaded:,} parts in {time.perf_counter() - t:.1f}s")

            t = time.perf_counter()
            cur.execute("SET maintenance_work_mem = '1GB'")
            for name, ddl in INDEXES.items():
                cur.execute(ddl)
            print(f"built {len(INDEXES)} indexes in {time.perf_counter() - t:.1f}s")

            cur.execute("DELETE FROM nouns")
            cur.executemany(
                "INSERT INTO nouns (noun, item_group, uom, modifier_order) VALUES (%s, %s, %s, %s)",
                [(n.name, n.group, n.uom, list(n.modifiers)) for n in nouns.values()],
            )
            cur.execute("UPDATE nouns SET part_count = c.n FROM "
                        "(SELECT noun, count(*) AS n FROM parts GROUP BY noun) c WHERE nouns.noun = c.noun")
            cur.execute("""INSERT INTO noun_modifier_values (noun, modifier, value, part_count)
                           SELECT p.noun, m.key, m.value, count(*)
                           FROM parts p, jsonb_each_text(p.modifiers) m
                           GROUP BY p.noun, m.key, m.value""")
            print(f"vocabulary: {len(nouns)} nouns, {cur.rowcount:,} modifier values")
        conn.commit()
        conn.autocommit = True
        conn.execute("VACUUM ANALYZE parts")
        conn.execute("VACUUM ANALYZE bom_lines")
    print(f"replaced parts master in {time.perf_counter() - started:.1f}s")
    rematch_boms()


def rematch_boms() -> None:
    from sqlalchemy import select

    from app.bom_service import match_bom_lines, refresh_status
    from app.db import SessionLocal
    from app.models import Bom

    with SessionLocal() as db:
        boms = db.scalars(select(Bom)).unique().all()
        for bom in boms:
            if bom.lines:
                match_bom_lines(bom.lines)
            refresh_status(bom)
            print(f"  re-matched BOM {bom.id} {bom.name!r}: "
                  f"{dict(Counter(l.match_status for l in bom.lines))}")
        db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--replace", action="store_true")
    mode.add_argument("--rematch", action="store_true", help="only re-match the existing BOMs")
    parser.add_argument("--no-backup", action="store_true",
                        help="skip the CSV backup (when the current parts are a previous catalog build)")
    args = parser.parse_args()
    if args.dry_run:
        dry_run()
    elif args.replace:
        replace(backup=not args.no_backup)
    else:
        rematch_boms()

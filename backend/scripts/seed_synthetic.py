"""Fill a separate database with a scaled-up synthetic parts master for performance testing.

Copies every part of the real database once as-is plus (copies - 1) variants with their own item
numbers and a vendor "MAKE ..." suffix, so 148k real parts become ~1.5M rows with realistic text.

The target database must exist and be migrated:
    createdb -U bom bom_perf
    $env:DATABASE_URL="postgresql+psycopg://bom:bom@localhost:5432/bom_perf"; alembic upgrade head

Usage: python scripts/seed_synthetic.py postgresql://bom:bom@localhost:5432/bom_perf [--copies 10]
"""
import argparse
import sys
import time
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402

COLUMNS = "item_no, description, description_norm, search_text, item_group, uom_group, in_stock, wtax_liable, attrs"
MAKES = ["L AND T", "KSB", "AUDCO", "VIRGO", "KIRLOSKAR", "BHEL", "JINDAL", "TATA", "MAHARASHTRA SEAMLESS",
         "ISMT", "SAIL", "ESSAR", "WELSPUN", "RATNAMANI"]


def seed(target_dsn: str, copies: int) -> None:
    source_dsn = get_settings().psycopg_dsn
    started = time.perf_counter()
    with psycopg.connect(source_dsn) as src, psycopg.connect(target_dsn) as dst:
        with dst.cursor() as cur:
            cur.execute("TRUNCATE parts RESTART IDENTITY CASCADE")
            cur.execute("DROP INDEX IF EXISTS ix_parts_search_trgm")
            with src.cursor().copy(f"COPY (SELECT {COLUMNS} FROM parts) TO STDOUT") as out, \
                    cur.copy(f"COPY parts ({COLUMNS}) FROM STDIN") as inp:
                for chunk in out:
                    inp.write(chunk)
            print(f"copied real parts in {time.perf_counter() - started:.1f}s")

            t = time.perf_counter()
            cur.execute(
                f"""INSERT INTO parts ({COLUMNS})
                    SELECT 'S' || k || '-' || p.item_no,
                           p.description || ' MAKE ' || m.make,
                           p.description_norm || ' MAKE ' || m.make,
                           ' ' || p.description_norm || ' MAKE ' || m.make || ' ',
                           p.item_group, p.uom_group, p.in_stock, p.wtax_liable, p.attrs
                    FROM (SELECT * FROM parts) p
                    CROSS JOIN generate_series(1, %(n)s) AS k
                    CROSS JOIN LATERAL (SELECT (%(makes)s::text[])[1 + (k + p.id) %% %(m)s] AS make) m""",
                {"n": copies - 1, "makes": MAKES, "m": len(MAKES)},
            )
            print(f"inserted {cur.rowcount} variants in {time.perf_counter() - t:.1f}s")

            t = time.perf_counter()
            cur.execute("SET maintenance_work_mem = '512MB'")
            cur.execute("CREATE INDEX ix_parts_search_trgm ON parts USING gin (search_text gin_trgm_ops)")
            print(f"built trigram index in {time.perf_counter() - t:.1f}s")
        dst.commit()
        dst.autocommit = True
        dst.execute("VACUUM ANALYZE parts")
        total = dst.execute("SELECT count(*) FROM parts").fetchone()[0]
    print(f"done: {total} parts in {time.perf_counter() - started:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dsn")
    parser.add_argument("--copies", type=int, default=10)
    args = parser.parse_args()
    seed(args.target_dsn, args.copies)

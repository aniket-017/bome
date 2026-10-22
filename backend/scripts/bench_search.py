"""Benchmark type-ahead search latency and BOM matching speed against the configured database.

Usage: python scripts/bench_search.py [--rounds 3] [--show]
Point DATABASE_URL at another database (e.g. the synthetic bom_perf) to benchmark it instead.
"""
import argparse
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal  # noqa: E402
from app.search import search_parts  # noqa: E402
from scripts.eval_matching import evaluate  # noqa: E402

QUERIES = [
    "elbow 316l dn 100 lr", "ELBOW", "flange wnrf cl 300 dn 50", "1001", "sa-403 wp304", "stud m20 x 310",
    "gasket spw dn 150 cl 300", "pipe sa106 dn 80 sch 40", "elbo 316l dn100", "flnge wnrf 304l", "red ecc 316 dn150",
    "hex bolt 8.8 m24", "argon", "s+b+w b7 1\"", "4\" elbow sch 40", "plate 70n thk 12", "pipe smls a106 b 2\" sch 80",
    "fl", "flan", "valve", "gate valve cl 150", "nut 2h m24",
]
# keystroke-by-keystroke prefixes, as the autocomplete sends them
TYPING = ["gasket spw dn 50 cl150", "elbow 90 lr 316l sch 10s dn 80"]


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))]


def main(rounds: int, show: bool) -> None:
    db = SessionLocal()
    queries = QUERIES + [t[:i] for t in TYPING for i in range(2, len(t) + 1)]
    search_parts(db, "warm up")
    timings: list[float] = []
    slowest: dict[str, float] = {}
    for _ in range(rounds):
        for q in queries:
            t = time.perf_counter()
            r = search_parts(db, q, limit=20)
            timings.append((time.perf_counter() - t) * 1000)
            slowest[q] = max(slowest.get(q, 0), timings[-1])
            if show and _ == 0 and q in QUERIES:
                print(f"{timings[-1]:7.1f} ms fuzzy={r['fuzzy']!s:5} {q!r:30} -> "
                      f"{[i['description'] for i in r['items'][:2]]}")
    db.close()
    print(f"search: {len(timings)} queries  p50 {statistics.median(timings):.1f} ms  "
          f"p95 {percentile(timings, 95):.1f} ms  p99 {percentile(timings, 99):.1f} ms  max {max(timings):.1f} ms")
    print("slowest:", ", ".join(f"{q!r} {ms:.0f} ms" for q, ms in sorted(slowest.items(), key=lambda kv: -kv[1])[:6]))
    print("matching:", evaluate())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    main(args.rounds, args.show)

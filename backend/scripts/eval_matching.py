"""Measure matching accuracy against tests/data/messy_bom.csv.

Usage: python scripts/eval_matching.py [--show-errors]
"""
import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal  # noqa: E402
from app.matcher import match_lines  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "tests" / "data" / "messy_bom.csv"


def evaluate(show_errors: bool = False) -> dict:
    with DATA.open(encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    db = SessionLocal()
    started = time.perf_counter()
    results = match_lines(db, [(None, c["messy_description"]) for c in cases])
    elapsed = time.perf_counter() - started
    db.close()

    statuses = Counter()
    auto_correct = top1 = top5 = 0
    errors = []
    for case, res in zip(cases, results):
        statuses[res.status] += 1
        expected = case["expected_item_no"]
        cand_items = [c["item_no"] for c in res.candidates]
        best = cand_items[0] if cand_items else None
        top1 += best == expected
        top5 += expected in cand_items
        if res.status == "auto":
            if best == expected:
                auto_correct += 1
            else:
                errors.append(("WRONG AUTO", case, res))
        elif best != expected:
            errors.append((f"{res.status} top1-miss", case, res))

    n = len(cases)
    auto = statuses["auto"] + statuses["exact_desc"]
    summary = {
        "lines": n,
        "status_counts": dict(statuses),
        "auto_rate": round(auto / n, 3),
        "auto_precision": round((auto_correct + statuses["exact_desc"]) / auto, 3) if auto else None,
        "top1_accuracy": round(top1 / n, 3),
        "top5_recall": round(top5 / n, 3),
        "ms_per_line": round(elapsed * 1000 / n, 1),
    }
    if show_errors:
        for label, case, res in errors:
            print(f"\n[{label}] {case['messy_description']}\n   expected {case['expected_item_no']}  {case['source_description']}")
            for c in res.candidates[:3]:
                print(f"   {c['score']:5}  {c['item_no']}  {c['description']}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-errors", action="store_true")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.show_errors), indent=2))

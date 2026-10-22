"""Dev helper: count catalog items per noun for the given catalog modules (default: all)."""
import collections
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib  # noqa: E402

from app.catalog import NOUNS, MODULES  # noqa: E402

mods = sys.argv[1:] or list(MODULES)
t = time.time()
for m in mods:
    importlib.import_module(f"app.catalog.{m}")
total, dup, seen = 0, 0, set()
samples = collections.defaultdict(list)
rng = random.Random(1)
for n in NOUNS.values():
    c = 0
    for it in n.items():
        c += 1
        if it.description in seen:
            dup += 1
            if dup <= 5:
                print("DUP", it.description)
        seen.add(it.description)
        if rng.random() < 0.0005 or c == 1:
            samples[n.name].append(it.description)
    total += c
    print(f"{n.name:22} {n.group:24} {c:>8}")
print(f"total {total}  duplicates {dup}  {time.time() - t:.1f}s")
for k, v in samples.items():
    for d in v[:3]:
        print("   ", d)

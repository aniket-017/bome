"""Load or refresh the parts master from an Excel/CSV file.

Usage:
    python scripts/import_parts.py "d:\\MY\\424-List of Items.xlsx" [--sheet Sheet1]

Safe to re-run: existing item numbers are updated in place, new ones are inserted.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.importer import import_parts  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("--sheet", default=None, help="sheet name (default: first sheet)")
    args = parser.parse_args()

    def progress(stage: str, info: dict) -> None:
        print(f"[{stage}] {json.dumps(info) if info else ''}", flush=True)

    stats = import_parts(args.file.read_bytes(), args.file.name, args.sheet, progress=progress)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

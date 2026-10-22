"""Reading Excel/CSV files into rows, with header-row detection and column-alias mapping."""
from __future__ import annotations

import csv
import io
from pathlib import Path

from python_calamine import CalamineWorkbook

HEADER_SCAN_ROWS = 30


def _clean_header(value) -> str:
    return " ".join(str(value or "").replace("\n", " ").replace(".", " ").split()).lower()


def cell_to_str(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return repr(value)
    text = str(value).strip()
    return text or None


def cell_to_float(value) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def list_sheets(data: bytes, filename: str) -> list[str]:
    if filename.lower().endswith(".csv"):
        return ["CSV"]
    return CalamineWorkbook.from_filelike(io.BytesIO(data)).sheet_names


def read_rows(data: bytes, filename: str, sheet: str | int | None = None) -> list[list]:
    if filename.lower().endswith(".csv"):
        text = data.decode("utf-8-sig", errors="replace")
        return [row for row in csv.reader(io.StringIO(text))]
    wb = CalamineWorkbook.from_filelike(io.BytesIO(data))
    if sheet is None or sheet == "":
        ws = wb.get_sheet_by_index(0)
    elif isinstance(sheet, int):
        ws = wb.get_sheet_by_index(sheet)
    else:
        ws = wb.get_sheet_by_name(sheet)
    return ws.to_python(skip_empty_area=False)


def read_rows_from_path(path: str | Path, sheet: str | int | None = None) -> list[list]:
    path = Path(path)
    return read_rows(path.read_bytes(), path.name, sheet)


def match_columns(header: list, aliases: dict[str, tuple[str, ...]]) -> dict[str, int]:
    """Map logical field -> column index using exact alias matches first, then substring matches."""
    cleaned = [_clean_header(h) for h in header]
    mapping: dict[str, int] = {}
    used: set[int] = set()
    for exact in (True, False):
        for field, names in aliases.items():
            if field in mapping:
                continue
            for idx, h in enumerate(cleaned):
                if idx in used or not h:
                    continue
                if any(h == n if exact else (n in h) for n in names):
                    mapping[field] = idx
                    used.add(idx)
                    break
    return mapping


def detect_header_row(rows: list[list], aliases: dict[str, tuple[str, ...]], required: tuple[str, ...]) -> int | None:
    best_idx, best_hits = None, 0
    for idx, row in enumerate(rows[:HEADER_SCAN_ROWS]):
        mapping = match_columns(row, aliases)
        if not all(r in mapping for r in required):
            continue
        if len(mapping) > best_hits:
            best_idx, best_hits = idx, len(mapping)
    return best_idx

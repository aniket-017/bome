"""BOM persistence helpers shared by the Excel, manual and image entry paths."""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.matcher import MatchResult, match_lines_parallel
from app.models import Bom, BomLine, Part
from app.tabular import cell_to_float, cell_to_str, detect_header_row, match_columns

BOM_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "line_no": ("sr no", "s no", "sl no", "line no", "line", "pos", "position", "s/n", "item sr no"),
    "item_no": ("item no", "item code", "part no", "part number", "material code", "item number", "code"),
    "description": ("description", "item description", "material description", "material", "particulars",
                    "item name", "desc"),
    "qty": ("qty", "quantity", "req qty", "required qty", "total qty", "nos"),
    "uom": ("uom", "unit", "units", "u/m"),
}
FIELDS = tuple(BOM_COLUMN_ALIASES)
PREVIEW_ROWS = 15


def json_cell(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def suggest_layout(rows: list[list], header_row: int | None) -> tuple[int, dict[str, int]]:
    if header_row is None:
        header_row = detect_header_row(rows, BOM_COLUMN_ALIASES, ("description",))
    if header_row is None:
        header_row = 0
    header = rows[header_row] if header_row < len(rows) else []
    return header_row, match_columns(header, BOM_COLUMN_ALIASES)


def rows_to_lines(rows: list[list], header_row: int, mapping: dict[str, int]) -> list[dict]:
    if "description" not in mapping and "item_no" not in mapping:
        raise HTTPException(422, "Map at least the description or item number column")
    header = [cell_to_str(h) or f"Column {i + 1}" for i, h in enumerate(rows[header_row])] if rows else []

    def get(row: list, field: str):
        idx = mapping.get(field)
        return row[idx] if idx is not None and 0 <= idx < len(row) else None

    lines = []
    for row in rows[header_row + 1:]:
        desc = cell_to_str(get(row, "description"))
        item_no = cell_to_str(get(row, "item_no"))
        if not desc and not item_no:
            continue
        line_no = cell_to_float(get(row, "line_no"))
        lines.append({
            "line_no": int(line_no) if line_no is not None and line_no.is_integer() else None,
            "raw_item_no": item_no,
            "raw_description": desc,
            "qty": cell_to_float(get(row, "qty")),
            "uom": (cell_to_str(get(row, "uom")) or None),
            "extra": {"row": {header[i] if i < len(header) else f"Column {i + 1}": json_cell(v)
                              for i, v in enumerate(row) if v not in (None, "")}},
        })
    return lines


def apply_result(line: BomLine, result: MatchResult) -> None:
    line.match_status = result.status
    line.matched_part_id = result.part_id
    line.match_score = result.score
    line.candidates = result.candidates


def match_bom_lines(lines: list[BomLine]) -> None:
    results = match_lines_parallel([(l.raw_item_no, l.raw_description) for l in lines])
    for line, result in zip(lines, results):
        apply_result(line, result)


def refresh_status(bom: Bom) -> None:
    statuses = {l.match_status for l in bom.lines}
    if not bom.lines:
        bom.status = "draft"
    elif statuses & {"review", "unmatched"}:
        bom.status = "needs_review"
    else:
        bom.status = "matched"


def create_bom(db: Session, *, name: str, project: str | None, source_type: str, lines: list[dict],
               source_file: str | None = None, image_path: str | None = None, auto_match: bool = True) -> Bom:
    bom = Bom(name=name, project=project, source_type=source_type, source_file=source_file, image_path=image_path)
    used = {l["line_no"] for l in lines if l.get("line_no")}
    next_no = 1
    for data in lines:
        line_no = data.get("line_no")
        if not line_no:
            while next_no in used:
                next_no += 1
            line_no = next_no
            used.add(line_no)
        line = BomLine(
            line_no=line_no,
            raw_item_no=data.get("raw_item_no"),
            raw_description=data.get("raw_description"),
            qty=data.get("qty"),
            uom=data.get("uom"),
            extra=data.get("extra") or {},
            candidates=[],
        )
        if data.get("matched_part_id"):
            line.matched_part_id = data["matched_part_id"]
            line.match_status = "manual"
        else:
            line.match_status = "unmatched"
        bom.lines.append(line)

    to_match = [l for l in bom.lines if l.match_status != "manual"]
    if auto_match and to_match:
        match_bom_lines(to_match)
    refresh_status(bom)
    db.add(bom)
    db.commit()
    return load_bom(db, bom.id)


def load_bom(db: Session, bom_id: int) -> Bom:
    bom = db.scalar(
        select(Bom).where(Bom.id == bom_id).options(selectinload(Bom.lines).joinedload(BomLine.matched_part))
    )
    if not bom:
        raise HTTPException(404, "BOM not found")
    return bom


def bom_to_dict(bom: Bom, include_lines: bool = True) -> dict:
    counts = Counter(l.match_status for l in bom.lines)
    out = {
        "id": bom.id,
        "name": bom.name,
        "project": bom.project,
        "source_type": bom.source_type,
        "source_file": bom.source_file,
        "image_path": bom.image_path,
        "status": bom.status,
        "created_at": bom.created_at,
        "line_count": len(bom.lines),
        "status_counts": dict(counts),
    }
    if include_lines:
        out["lines"] = bom.lines
    return out


def part_exists(db: Session, part_id: int) -> Part:
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(422, f"Part {part_id} does not exist")
    return part

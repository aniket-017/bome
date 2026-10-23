"""BOM material costing: matched part x quantity x unit cost (weighted average, else standard cost)."""
from __future__ import annotations

from app.models import Bom, BomLine, Part
from app.schemas import PartOut


def unit_cost_of(part: Part) -> tuple[float | None, str | None]:
    if part.avg_cost is not None:
        return float(part.avg_cost), "avg_cost"
    if part.standard_cost is not None:
        return float(part.standard_cost), "standard_cost"
    return None, None


def cost_line(line: BomLine, batch_qty: float) -> dict:
    part = line.matched_part
    qty = float(line.qty) if line.qty is not None else None
    total_qty = qty * batch_qty if qty is not None else None
    unit_cost, source = unit_cost_of(part) if part else (None, None)
    if not part:
        issue = "unmatched"
    elif total_qty is None:
        issue = "no_qty"
    elif unit_cost is None:
        issue = "no_cost"
    else:
        issue = None
    return {
        "line_id": line.id,
        "line_no": line.line_no,
        "raw_item_no": line.raw_item_no,
        "raw_description": line.raw_description,
        "part": PartOut.model_validate(part) if part else None,
        "qty": qty,
        "total_qty": total_qty,
        "uom": line.uom or (part.uom_group if part else None),
        "unit_cost": unit_cost,
        "cost_source": source,
        "line_cost": round(total_qty * unit_cost, 2) if issue is None else None,
        "issue": issue,
    }


def cost_bom(bom: Bom, batch_qty: float = 1) -> dict:
    lines = [cost_line(l, batch_qty) for l in bom.lines]
    total = round(sum(l["line_cost"] for l in lines if l["line_cost"] is not None), 2)
    return {
        "bom_id": bom.id,
        "bom_name": bom.name,
        "project": bom.project,
        "batch_qty": batch_qty,
        "lines": lines,
        "material_cost": total,
        "unit_material_cost": round(total / batch_qty, 2),
        "line_count": len(lines),
        "costed_count": sum(1 for l in lines if l["issue"] is None),
        "unmatched_count": sum(1 for l in lines if l["issue"] == "unmatched"),
        "uncosted_count": sum(1 for l in lines if l["issue"] in ("no_cost", "no_qty")),
    }

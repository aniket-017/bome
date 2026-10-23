from decimal import Decimal

import pytest

from app.costing import cost_bom, unit_cost_of
from app.models import Bom, BomLine, Part


def _part(pid: int, avg=None, std=None) -> Part:
    return Part(id=pid, item_no=f"P{pid}", description=f"PART {pid}", uom_group="NOS",
                avg_cost=None if avg is None else Decimal(str(avg)),
                standard_cost=None if std is None else Decimal(str(std)))


def _line(lid: int, part: Part | None, qty) -> BomLine:
    return BomLine(id=lid, line_no=lid, raw_description=f"line {lid}", qty=None if qty is None else Decimal(str(qty)),
                   matched_part=part, matched_part_id=part.id if part else None)


def _bom(*lines: BomLine) -> Bom:
    bom = Bom(id=1, name="Frame", project="P-1")
    bom.lines = list(lines)
    return bom


def test_unit_cost_prefers_weighted_average():
    assert unit_cost_of(_part(1, avg=12.5, std=10)) == (12.5, "avg_cost")
    assert unit_cost_of(_part(1, std=10)) == (10.0, "standard_cost")
    assert unit_cost_of(_part(1)) == (None, None)


def test_bom_totals_and_flags():
    bom = _bom(
        _line(1, _part(1, avg=200), 4),          # 800
        _line(2, _part(2, std=1_000), 2),        # 2000
        _line(3, None, 5),                       # unmatched
        _line(4, _part(4), 1),                   # no cost
        _line(5, _part(5, std=50), None),        # no qty
    )
    c = cost_bom(bom)
    assert c["material_cost"] == 2_800
    assert c["unit_material_cost"] == 2_800
    assert (c["line_count"], c["costed_count"], c["unmatched_count"], c["uncosted_count"]) == (5, 2, 1, 2)
    assert [l["issue"] for l in c["lines"]] == [None, None, "unmatched", "no_cost", "no_qty"]
    assert all(l["line_cost"] is None for l in c["lines"][2:])
    assert c["lines"][1]["cost_source"] == "standard_cost"
    assert c["lines"][0]["uom"] == "NOS"


def test_batch_quantity_scales_quantities_and_cost():
    bom = _bom(_line(1, _part(1, std=25), 4))
    c = cost_bom(bom, batch_qty=20)
    line = c["lines"][0]
    assert line["total_qty"] == 80
    assert line["line_cost"] == pytest.approx(2_000)
    assert c["material_cost"] == pytest.approx(2_000)
    assert c["unit_material_cost"] == pytest.approx(100)

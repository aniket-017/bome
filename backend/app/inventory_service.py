"""Stock movements: GRN receipts (weighted-average costing), material requisitions and issues."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.bom_service import load_bom
from app.models import Grn, GrnLine, MaterialRequisition, MrLine, Part, StockTxn
from app.schemas import GrnCreate, IssueRequest, MrCreate, MrFromBom

QTY = Decimal("0.0001")
ZERO = Decimal(0)


def dec(value) -> Decimal:
    return Decimal(str(value)) if value is not None else ZERO


def next_doc_no(db: Session, prefix: str, sequence: str) -> str:
    n = db.execute(text(f"SELECT nextval('{sequence}')")).scalar_one()
    return f"{prefix}-{date.today().year}-{n:05d}"


def lock_parts(db: Session, part_ids: Iterable[int]) -> dict[int, Part]:
    """Row-lock the parts (in id order, so concurrent postings cannot deadlock) and check they are usable."""
    ids = sorted(set(part_ids))
    parts = {p.id: p for p in db.scalars(select(Part).where(Part.id.in_(ids)).order_by(Part.id).with_for_update())}
    missing = [i for i in ids if i not in parts]
    if missing:
        raise HTTPException(422, f"Parts {missing} do not exist")
    inactive = [p.item_no for p in parts.values() if not p.is_active]
    if inactive:
        raise HTTPException(422, f"Items {inactive} are inactive")
    return parts


def weighted_avg(stock: Decimal, avg: Decimal | None, qty: Decimal, unit_cost: Decimal) -> Decimal:
    if stock <= 0 or avg is None:
        return unit_cost
    return ((stock * avg + qty * unit_cost) / (stock + qty)).quantize(QTY)


def post_grn(db: Session, body: GrnCreate) -> Grn:
    parts = lock_parts(db, (l.part_id for l in body.lines))
    grn = Grn(grn_no=next_doc_no(db, "GRN", "grn_no_seq"), supplier=body.supplier, remarks=body.remarks,
              received_on=body.received_on or date.today())
    for i, data in enumerate(body.lines, 1):
        part = parts[data.part_id]
        qty, cost = dec(data.qty), dec(data.unit_cost)
        stock = dec(part.in_stock)
        part.avg_cost = weighted_avg(stock, None if part.avg_cost is None else dec(part.avg_cost), qty, cost)
        part.in_stock = stock + qty
        grn.lines.append(GrnLine(line_no=i, part_id=part.id, qty=qty, unit_cost=cost))
    db.add(grn)
    db.flush()
    db.add_all(StockTxn(part_id=l.part_id, txn_type="GRN", qty=l.qty, unit_cost=l.unit_cost, ref_type="GRN",
                        ref_id=grn.id) for l in grn.lines)
    db.commit()
    return load_grn(db, grn.id)


def load_grn(db: Session, grn_id: int) -> Grn:
    grn = db.scalar(select(Grn).where(Grn.id == grn_id).options(selectinload(Grn.lines)))
    if not grn:
        raise HTTPException(404, "GRN not found")
    return grn


def grn_to_dict(grn: Grn) -> dict:
    return {
        "id": grn.id, "grn_no": grn.grn_no, "supplier": grn.supplier, "received_on": grn.received_on,
        "remarks": grn.remarks, "created_at": grn.created_at, "line_count": len(grn.lines),
        "total_value": float(sum(dec(l.qty) * dec(l.unit_cost) for l in grn.lines)),
        "lines": grn.lines,
    }


def create_mr(db: Session, body: MrCreate) -> MaterialRequisition:
    ids = {l.part_id for l in body.lines}
    found = {p.id: p for p in db.scalars(select(Part).where(Part.id.in_(ids)))}
    missing = sorted(ids - set(found))
    if missing:
        raise HTTPException(422, f"Parts {missing} do not exist")
    inactive = [p.item_no for p in found.values() if not p.is_active]
    if inactive:
        raise HTTPException(422, f"Items {inactive} are inactive")
    mr = MaterialRequisition(mr_no=next_doc_no(db, "MR", "mr_no_seq"), department=body.department,
                             job_ref=body.job_ref, bom_id=body.bom_id, remarks=body.remarks, status="open")
    mr.lines = [MrLine(line_no=i, part_id=l.part_id, qty_requested=dec(l.qty_requested), qty_issued=ZERO)
                for i, l in enumerate(body.lines, 1)]
    db.add(mr)
    db.commit()
    return load_mr(db, mr.id)


def mr_from_bom(db: Session, bom_id: int, body: MrFromBom) -> MaterialRequisition:
    """One MR line per matched BOM line with a positive quantity, scaled by the batch quantity."""
    bom = load_bom(db, bom_id)
    batch = dec(body.batch_qty)
    lines = [
        {"part_id": l.matched_part_id, "qty_requested": float((dec(l.qty) * batch).quantize(QTY))}
        for l in bom.lines
        if l.matched_part_id and l.matched_part and l.matched_part.is_active and l.qty is not None and l.qty > 0
    ]
    if not lines:
        raise HTTPException(422, "The BOM has no matched lines with a quantity")
    return create_mr(db, MrCreate(
        department=body.department, job_ref=body.job_ref or bom.project or bom.name, bom_id=bom.id,
        remarks=f"From BOM {bom.name} x {body.batch_qty:g}", lines=lines,
    ))


def load_mr(db: Session, mr_id: int, lock: bool = False) -> MaterialRequisition:
    stmt = select(MaterialRequisition).where(MaterialRequisition.id == mr_id).options(
        selectinload(MaterialRequisition.lines))
    if lock:
        stmt = stmt.with_for_update(of=MaterialRequisition)
    mr = db.scalar(stmt)
    if not mr:
        raise HTTPException(404, "Material requisition not found")
    return mr


def mr_status(mr: MaterialRequisition) -> str:
    if all(dec(l.qty_issued) >= dec(l.qty_requested) for l in mr.lines):
        return "issued"
    if any(dec(l.qty_issued) > 0 for l in mr.lines):
        return "partial"
    return "open"


def mr_to_dict(mr: MaterialRequisition) -> dict:
    return {
        "id": mr.id, "mr_no": mr.mr_no, "department": mr.department, "job_ref": mr.job_ref, "bom_id": mr.bom_id,
        "status": mr.status, "remarks": mr.remarks, "created_at": mr.created_at, "line_count": len(mr.lines),
        "lines": mr.lines,
    }


def issue_mr(db: Session, mr_id: int, body: IssueRequest) -> MaterialRequisition:
    mr = load_mr(db, mr_id, lock=True)
    by_id = {l.id: l for l in mr.lines}
    if body.lines is None:
        wanted = [(l, dec(l.qty_requested) - dec(l.qty_issued)) for l in mr.lines]
        wanted = [(l, q) for l, q in wanted if q > 0]
    else:
        wanted = []
        for item in body.lines:
            line = by_id.get(item.line_id)
            if not line:
                raise HTTPException(422, f"Line {item.line_id} is not part of {mr.mr_no}")
            qty = dec(item.qty)
            outstanding = dec(line.qty_requested) - dec(line.qty_issued)
            if qty > outstanding:
                raise HTTPException(422, f"Line {line.line_no}: issuing {qty:g} exceeds the outstanding {outstanding:g}")
            wanted.append((line, qty))
    if not wanted:
        raise HTTPException(422, "Nothing outstanding to issue")

    parts = lock_parts(db, (l.part_id for l, _ in wanted))
    available = {pid: dec(p.in_stock) for pid, p in parts.items()}
    short = []
    for line, qty in wanted:
        if qty > available[line.part_id]:
            short.append(f"{parts[line.part_id].item_no} (need {qty:g}, in stock {max(available[line.part_id], ZERO):g})")
        available[line.part_id] -= qty
    if short:
        raise HTTPException(409, "Insufficient stock: " + "; ".join(short))

    for line, qty in wanted:
        part = parts[line.part_id]
        part.in_stock = dec(part.in_stock) - qty
        line.qty_issued = dec(line.qty_issued) + qty
        cost = part.avg_cost if part.avg_cost is not None else part.standard_cost
        db.add(StockTxn(part_id=part.id, txn_type="ISSUE", qty=-qty, unit_cost=cost, ref_type="MR", ref_id=mr.id))
    mr.status = mr_status(mr)
    db.commit()
    return load_mr(db, mr.id)

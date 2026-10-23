from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_db
from app.inventory_service import (
    create_mr,
    grn_to_dict,
    issue_mr,
    load_grn,
    load_mr,
    mr_from_bom,
    mr_to_dict,
    post_grn,
)
from app.models import Grn, GrnLine, MaterialRequisition, MrLine, Part, StockTxn
from app.schemas import (
    GrnCreate,
    GrnOut,
    GrnSummary,
    IssueRequest,
    LedgerEntry,
    MrCreate,
    MrFromBom,
    MrOut,
    MrSummary,
    StockResponse,
)
from app.search import NUMERIC_COLUMNS, PART_COLUMNS, search_parts

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

StockFilter = Literal["all", "in_stock", "out_of_stock"]


@router.get("/grns", response_model=list[GrnSummary])
def list_grns(db: Session = Depends(get_db)):
    totals = (
        select(GrnLine.grn_id, func.count().label("n"), func.sum(GrnLine.qty * GrnLine.unit_cost).label("value"))
        .group_by(GrnLine.grn_id)
        .subquery()
    )
    rows = db.execute(
        select(Grn, totals.c.n, totals.c.value)
        .outerjoin(totals, totals.c.grn_id == Grn.id)
        .order_by(Grn.created_at.desc(), Grn.id.desc())
        .limit(500)
    )
    return [
        {"id": g.id, "grn_no": g.grn_no, "supplier": g.supplier, "received_on": g.received_on, "remarks": g.remarks,
         "created_at": g.created_at, "line_count": n or 0, "total_value": float(value or 0)}
        for g, n, value in rows
    ]


@router.post("/grns", response_model=GrnOut, status_code=201)
def create_grn(body: GrnCreate, db: Session = Depends(get_db)):
    return grn_to_dict(post_grn(db, body))


@router.get("/grns/{grn_id}", response_model=GrnOut)
def get_grn(grn_id: int, db: Session = Depends(get_db)):
    return grn_to_dict(load_grn(db, grn_id))


@router.get("/mrs", response_model=list[MrSummary])
def list_mrs(status: Literal["open", "partial", "issued"] | None = None, db: Session = Depends(get_db)):
    counts = select(MrLine.mr_id, func.count().label("n")).group_by(MrLine.mr_id).subquery()
    stmt = (
        select(MaterialRequisition, counts.c.n)
        .outerjoin(counts, counts.c.mr_id == MaterialRequisition.id)
        .order_by(MaterialRequisition.created_at.desc(), MaterialRequisition.id.desc())
        .limit(500)
    )
    if status:
        stmt = stmt.where(MaterialRequisition.status == status)
    return [
        {"id": m.id, "mr_no": m.mr_no, "department": m.department, "job_ref": m.job_ref, "bom_id": m.bom_id,
         "status": m.status, "remarks": m.remarks, "created_at": m.created_at, "line_count": n or 0}
        for m, n in db.execute(stmt)
    ]


@router.post("/mrs", response_model=MrOut, status_code=201)
def create_requisition(body: MrCreate, db: Session = Depends(get_db)):
    return mr_to_dict(create_mr(db, body))


@router.post("/mrs/from-bom/{bom_id}", response_model=MrOut, status_code=201)
def create_requisition_from_bom(bom_id: int, body: MrFromBom | None = None, db: Session = Depends(get_db)):
    return mr_to_dict(mr_from_bom(db, bom_id, body or MrFromBom()))


@router.get("/mrs/{mr_id}", response_model=MrOut)
def get_requisition(mr_id: int, db: Session = Depends(get_db)):
    return mr_to_dict(load_mr(db, mr_id))


@router.post("/mrs/{mr_id}/issue", response_model=MrOut)
def issue_requisition(mr_id: int, body: IssueRequest | None = None, db: Session = Depends(get_db)):
    return mr_to_dict(issue_mr(db, mr_id, body or IssueRequest()))


def _stock_value(item: dict) -> float | None:
    cost = item["avg_cost"] if item["avg_cost"] is not None else item["standard_cost"]
    if item["in_stock"] is None or cost is None:
        return None
    return round(item["in_stock"] * cost, 2)


@router.get("/stock", response_model=StockResponse)
def stock(
    q: str = Query("", max_length=200),
    group: str | None = None,
    availability: StockFilter = "in_stock",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0, le=100_000),
    db: Session = Depends(get_db),
):
    """Stock on hand with its value at weighted-average (else standard) cost."""
    stock_sql = {"all": "", "in_stock": " AND in_stock > 0", "out_of_stock": " AND coalesce(in_stock, 0) <= 0"}
    if q.strip():
        items = search_parts(db, q, group=group or None, limit=limit, offset=offset)["items"]
        if availability == "in_stock":
            items = [i for i in items if (i["in_stock"] or 0) > 0]
        elif availability == "out_of_stock":
            items = [i for i in items if (i["in_stock"] or 0) <= 0]
        for item in items:
            item["stock_value"] = _stock_value(item)
        return {"items": items, "total": len(items), "total_value": round(sum(i["stock_value"] or 0 for i in items), 2)}

    params: dict = {"limit": limit, "offset": offset}
    where = "is_active" + stock_sql[availability]
    if group:
        where += " AND item_group = :group"
        params["group"] = group
    total, total_value = db.execute(
        text(f"SELECT count(*), coalesce(sum(in_stock * coalesce(avg_cost, standard_cost)), 0) FROM parts "
             f"WHERE {where}"),
        params,
    ).one()
    rows = db.execute(
        text(f"SELECT {PART_COLUMNS} FROM parts WHERE {where} ORDER BY item_no LIMIT :limit OFFSET :offset"), params
    )
    items = [dict(r._mapping) for r in rows]
    for item in items:
        for col in NUMERIC_COLUMNS:
            item[col] = float(item[col]) if item[col] is not None else None
        item["stock_value"] = _stock_value(item)
    return {"items": items, "total": total, "total_value": round(float(total_value), 2)}


@router.get("/ledger/{part_id}", response_model=list[LedgerEntry])
def ledger(part_id: int, db: Session = Depends(get_db)):
    """Stock movements of one part, newest first, with the running balance after each movement."""
    if not db.get(Part, part_id):
        raise HTTPException(404, "Part not found")
    txns = db.scalars(select(StockTxn).where(StockTxn.part_id == part_id).order_by(StockTxn.created_at, StockTxn.id)).all()
    grn_ids = {t.ref_id for t in txns if t.ref_type == "GRN"}
    mr_ids = {t.ref_id for t in txns if t.ref_type == "MR"}
    grn_nos = dict(db.execute(select(Grn.id, Grn.grn_no).where(Grn.id.in_(grn_ids))).tuples().all()) if grn_ids else {}
    mr_nos = dict(db.execute(select(MaterialRequisition.id, MaterialRequisition.mr_no)
                             .where(MaterialRequisition.id.in_(mr_ids))).tuples().all()) if mr_ids else {}
    out = []
    balance = 0.0
    for t in txns:
        balance += float(t.qty)
        ref_no = grn_nos.get(t.ref_id) if t.ref_type == "GRN" else mr_nos.get(t.ref_id) if t.ref_type == "MR" else None
        out.append({**LedgerEntry.model_validate(t).model_dump(), "ref_no": ref_no, "balance": round(balance, 4)})
    return list(reversed(out))

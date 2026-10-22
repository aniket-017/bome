import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Noun, NounModifierValue, Part
from app.schemas import GroupCount, NounDetail, NounOut, PartBrowseResponse, PartDetail, PartSearchResponse
from app.search import search_parts

router = APIRouter(prefix="/api/parts", tags=["parts"])


@router.get("/search", response_model=PartSearchResponse)
def search(
    q: str = Query("", max_length=200),
    group: str | None = None,
    noun: str | None = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=10_000),
    db: Session = Depends(get_db),
):
    return search_parts(db, q, group=group or None, noun=noun or None, limit=limit, offset=offset)


@router.get("/groups", response_model=list[GroupCount])
def groups(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Part.item_group, func.count()).where(Part.is_active).group_by(Part.item_group).order_by(func.count().desc())
    )
    return [{"item_group": g, "count": c} for g, c in rows]


@router.get("/nouns", response_model=list[NounOut])
def nouns(group: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Noun).order_by(Noun.item_group, Noun.noun)
    if group:
        stmt = stmt.where(Noun.item_group == group)
    return db.scalars(stmt).all()


@router.get("/nouns/{noun}", response_model=NounDetail)
def noun_detail(noun: str, db: Session = Depends(get_db)):
    """The noun's modifiers in their fixed description order, each with its allowed values."""
    n = db.get(Noun, noun.upper())
    if not n:
        raise HTTPException(404, "Noun not found")
    values: dict[str, list[dict]] = {m: [] for m in n.modifier_order}
    rows = db.execute(
        select(NounModifierValue.modifier, NounModifierValue.value, NounModifierValue.part_count)
        .where(NounModifierValue.noun == n.noun)
        .order_by(NounModifierValue.modifier, NounModifierValue.part_count.desc(), NounModifierValue.value)
    )
    for modifier, value, count in rows:
        values.setdefault(modifier, []).append({"value": value, "count": count})
    return {
        **NounOut.model_validate(n).model_dump(),
        "modifiers": [{"modifier": m, "values": v} for m, v in values.items() if v],
    }


@router.get("/browse", response_model=PartBrowseResponse)
def browse(
    noun: str,
    m: list[str] = Query(default=[], description="modifier filter MODIFIER=VALUE, repeatable"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0, le=100_000),
    db: Session = Depends(get_db),
):
    """Parts of one noun narrowed down by exact modifier values, e.g. noun=FLANGE&m=TYPE=WN&m=RATING=CL 300."""
    filters: dict[str, str] = {}
    for f in m:
        key, sep, value = f.partition("=")
        if not sep or not key.strip() or not value.strip():
            raise HTTPException(422, f"modifier filter must be MODIFIER=VALUE, got {f!r}")
        filters[key.strip().upper()] = value.strip()
    params = {"noun": noun.upper(), "mods": json.dumps(filters), "limit": limit, "offset": offset}
    where = "is_active AND noun = :noun AND modifiers @> CAST(:mods AS jsonb)"
    total = db.execute(text(f"SELECT count(*) FROM parts WHERE {where}"), params).scalar()
    rows = db.execute(
        text(f"""SELECT id, item_no, description, item_group, uom_group, in_stock, noun, modifiers FROM parts
                 WHERE {where} ORDER BY item_no LIMIT :limit OFFSET :offset"""),
        params,
    )
    items = [dict(r._mapping) for r in rows]
    for item in items:
        item["in_stock"] = float(item["in_stock"]) if item["in_stock"] is not None else None
    return {"items": items, "total": total}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Part))
    active = db.scalar(select(func.count()).select_from(Part).where(Part.is_active))
    return {"total": total, "active": active}


@router.get("/by-item-no/{item_no}", response_model=PartDetail)
def by_item_no(item_no: str, db: Session = Depends(get_db)):
    part = db.scalar(select(Part).where(Part.item_no == item_no))
    if not part:
        raise HTTPException(404, "Part not found")
    return part


@router.get("/{part_id}", response_model=PartDetail)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(404, "Part not found")
    return part

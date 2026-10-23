import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Noun, NounModifierValue, Part, StockTxn
from app.normalize import derive_part_fields
from app.schemas import (
    GroupCount,
    NounDetail,
    NounOut,
    PartBrowseResponse,
    PartCreate,
    PartDetail,
    PartSearchResponse,
    PartUpdate,
)
from app.search import NUMERIC_COLUMNS, PART_COLUMNS, search_parts

router = APIRouter(prefix="/api/parts", tags=["parts"])


def _clean(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _resolve_noun(db: Session, noun: str | None, modifiers: dict[str, str] | None) -> tuple[str | None, dict]:
    """Validate an explicitly chosen noun and its modifiers against the controlled vocabulary."""
    if not noun:
        if modifiers:
            raise HTTPException(422, "modifiers require a noun")
        return None, {}
    n = db.get(Noun, noun.strip().upper())
    if not n:
        raise HTTPException(422, f"Unknown noun {noun!r}")
    mods = {k.strip().upper(): v.strip() for k, v in (modifiers or {}).items() if v and v.strip()}
    unknown = sorted(set(mods) - set(n.modifier_order))
    if unknown:
        raise HTTPException(422, f"Modifiers {unknown} are not defined for noun {n.noun}")
    return n.noun, mods


def _apply_description(part: Part, description: str) -> None:
    part.description = description
    for field, value in derive_part_fields(description).items():
        setattr(part, field, value)


@router.post("", response_model=PartDetail, status_code=201)
def create_part(body: PartCreate, db: Session = Depends(get_db)):
    item_no = body.item_no.strip()
    existing = db.scalar(select(Part).where(Part.item_no == item_no))
    if existing:
        state = "" if existing.is_active else " (inactive)"
        raise HTTPException(409, f"Item number {item_no} already exists{state}")
    part = Part(
        item_no=item_no,
        item_group=_clean(body.item_group),
        uom_group=_clean(body.uom_group),
        standard_cost=body.standard_cost,
        wtax_liable=body.wtax_liable,
        is_active=True,
    )
    _apply_description(part, body.description.strip())
    if body.noun:
        part.noun, part.modifiers = _resolve_noun(db, body.noun, body.modifiers)
    else:
        part.modifiers = {}
    if body.opening_stock:
        part.in_stock = body.opening_stock
        part.avg_cost = body.standard_cost
    db.add(part)
    db.flush()
    if body.opening_stock:
        db.add(StockTxn(part_id=part.id, txn_type="OPENING", qty=body.opening_stock,
                        unit_cost=body.standard_cost, ref_type="ITEM", ref_id=part.id))
    db.commit()
    db.refresh(part)
    return part


@router.patch("/{part_id}", response_model=PartDetail)
def update_part(part_id: int, body: PartUpdate, db: Session = Depends(get_db)):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(404, "Part not found")
    changes = body.model_dump(exclude_unset=True)
    old_noun = part.noun
    if changes.get("description") and changes["description"].strip() != part.description:
        _apply_description(part, changes["description"].strip())
    for field in ("item_group", "uom_group"):
        if field in changes:
            setattr(part, field, _clean(changes[field]))
    for field in ("standard_cost", "wtax_liable"):
        if field in changes:
            setattr(part, field, changes[field])
    if changes.get("is_active") is not None:
        part.is_active = changes["is_active"]
    if "noun" in changes or changes.get("modifiers") is not None:
        noun = changes["noun"] if "noun" in changes else part.noun
        if changes.get("modifiers") is not None:
            mods = changes["modifiers"]
        else:
            mods = part.modifiers if noun == old_noun else {}
        part.noun, part.modifiers = _resolve_noun(db, noun, mods)
    elif part.noun != old_noun:
        part.modifiers = {}
    db.commit()
    db.refresh(part)
    return part


@router.delete("/{part_id}", status_code=204)
def delete_part(part_id: int, db: Session = Depends(get_db)):
    """Soft delete: BOM lines, GRNs, MRs and the stock ledger keep pointing at the part."""
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(404, "Part not found")
    part.is_active = False
    db.commit()


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
        text(f"""SELECT {PART_COLUMNS}, modifiers FROM parts
                 WHERE {where} ORDER BY item_no LIMIT :limit OFFSET :offset"""),
        params,
    )
    items = [dict(r._mapping) for r in rows]
    for item in items:
        for col in NUMERIC_COLUMNS:
            item[col] = float(item[col]) if item[col] is not None else None
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

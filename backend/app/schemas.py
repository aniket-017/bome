from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_no: str
    description: str
    item_group: str | None = None
    uom_group: str | None = None
    in_stock: float | None = None
    noun: str | None = None


class PartDetail(PartOut):
    description_norm: str
    attrs: dict
    modifiers: dict
    wtax_liable: bool | None = None
    is_active: bool


class PartWithModifiers(PartOut):
    modifiers: dict


class PartBrowseResponse(BaseModel):
    items: list[PartWithModifiers]
    total: int


class NounOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    noun: str
    item_group: str
    uom: str
    modifier_order: list[str]
    part_count: int


class ModifierValue(BaseModel):
    value: str
    count: int


class NounModifier(BaseModel):
    modifier: str
    values: list[ModifierValue]


class NounDetail(NounOut):
    modifiers: list[NounModifier]


class PartSearchItem(PartOut):
    score: float


class PartSearchResponse(BaseModel):
    items: list[PartSearchItem]
    fuzzy: bool
    corrected_query: str | None = None
    took_ms: float


class GroupCount(BaseModel):
    item_group: str | None
    count: int


class Candidate(BaseModel):
    part_id: int
    item_no: str
    description: str
    item_group: str | None = None
    score: float


class BomLineIn(BaseModel):
    line_no: int | None = None
    raw_item_no: str | None = None
    raw_description: str | None = None
    qty: float | None = None
    uom: str | None = None
    matched_part_id: int | None = None


class BomLineUpdate(BaseModel):
    raw_item_no: str | None = None
    raw_description: str | None = None
    qty: float | None = None
    uom: str | None = None
    matched_part_id: int | None = None
    clear_match: bool = False
    rematch: bool = False


class BomLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_no: int
    raw_item_no: str | None
    raw_description: str | None
    qty: float | None
    uom: str | None
    matched_part_id: int | None
    match_score: float | None
    match_status: str
    candidates: list[Candidate]
    extra: dict
    matched_part: PartOut | None


class BomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    project: str | None = None
    lines: list[BomLineIn] = []
    auto_match: bool = True


class BomSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    project: str | None
    source_type: str
    source_file: str | None
    status: str
    created_at: datetime
    line_count: int = 0
    status_counts: dict[str, int] = {}


class BomOut(BomSummary):
    image_path: str | None = None
    lines: list[BomLineOut]


class AcceptRequest(BaseModel):
    line_ids: list[int] | None = None
    min_score: float = 0


class MatchRequest(BaseModel):
    force: bool = False

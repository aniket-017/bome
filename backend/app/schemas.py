from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_no: str
    description: str
    item_group: str | None = None
    uom_group: str | None = None
    in_stock: float | None = None
    standard_cost: float | None = None
    avg_cost: float | None = None
    noun: str | None = None


class PartCreate(BaseModel):
    item_no: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    item_group: str | None = Field(None, max_length=100)
    uom_group: str | None = Field(None, max_length=50)
    standard_cost: float | None = Field(None, ge=0)
    wtax_liable: bool | None = None
    noun: str | None = Field(None, max_length=60)
    modifiers: dict[str, str] = {}
    opening_stock: float | None = Field(None, ge=0)


class PartUpdate(BaseModel):
    description: str | None = Field(None, min_length=1)
    item_group: str | None = Field(None, max_length=100)
    uom_group: str | None = Field(None, max_length=50)
    standard_cost: float | None = Field(None, ge=0)
    wtax_liable: bool | None = None
    noun: str | None = Field(None, max_length=60)
    modifiers: dict[str, str] | None = None
    is_active: bool | None = None


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


class CostingLine(BaseModel):
    line_id: int
    line_no: int
    raw_item_no: str | None
    raw_description: str | None
    part: PartOut | None
    qty: float | None
    total_qty: float | None
    uom: str | None
    unit_cost: float | None
    cost_source: str | None  # "avg_cost" | "standard_cost" | None
    line_cost: float | None
    issue: str | None  # "unmatched" | "no_qty" | "no_cost" | None


class BomCosting(BaseModel):
    bom_id: int
    bom_name: str
    project: str | None
    batch_qty: float
    lines: list[CostingLine]
    material_cost: float
    unit_material_cost: float
    line_count: int
    costed_count: int
    unmatched_count: int
    uncosted_count: int


class GrnLineIn(BaseModel):
    part_id: int
    qty: float = Field(gt=0)
    unit_cost: float = Field(ge=0)


class GrnCreate(BaseModel):
    supplier: str | None = Field(None, max_length=200)
    received_on: date | None = None
    remarks: str | None = None
    lines: list[GrnLineIn] = Field(min_length=1)


class GrnLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_no: int
    part_id: int
    qty: float
    unit_cost: float
    part: PartOut


class GrnSummary(BaseModel):
    id: int
    grn_no: str
    supplier: str | None
    received_on: date
    remarks: str | None
    created_at: datetime
    line_count: int
    total_value: float


class GrnOut(GrnSummary):
    lines: list[GrnLineOut]


class MrLineIn(BaseModel):
    part_id: int
    qty_requested: float = Field(gt=0)


class MrCreate(BaseModel):
    department: str | None = Field(None, max_length=200)
    job_ref: str | None = Field(None, max_length=200)
    bom_id: int | None = None
    remarks: str | None = None
    lines: list[MrLineIn] = Field(min_length=1)


class MrFromBom(BaseModel):
    batch_qty: float = Field(1, gt=0)
    department: str | None = Field(None, max_length=200)
    job_ref: str | None = Field(None, max_length=200)


class MrLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_no: int
    part_id: int
    qty_requested: float
    qty_issued: float
    part: PartOut


class MrSummary(BaseModel):
    id: int
    mr_no: str
    department: str | None
    job_ref: str | None
    bom_id: int | None
    status: str
    remarks: str | None
    created_at: datetime
    line_count: int


class MrOut(MrSummary):
    lines: list[MrLineOut]


class IssueLine(BaseModel):
    line_id: int
    qty: float = Field(gt=0)


class IssueRequest(BaseModel):
    """Quantities to issue per MR line; omitted means issue everything still outstanding."""

    lines: list[IssueLine] | None = None


class StockItem(PartOut):
    stock_value: float | None = None


class StockResponse(BaseModel):
    items: list[StockItem]
    total: int
    total_value: float


class LedgerEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    txn_type: str
    qty: float
    unit_cost: float | None
    ref_type: str | None
    ref_id: int | None
    ref_no: str | None = None
    balance: float | None = None
    created_at: datetime

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

MATCH_STATUSES = ("exact_item_no", "exact_desc", "auto", "review", "unmatched", "manual")
SOURCE_TYPES = ("excel", "manual", "image")


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    item_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_norm: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    # ' ' || description_norm || ' ' so whole-token LIKE patterns ('% DN100 %') work at the edges too
    search_text: Mapped[str] = mapped_column(Text, nullable=False)
    item_group: Mapped[str | None] = mapped_column(String(100), index=True)
    uom_group: Mapped[str | None] = mapped_column(String(50))
    in_stock: Mapped[float | None] = mapped_column(Numeric(18, 4))
    wtax_liable: Mapped[bool | None] = mapped_column(Boolean)
    attrs: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    noun: Mapped[str | None] = mapped_column(String(60), index=True)
    # modifier name -> value; the display order lives in Noun.modifier_order (JSONB does not keep key order)
    modifiers: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Noun(Base):
    """Approved noun of the parts master with its fixed modifier sequence."""

    __tablename__ = "nouns"

    noun: Mapped[str] = mapped_column(String(60), primary_key=True)
    item_group: Mapped[str] = mapped_column(String(100), nullable=False)
    uom: Mapped[str] = mapped_column(String(20), nullable=False)
    modifier_order: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    part_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class NounModifierValue(Base):
    """Allowed value of one modifier of one noun."""

    __tablename__ = "noun_modifier_values"

    noun: Mapped[str] = mapped_column(ForeignKey("nouns.noun", ondelete="CASCADE"), primary_key=True)
    modifier: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[str] = mapped_column(Text, primary_key=True)
    part_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class Bom(Base):
    __tablename__ = "boms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    project: Mapped[str | None] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500))
    image_path: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lines: Mapped[list["BomLine"]] = relationship(
        back_populates="bom", cascade="all, delete-orphan", order_by="BomLine.line_no"
    )


class BomLine(Base):
    __tablename__ = "bom_lines"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bom_id: Mapped[int] = mapped_column(ForeignKey("boms.id", ondelete="CASCADE"), index=True)
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_item_no: Mapped[str | None] = mapped_column(String(100))
    raw_description: Mapped[str | None] = mapped_column(Text)
    qty: Mapped[float | None] = mapped_column(Numeric(18, 4))
    uom: Mapped[str | None] = mapped_column(String(30))
    matched_part_id: Mapped[int | None] = mapped_column(ForeignKey("parts.id", ondelete="SET NULL"), index=True)
    match_score: Mapped[float | None] = mapped_column(Float)
    match_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="unmatched")
    candidates: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    bom: Mapped[Bom] = relationship(back_populates="lines")
    matched_part: Mapped[Part | None] = relationship(lazy="joined")

"""initial schema: parts, boms, bom_lines with trigram search indexes

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-06
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "parts",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("item_no", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("description_norm", sa.Text, nullable=False),
        sa.Column("search_text", sa.Text, nullable=False),
        sa.Column("item_group", sa.String(100)),
        sa.Column("uom_group", sa.String(50)),
        sa.Column("in_stock", sa.Numeric(18, 4)),
        sa.Column("wtax_liable", sa.Boolean),
        sa.Column("attrs", JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("item_no", name="uq_parts_item_no"),
    )
    op.execute("CREATE INDEX ix_parts_item_no_prefix ON parts (item_no text_pattern_ops)")
    op.create_index("ix_parts_description_norm", "parts", ["description_norm"])
    op.create_index("ix_parts_item_group", "parts", ["item_group"])
    op.execute("CREATE INDEX ix_parts_search_trgm ON parts USING gin (search_text gin_trgm_ops)")

    op.create_table(
        "boms",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("project", sa.String(200)),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("source_file", sa.String(500)),
        sa.Column("image_path", sa.String(500)),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("source_type IN ('excel','manual','image')", name="ck_boms_source_type"),
    )

    op.create_table(
        "bom_lines",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("bom_id", sa.BigInteger, sa.ForeignKey("boms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("line_no", sa.Integer, nullable=False),
        sa.Column("raw_item_no", sa.String(100)),
        sa.Column("raw_description", sa.Text),
        sa.Column("qty", sa.Numeric(18, 4)),
        sa.Column("uom", sa.String(30)),
        sa.Column("matched_part_id", sa.BigInteger, sa.ForeignKey("parts.id", ondelete="SET NULL")),
        sa.Column("match_score", sa.Float),
        sa.Column("match_status", sa.String(20), nullable=False, server_default="unmatched"),
        sa.Column("candidates", JSONB, nullable=False, server_default="[]"),
        sa.Column("extra", JSONB, nullable=False, server_default="{}"),
        sa.CheckConstraint(
            "match_status IN ('exact_item_no','exact_desc','auto','review','unmatched','manual')",
            name="ck_bom_lines_match_status",
        ),
    )
    op.create_index("ix_bom_lines_bom_id", "bom_lines", ["bom_id"])
    op.create_index("ix_bom_lines_matched_part_id", "bom_lines", ["matched_part_id"])


def downgrade() -> None:
    op.drop_table("bom_lines")
    op.drop_table("boms")
    op.drop_table("parts")

"""noun + modifier structure: parts.noun / parts.modifiers and the controlled vocabulary tables

Revision ID: 0002_noun_modifier
Revises: 0001_initial
Create Date: 2026-10-07
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision = "0002_noun_modifier"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parts", sa.Column("noun", sa.String(60)))
    op.add_column("parts", sa.Column("modifiers", JSONB, nullable=False, server_default="{}"))
    op.create_index("ix_parts_noun", "parts", ["noun"])
    op.execute("CREATE INDEX ix_parts_modifiers ON parts USING gin (modifiers jsonb_path_ops)")

    op.create_table(
        "nouns",
        sa.Column("noun", sa.String(60), primary_key=True),
        sa.Column("item_group", sa.String(100), nullable=False),
        sa.Column("uom", sa.String(20), nullable=False),
        sa.Column("modifier_order", ARRAY(sa.Text), nullable=False),
        sa.Column("part_count", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_table(
        "noun_modifier_values",
        sa.Column("noun", sa.String(60), sa.ForeignKey("nouns.noun", ondelete="CASCADE"), primary_key=True),
        sa.Column("modifier", sa.String(60), primary_key=True),
        sa.Column("value", sa.Text, primary_key=True),
        sa.Column("part_count", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("noun_modifier_values")
    op.drop_table("nouns")
    op.drop_index("ix_parts_modifiers", table_name="parts")
    op.drop_index("ix_parts_noun", table_name="parts")
    op.drop_column("parts", "modifiers")
    op.drop_column("parts", "noun")

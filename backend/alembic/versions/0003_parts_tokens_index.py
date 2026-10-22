"""word-array index for whole-word candidate retrieval in BOM matching

Revision ID: 0003_parts_tokens_index
Revises: 0002_noun_modifier
Create Date: 2026-10-07
"""
from alembic import op

revision = "0003_parts_tokens_index"
down_revision = "0002_noun_modifier"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_parts_tokens ON parts USING gin (string_to_array(description_norm, ' '))")


def downgrade() -> None:
    op.drop_index("ix_parts_tokens", table_name="parts")

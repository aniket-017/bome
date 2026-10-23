"""ERP phase 1: item costs, GRN, material requisitions and the stock ledger

Revision ID: 0004_erp_phase1
Revises: 0003_parts_tokens_index
Create Date: 2026-10-23
"""
import sqlalchemy as sa
from alembic import op

revision = "0004_erp_phase1"
down_revision = "0003_parts_tokens_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parts", sa.Column("standard_cost", sa.Numeric(18, 4)))
    op.add_column("parts", sa.Column("avg_cost", sa.Numeric(18, 4)))

    op.execute("CREATE SEQUENCE grn_no_seq")
    op.execute("CREATE SEQUENCE mr_no_seq")

    op.create_table(
        "grns",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("grn_no", sa.String(30), nullable=False, unique=True),
        sa.Column("supplier", sa.String(200)),
        sa.Column("received_on", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("remarks", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "grn_lines",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("grn_id", sa.BigInteger, sa.ForeignKey("grns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("line_no", sa.Integer, nullable=False),
        sa.Column("part_id", sa.BigInteger, sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=False),
        sa.CheckConstraint("qty > 0", name="ck_grn_lines_qty"),
        sa.CheckConstraint("unit_cost >= 0", name="ck_grn_lines_unit_cost"),
    )
    op.create_index("ix_grn_lines_grn_id", "grn_lines", ["grn_id"])
    op.create_index("ix_grn_lines_part_id", "grn_lines", ["part_id"])

    op.create_table(
        "material_requisitions",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("mr_no", sa.String(30), nullable=False, unique=True),
        sa.Column("department", sa.String(200)),
        sa.Column("job_ref", sa.String(200)),
        sa.Column("bom_id", sa.BigInteger, sa.ForeignKey("boms.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("remarks", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('open','partial','issued')", name="ck_material_requisitions_status"),
    )
    op.create_table(
        "mr_lines",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("mr_id", sa.BigInteger, sa.ForeignKey("material_requisitions.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("line_no", sa.Integer, nullable=False),
        sa.Column("part_id", sa.BigInteger, sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("qty_requested", sa.Numeric(18, 4), nullable=False),
        sa.Column("qty_issued", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.CheckConstraint("qty_requested > 0", name="ck_mr_lines_qty_requested"),
        sa.CheckConstraint("qty_issued >= 0 AND qty_issued <= qty_requested", name="ck_mr_lines_qty_issued"),
    )
    op.create_index("ix_mr_lines_mr_id", "mr_lines", ["mr_id"])
    op.create_index("ix_mr_lines_part_id", "mr_lines", ["part_id"])

    op.create_table(
        "stock_txns",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("part_id", sa.BigInteger, sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("txn_type", sa.String(20), nullable=False),
        sa.Column("qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4)),
        sa.Column("ref_type", sa.String(20)),
        sa.Column("ref_id", sa.BigInteger),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("txn_type IN ('OPENING','GRN','ISSUE')", name="ck_stock_txns_txn_type"),
    )
    op.create_index("ix_stock_txns_part_id", "stock_txns", ["part_id", "created_at"])
    op.execute("INSERT INTO stock_txns (part_id, txn_type, qty, ref_type) "
               "SELECT id, 'OPENING', in_stock, 'IMPORT' FROM parts WHERE in_stock IS NOT NULL AND in_stock <> 0")


def downgrade() -> None:
    op.drop_table("stock_txns")
    op.drop_table("mr_lines")
    op.drop_table("material_requisitions")
    op.drop_table("grn_lines")
    op.drop_table("grns")
    op.execute("DROP SEQUENCE mr_no_seq")
    op.execute("DROP SEQUENCE grn_no_seq")
    op.drop_column("parts", "avg_cost")
    op.drop_column("parts", "standard_cost")

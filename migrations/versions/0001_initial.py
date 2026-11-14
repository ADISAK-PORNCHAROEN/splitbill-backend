"""Create the group ledger schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
    )
    op.create_table(
        "memberships",
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("payer_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("group_id", "idempotency_key", name="uq_expense_group_key"),
        sa.UniqueConstraint("id", "group_id", name="uq_expense_id_group"),
        sa.ForeignKeyConstraint(
            ["group_id", "payer_id"], ["memberships.group_id", "memberships.user_id"]
        ),
        sa.CheckConstraint("amount > 0", name="ck_expense_positive"),
        sa.CheckConstraint("length(idempotency_key) > 0", name="ck_expense_key"),
    )
    op.create_table(
        "shares",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["expense_id", "group_id"], ["expenses.id", "expenses.group_id"]),
        sa.ForeignKeyConstraint(
            ["group_id", "user_id"], ["memberships.group_id", "memberships.user_id"]
        ),
        sa.UniqueConstraint("expense_id", "user_id", name="uq_share_expense_user"),
        sa.CheckConstraint("amount >= 0", name="ck_share_nonnegative"),
    )


def downgrade():
    op.drop_table("shares")
    op.drop_table("expenses")
    op.drop_table("memberships")
    op.drop_table("groups")
    op.drop_table("users")

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        UniqueConstraint("group_id", "idempotency_key", name="uq_expense_group_key"),
        UniqueConstraint("id", "group_id", name="uq_expense_id_group"),
        ForeignKeyConstraint(
            ["group_id", "payer_id"], ["memberships.group_id", "memberships.user_id"]
        ),
        CheckConstraint("amount > 0", name="ck_expense_positive"),
        CheckConstraint("length(idempotency_key) > 0", name="ck_expense_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    payer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

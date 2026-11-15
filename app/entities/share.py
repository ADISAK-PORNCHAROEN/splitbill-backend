from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class Share(Base):
    __tablename__ = "shares"
    __table_args__ = (
        ForeignKeyConstraint(["expense_id", "group_id"], ["expenses.id", "expenses.group_id"]),
        ForeignKeyConstraint(
            ["group_id", "user_id"], ["memberships.group_id", "memberships.user_id"]
        ),
        UniqueConstraint("expense_id", "user_id", name="uq_share_expense_user"),
        CheckConstraint("amount >= 0", name="ck_share_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(Integer, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

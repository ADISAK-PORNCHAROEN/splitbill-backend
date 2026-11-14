from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class Membership(Base):
    __tablename__ = "memberships"
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


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

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.entities.expense import Expense
from app.entities.share import Share
from app.entities.user import User


def insert_expense(session: Session, values: dict) -> int | None:
    statement = (
        insert(Expense)
        .values(**values)
        .on_conflict_do_nothing(constraint="uq_expense_group_key")
        .returning(Expense.id)
    )
    return session.scalar(statement)


def by_key(session: Session, group_id: int, key: str) -> Expense:
    return session.scalars(
        select(Expense).where(Expense.group_id == group_id, Expense.idempotency_key == key)
    ).one()


def by_id(session: Session, expense_id: int) -> Expense:
    return session.scalars(select(Expense).where(Expense.id == expense_id)).one()


def payer_name(session: Session, user_id: int) -> str:
    return session.scalars(select(User.username).where(User.id == user_id)).one()


def add_shares(session: Session, shares: list[Share]) -> None:
    session.add_all(shares)
    session.flush()


def active(session: Session, group_id: int) -> list[Expense]:
    return list(
        session.scalars(
            select(Expense)
            .where(Expense.group_id == group_id, Expense.deleted_at.is_(None))
            .order_by(Expense.created_at.desc(), Expense.id.desc())
        )
    )


def active_locked(session: Session, group_id: int, expense_id: int) -> Expense | None:
    return session.scalar(
        select(Expense)
        .where(Expense.group_id == group_id, Expense.id == expense_id, Expense.deleted_at.is_(None))
        .with_for_update()
    )


def shares_for(session: Session, expense_id: int) -> list[tuple[str, Decimal]]:
    return list(
        session.execute(
            select(User.username, Share.amount)
            .join(Share, Share.user_id == User.id)
            .where(Share.expense_id == expense_id)
            .order_by(Share.id)
        ).all()
    )

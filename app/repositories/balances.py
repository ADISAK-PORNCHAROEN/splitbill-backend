from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.entities.expense import Expense
from app.entities.membership import Membership
from app.entities.share import Share
from app.entities.user import User


def balance_rows(session: Session, group_id: int) -> list[tuple[str, Decimal]]:
    credits = (
        select(Expense.payer_id.label("user_id"), func.sum(Expense.amount).label("total"))
        .where(Expense.group_id == group_id, Expense.deleted_at.is_(None))
        .group_by(Expense.payer_id)
        .subquery()
    )
    debits = (
        select(Share.user_id.label("user_id"), func.sum(Share.amount).label("total"))
        .join(Expense, Expense.id == Share.expense_id)
        .where(Expense.group_id == group_id, Expense.deleted_at.is_(None))
        .group_by(Share.user_id)
        .subquery()
    )
    return list(
        session.execute(
            select(
                User.username,
                (func.coalesce(credits.c.total, 0) - func.coalesce(debits.c.total, 0)),
            )
            .join(Membership, Membership.user_id == User.id)
            .outerjoin(credits, credits.c.user_id == User.id)
            .outerjoin(debits, debits.c.user_id == User.id)
            .where(Membership.group_id == group_id)
            .order_by(User.id)
        ).all()
    )

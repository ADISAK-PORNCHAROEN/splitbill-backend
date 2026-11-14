from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.money import format_money, parse_money
from app.domain.splits import allocate
from app.domain.types import DomainError, bad_request, not_found
from app.entities.models import Expense, Share
from app.repositories import expenses, groups
from app.services.groups import authorize


def serialize(session: Session, expense: Expense) -> dict:
    payer = expenses.payer_name(session, expense.payer_id)
    return {
        "id": expense.id,
        "group_id": expense.group_id,
        "description": expense.description,
        "paid_by": payer,
        "amount": format_money(expense.amount),
        "shares": {
            name: format_money(amount) for name, amount in expenses.shares_for(session, expense.id)
        },
        "created_at": expense.created_at.isoformat(),
    }


def create(
    session: Session, actor_id: int, group_id: int, key: str | None, body: object
) -> tuple[dict, bool]:
    authorize(session, actor_id, group_id)
    if not key or not key.strip() or len(key) > 255:
        raise bad_request("Idempotency-Key is required and must be at most 255 characters")
    if not isinstance(body, dict):
        raise bad_request("Request body must be an object")
    description, paid_by = body.get("description"), body.get("paid_by")
    if not isinstance(description, str) or not description.strip() or len(description) > 500:
        raise bad_request("Description is required and must be at most 500 characters")
    try:
        description.encode("utf-8")
    except UnicodeEncodeError:
        raise bad_request("Description contains invalid characters") from None
    if "\x00" in description:
        raise bad_request("Description contains invalid characters")
    if not isinstance(paid_by, str) or not paid_by.strip():
        raise bad_request("Payer is required")
    amount = parse_money(body.get("amount"))
    shares = allocate(amount, body.get("split"))
    members = {member.username: member.id for member in groups.members(session, group_id)}
    if paid_by not in members or any(name not in members for name in shares):
        raise bad_request("Payer and participants must be group members")
    expense_id = expenses.insert_expense(
        session,
        {
            "group_id": group_id,
            "payer_id": members[paid_by],
            "description": description,
            "amount": amount,
            "idempotency_key": key,
        },
    )
    if expense_id is None:
        expense = expenses.by_key(session, group_id, key)
        result = serialize(session, expense)
        session.commit()
        return result, False
    expenses.add_shares(
        session,
        [
            Share(expense_id=expense_id, group_id=group_id, user_id=members[name], amount=value)
            for name, value in shares.items()
        ],
    )
    expense = expenses.by_id(session, expense_id)
    result = serialize(session, expense)
    session.commit()
    return result, True


def delete(session: Session, actor_id: int, group_id: int, expense_id: int) -> None:
    authorize(session, actor_id, group_id)
    expense = expenses.active_locked(session, group_id, expense_id)
    if expense is None:
        raise not_found()
    if expense.payer_id != actor_id:
        raise DomainError(403, "forbidden", "Only the payer can delete this expense")
    expense.deleted_at = datetime.now(UTC)
    session.commit()


def list_active(session: Session, actor_id: int, group_id: int) -> list[dict]:
    authorize(session, actor_id, group_id)
    return [serialize(session, expense) for expense in expenses.active(session, group_id)]


def get_balances(session: Session, actor_id: int, group_id: int) -> list[dict]:
    authorize(session, actor_id, group_id)
    return [
        {"member": username, "balance": format_money(Decimal(value))}
        for username, value in expenses.balance_rows(session, group_id)
    ]

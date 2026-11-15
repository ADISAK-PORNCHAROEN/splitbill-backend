from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.money import format_money
from app.repositories import balances as balance_repository
from app.services.groups import authorize


def get_balances(session: Session, actor_id: int, group_id: int) -> list[dict]:
    authorize(session, actor_id, group_id)
    return [
        {"member": username, "balance": format_money(Decimal(value))}
        for username, value in balance_repository.balance_rows(session, group_id)
    ]

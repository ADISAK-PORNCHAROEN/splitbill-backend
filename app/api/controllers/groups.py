from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.services import expenses, groups
from app.services.groups import identify

router = APIRouter(prefix="/groups")


@router.get("")
def list_groups(
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identify(session, x_user)
    return groups.list_for_user(session, actor.id)


@router.get("/{group_id}")
def group_detail(
    group_id: int,
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identify(session, x_user)
    return groups.detail(session, actor.id, group_id)


@router.get("/{group_id}/balances")
def group_balances(
    group_id: int,
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identify(session, x_user)
    return expenses.get_balances(session, actor.id, group_id)

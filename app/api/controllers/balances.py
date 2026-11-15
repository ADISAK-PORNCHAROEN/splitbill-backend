from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.services import balances, identity

router = APIRouter(prefix="/groups")


@router.get("/{group_id}/balances")
def group_balances(
    group_id: int,
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identity.identify(session, x_user)
    return balances.get_balances(session, actor.id, group_id)

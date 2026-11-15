from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.group import Group
from app.entities.membership import Membership
from app.entities.user import User


def groups_for_user(session: Session, user_id: int) -> list[Group]:
    return list(
        session.scalars(
            select(Group).join(Membership).where(Membership.user_id == user_id).order_by(Group.id)
        )
    )


def get_accessible_group(session: Session, user_id: int, group_id: int) -> Group | None:
    return session.scalar(
        select(Group).join(Membership).where(Group.id == group_id, Membership.user_id == user_id)
    )


def members(session: Session, group_id: int) -> list[User]:
    return list(
        session.scalars(
            select(User).join(Membership).where(Membership.group_id == group_id).order_by(User.id)
        )
    )

from sqlalchemy.orm import Session

from app.domain.types import not_found
from app.entities.group import Group
from app.repositories import groups


def authorize(session: Session, actor_id: int, group_id: int) -> Group:
    group = groups.get_accessible_group(session, actor_id, group_id)
    if group is None:
        raise not_found()
    return group


def list_for_user(session: Session, actor_id: int) -> list[dict]:
    return [
        {"id": group.id, "name": group.name} for group in groups.groups_for_user(session, actor_id)
    ]


def detail(session: Session, actor_id: int, group_id: int) -> dict:
    group = authorize(session, actor_id, group_id)
    return {
        "id": group.id,
        "name": group.name,
        "members": [member.username for member in groups.members(session, group_id)],
    }

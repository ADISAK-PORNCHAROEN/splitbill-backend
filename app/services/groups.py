from sqlalchemy.orm import Session

from app.domain.types import bad_request, not_found
from app.repositories import groups


def identify(session: Session, username: str | None):
    if not username or not username.strip():
        raise bad_request("X-User is required")
    user = groups.find_user(session, username)
    if user is None:
        raise bad_request("Unknown X-User")
    return user


def authorize(session: Session, actor_id: int, group_id: int):
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

from sqlalchemy.orm import Session

from app.domain.types import bad_request
from app.entities.user import User
from app.repositories import users


def identify(session: Session, username: str | None) -> User:
    if not username or not username.strip():
        raise bad_request("X-User is required")
    user = users.find_by_username(session, username)
    if user is None:
        raise bad_request("Unknown X-User")
    return user

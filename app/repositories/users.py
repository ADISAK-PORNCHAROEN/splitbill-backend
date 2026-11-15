from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.user import User


def find_by_username(session: Session, username: str) -> User | None:
    return session.scalar(select(User).where(User.username == username))

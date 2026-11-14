from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal
from app.entities.models import Group, Membership, User


def seed() -> None:
    with SessionLocal.begin() as session:
        for user_id, username in enumerate(("alice", "bob", "carol", "dan"), 1):
            existing_id = session.get(User, user_id)
            existing_name = session.scalar(select(User).where(User.username == username))
            if (existing_id and existing_id.username != username) or (
                existing_name and existing_name.id != user_id
            ):
                raise ValueError(f"Conflicting seed user {username}")
            session.execute(
                insert(User).values(id=user_id, username=username).on_conflict_do_nothing()
            )
        for group_id, name in ((1, "Chiang Mai trip"), (2, "Office lunch")):
            existing = session.get(Group, group_id)
            if existing and existing.name != name:
                raise ValueError(f"Conflicting seed group {group_id}")
            session.execute(insert(Group).values(id=group_id, name=name).on_conflict_do_nothing())
        for group_id, user_id in ((1, 1), (1, 2), (1, 3), (2, 2), (2, 4)):
            session.execute(
                insert(Membership)
                .values(group_id=group_id, user_id=user_id)
                .on_conflict_do_nothing()
            )
        for table in ("users", "groups"):
            session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), GREATEST((SELECT COALESCE(MAX(id), 1) FROM {table}), nextval(pg_get_serial_sequence('{table}', 'id'))))"
                )
            )


if __name__ == "__main__":
    seed()

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class Membership(Base):
    __tablename__ = "memberships"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

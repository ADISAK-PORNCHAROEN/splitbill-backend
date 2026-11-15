from app.entities.base import Base
from app.entities.expense import Expense
from app.entities.group import Group
from app.entities.membership import Membership
from app.entities.share import Share
from app.entities.user import User

MAPPED_ENTITIES = (Expense, Group, Membership, Share, User)
metadata = Base.metadata

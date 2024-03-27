from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import TIMESTAMP

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin


class Sessions(Base, MysqlPrimaryKeyMixin):
    __tablename__ = 'sessions'

    csv_file = Column(String(255))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

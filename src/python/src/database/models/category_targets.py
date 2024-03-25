from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import BOOLEAN

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin


class CategoryTargets(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin):
    __tablename__ = 'category_targets'

    url = Column("url", String(768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)
    is_tracked = Column('is_tracked', BOOLEAN, nullable=False, server_default=text("True"))

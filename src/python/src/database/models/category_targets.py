from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, TEXT, BIGINT, TIMESTAMP

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin


class CategoryTargets(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin):
    __tablename__ = 'category_targets'

    url = Column("url", String(768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)

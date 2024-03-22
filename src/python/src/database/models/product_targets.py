from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, BIGINT, TIMESTAMP, TEXT, JSON

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin


class ProductTargets(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin):
    __tablename__ = 'product_targets'

    url = Column("url", String(768), unique=True, nullable=False)
    external_id = Column('external_id', String(768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)
    category = Column('category', String(255))
    title = Column('title', String(255), unique=False, nullable=True)
    description = Column('description', TEXT())
    brand = Column('brand', String(255))
    image_url = Column('image_url', String(255))
    image_file = Column('image_file', String(255))
    additional_info = Column('additional_info', JSON)


from sqlalchemy import Column, String, text, ForeignKey
from sqlalchemy.dialects.mysql import TEXT, JSON, BOOLEAN, INTEGER, BIGINT

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin


class ProductTargets(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlExceptionMixin, MysqlTimestampsMixin):
    __tablename__ = 'product_targets'

    url = Column("url", String(768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)
    title = Column('title', String(255), unique=False, nullable=True)
    description = Column('description', TEXT())
    brand = Column('brand', String(255))
    image_url = Column('image_url', String(255))
    image_file = Column('image_file', String(255))
    additional_info = Column('additional_info', JSON)
    is_tracked = Column('is_tracked', BOOLEAN, nullable=False, server_default=text("True"))
    position = Column('position', INTEGER(unsigned=True))
    session = Column('session', BIGINT(unsigned=True), ForeignKey('sessions.id'))
    category = Column('category', String(768))

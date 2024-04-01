from sqlalchemy import Column, String, text, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL, MEDIUMINT, TIMESTAMP, BOOLEAN, INTEGER, BIGINT

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin


class ProductHistory(Base, MysqlPrimaryKeyMixin):
    __tablename__ = 'product_history'

    product_id = Column(
        'product_id', BIGINT(unsigned=True), ForeignKey('product_targets.id'), nullable=False
    )
    regular_price = Column('regular_price', DECIMAL(20, 2))
    current_price = Column('current_price', DECIMAL(20, 2))
    is_in_stock = Column('is_in_stock', BOOLEAN)
    stock = Column('stock', MEDIUMINT(unsigned=True))
    position = Column('position', INTEGER(unsigned=True))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    session = Column('session', BIGINT(unsigned=True), ForeignKey('sessions.id'))
    currency = Column('currency', String(255))
    units = Column('units', String(255))

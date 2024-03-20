from sqlalchemy import Column, String, text, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL, MEDIUMINT, TIMESTAMP, BIGINT, BOOLEAN, INTEGER

from database.models import Base


class ProductHistory(Base):
    __tablename__ = 'product_history'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    product_external_id = Column(
        'product_external_id', String(255), ForeignKey('product_targets.external_id'), nullable=False
    )
    regular_price = Column('regular_price', DECIMAL(20, 2))
    current_price = Column('current_price', DECIMAL(20, 2))
    in_stock = Column('in_stock', BOOLEAN)
    stock = Column('stock', MEDIUMINT(unsigned=True))
    position = Column('position', INTEGER(unsigned=True))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

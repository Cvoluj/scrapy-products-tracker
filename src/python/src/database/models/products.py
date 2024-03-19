from sqlalchemy import Column, String, JSON, text, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL, MEDIUMINT, TIMESTAMP, BIGINT

from database.models import Base


class Products(Base):
    __tablename__ = 'products'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    product_external_id = Column(
        'product_external_id', String(255), ForeignKey('product_targets.external_id'), nullable=False
    )
    title = Column('title', String(255), unique=False, nullable=False)
    normal_price = Column('normal_price', DECIMAL(20, 2))
    current_price = Column('current_price', DECIMAL(20, 2))
    stock = Column('stock', MEDIUMINT(unsigned=True), server_default=text("0"))
    brand = Column('brand', String(255))
    image_url = Column('image_url', String(255))
    image_file = Column('image_file', String(255))
    additional_info = Column('additional_info', JSON)
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )



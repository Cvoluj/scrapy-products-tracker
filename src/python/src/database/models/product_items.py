
from sqlalchemy import Column, String, JSON, text
from sqlalchemy.dialects.mysql import  DECIMAL, MEDIUMINT, TIMESTAMP

from database.models import Base


class ProductItems(Base):
    __tablename__ = 'product_items'

    external_id = Column('external_id', String(255), unique=True, nullable=False)
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


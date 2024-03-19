
from sqlalchemy import Column, String, JSON, text
from sqlalchemy.dialects.mysql import DECIMAL, MEDIUMINT, TIMESTAMP, BIGINT

from database.models import Base


class CategoryItems(Base):
    __tablename__ = 'category_items'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    external_id = Column('external_id', String(255), unique=True, nullable=False)
    title = Column('title', String(255), unique=False, nullable=False)
    normal_price = Column('normal_price', DECIMAL(20, 2))
    stock = Column('stock', MEDIUMINT(unsigned=True), server_default=text("0"))
    brand = Column('brand', String(255))
    image_url = Column('image_url', String(255))
    image_file = Column('image_file', String(255))
    additional_info = Column('additional_info', JSON)
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        index=True,
        unique=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

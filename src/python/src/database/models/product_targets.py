from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, BIGINT, TIMESTAMP, TEXT, JSON

from database.models import Base


class ProductTargets(Base):
    __tablename__ = 'product_targets'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    url = Column("url", String(255), unique=True, nullable=False)
    external_id = Column('external_id', String(255), unique=True, nullable=False)
    category = Column('category', String(255))
    title = Column('title', String(255), unique=False, nullable=False)
    brand = Column('brand', String(255))
    image_url = Column('image_url', String(255))
    image_file = Column('image_file', String(255))
    additional_info = Column('additional_info', JSON)
    created_at = Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),)
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        index=True,
        unique=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
    status = Column(
        "status",
        MEDIUMINT(unsigned=True),
        index=True,
        unique=False,
        nullable=False,
        server_default=text("0"),
    )
    exception = Column("exception", TEXT(), nullable=True, unique=False)

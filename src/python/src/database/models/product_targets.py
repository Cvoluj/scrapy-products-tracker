from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, BIGINT, TIMESTAMP, TEXT

from database.models import Base


class ProductTargets(Base):
    __tablename__ = 'product_targets'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    target_url = Column("target_url", String(255), unique=True, nullable=False)
    external_id = Column('external_id', String(255), unique=True, nullable=False)
    category = Column('category', String(255))
    position = Column('position', INTEGER(unsigned=True), server_defailt=text("0"))
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

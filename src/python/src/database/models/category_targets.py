from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, TEXT, BIGINT, TIMESTAMP

from database.models import Base


class CategoryTargets(Base):
    __tablename__ = 'category_targets'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    url = Column("url", String(768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)
    status = Column(
        "status",
        MEDIUMINT(unsigned=True),
        index=True,
        unique=False,
        nullable=False,
        server_default=text("0"),
    )
    exception = Column("exception", TEXT(), nullable=True, unique=False)
    created_at = Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), )
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        index=True,
        unique=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )


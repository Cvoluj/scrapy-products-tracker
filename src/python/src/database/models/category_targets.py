from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import MEDIUMINT, TEXT, BIGINT

from database.models import Base


class CategoryTargets(Base):
    __tablename__ = 'category_targets'

    id = Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    target_url = Column("target_url", String(255), unique=True, nullable=False)
    status = Column(
        "status",
        MEDIUMINT(unsigned=True),
        index=True,
        unique=False,
        nullable=False,
        server_default=text("0"),
    )
    exception = Column("exception", TEXT(), nullable=True, unique=False)

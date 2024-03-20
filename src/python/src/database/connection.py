from twisted.enterprise.adbapi import ConnectionPool
from MySQLdb.cursors import DictCursor
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor


def get_db() -> ConnectionPool:
    settings = get_project_settings()
    return ConnectionPool(
            "MySQLdb",
            host=settings.get("DB_HOST"),
            port=settings.get("DB_PORT"),
            user=settings.get("DB_USERNAME"),
            passwd=str(settings.get("DB_PASSWORD")),
            db=settings.get("DB_DATABASE"),
            cursorclass=DictCursor,
            charset="utf8mb4",
            cp_reconnect=True,
        )
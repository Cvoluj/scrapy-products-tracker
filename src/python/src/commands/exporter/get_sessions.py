from commands.base import BaseCommand
from database.connection import get_db
from database.models import Sessions
from rmq.utils.sql_expressions import compile_expression
from sqlalchemy.sql import ClauseElement
from argparse import Namespace
from sqlalchemy import select


class GetSessions(BaseCommand):
    def init(self):
        self.conn = get_db()

    def select_results(self):
        stmt = select([Sessions.id, Sessions.target])
        return stmt

    def get_interaction(self, transaction):
        """If building task requires several queries to db or single query has extreme difficulty
        then this method could be overridden.
        In this case using of self.build_task_query_stmt method is not required
        and could be overridden with pass statement"""
        stmt = self.select_results()
        if isinstance(stmt, ClauseElement):
            # parameter passing method describes here: https://peps.python.org/pep-0249/#id20
            transaction.execute(*compile_expression(stmt))
        else:
            transaction.execute(stmt)

        return transaction.fetchall()

    def execute(self, args):
        d = self.conn.runInteraction(self.get_interaction)
        return d


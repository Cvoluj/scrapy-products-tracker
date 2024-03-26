from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task
from sqlalchemy import Table, update
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes


from commands.base import BaseCommand
from database.models import CategoryTargets
from database.connection import get_db

class StartSession(BaseCommand):
    
    def init(self):
        self.days = None
        self.hours = None
        self.minutes = None
        self.csv_file = None
        self.model: Table = CategoryTargets
        self.conn = get_db()

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-d",
            "--days",
            type=int,
            dest="days",
            help="number of days",
        )
        parser.add_argument(
            "-h",
            "--hours",
            type=int,
            dest="hours",
            help="number of hours",
        )
        parser.add_argument(
            "-m",
            "--minutes",
            type=int,
            dest="minutes",
            help="number of minutes",
        )
    
    def init_days(self, opts: Namespace):
        days = getattr(opts, "days", None)
        if days is None:
            days = self.days
        self.days = days
        return days
    
    def init_hours(self, opts: Namespace):
        hours = getattr(opts, "hours", None)
        if hours is None:
            hours = self.hours
        self.hours = hours
        return hours
    
    def init_minutes(self, opts: Namespace):
        minutes = getattr(opts, "minutes", None)
        if minutes is None:
            minutes = self.minutes
        self.minutes = minutes
        return minutes
    
    def execute(self, args, opts: Namespace):
        self.init_days(opts)
        self.init_hours(opts)
        self.init_minutes(opts)        

        delay = ((self.days or 0) * 86400) + ((self.hours or 0) * 3600) + ((self.minutes or 0) * 10)

        repeat_session_task = task.LoopingCall(self.repeat_session)
        reactor.callLater(delay, repeat_session_task.start, delay)
                    
    def update_status(self):
        try:
            stmt = update(self.model).where(self.model.is_tracked == True).values(status=TaskStatusCodes.NOT_PROCESSED)
            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.loggerr.error("Error updating item: %s", e)

    def repeat_session(self):
        self.update_status()
        self.logger.info('STATUS WERE UPDATED')

    def run(self, args: list[str], opts: Namespace):
        reactor.callLater(0, self.execute, args, opts)
        reactor.run()
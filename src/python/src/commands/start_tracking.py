from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task
from sqlalchemy import update, select, desc
from sqlalchemy.dialects.mysql import Insert, insert
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes


from commands.base import BaseCommand
from database.models import *
from database.connection import get_db

class StartTracking(BaseCommand):
    """
    scrapy start_tracking --model=ProductTargets --minutes=1 --hours=1 --days=1
    """
    
    def init(self):
        self.days = None
        self.hours = None
        self.minutes = None
        self.model = None
        self.session_file = None
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
        parser.add_argument(
            "-t",
            "--model",
            type=str,
            dest="model",
            help="SQLAlchemy model name",
        )

    def init_model_name(self, opts: Namespace):
        model = getattr(opts, "model", None)
        if model is None:
            raise NotImplementedError(
                "Model name must be provided with options or override this method to return it"
            )
        model_class = globals().get(model)
        if model_class is None or not issubclass(model_class, Base):
            raise ImportError(f"Model class '{model}' not found or is not a subclass of Table")

        self.model = model_class
        return model_class
    
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
    
    def get_session(self):
        stmt = select(Sessions).order_by(desc(Sessions.id)).limit(1)
        deferred = self.conn.runQuery(*compile_expression(stmt))
        deferred.addCallback(self.handle_session_result)
        return deferred
    
    def handle_session_result(self, result):
        self.session_file = result[0].get('csv_file') if result else None

    def execute(self, args, opts: Namespace):
        self.init_days(opts)
        self.init_hours(opts)
        self.init_minutes(opts)  
        self.init_model_name(opts)      

        delay = ((self.days or 0) * 86400) + ((self.hours or 0) * 3600) + ((self.minutes or 0) * 10)

        repeat_session_task = task.LoopingCall(self.repeat_session)
        reactor.callLater(delay, repeat_session_task.start, delay)
                    
    def update_status(self):
        try:
            stmt = update(self.model).where(self.model.is_tracked == 1).values(status=TaskStatusCodes.NOT_PROCESSED)
            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.loggerr.error("Error updating item: %s", e)

    def repeat_session(self):
        d = self.get_session()
        d.addCallback(lambda _: self.update_session())
        d.addCallback(lambda _: self.update_status())

        self.logger.warning('STATUS WERE UPDATED')

    def update_session(self):
        try:
            stmt: Insert = insert(Sessions).values(csv_file=self.session_file)
            return self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.logger.error("Error inserting item: %s", e)

    def run(self, args: list[str], opts: Namespace):
        reactor.callLater(0, self.execute, args, opts)
        reactor.run()
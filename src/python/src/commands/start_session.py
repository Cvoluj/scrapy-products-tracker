from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task

from commands.base import BaseCommand
from database.models import CategoryTargets
from utils import CSVDatabase

class StartSession(BaseCommand):
    
    def init(self):
        self.days = None
        self.hours = None
        self.minutes = None
        self.csv_file = None
        self.model = CategoryTargets

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
            "-f",
            "--file",
            type=str,
            dest="csv_file",
            help="path to csv file",
        )

    def init_csv_file_name(self, opts: Namespace):
        csv_file = getattr(opts, "csv_file", None)
        if csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        self.csv_file = csv_file
        return csv_file
    
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
        self.init_csv_file_name(opts)
        self.csv_database = CSVDatabase(self.csv_file, self.model)

        delay = ((self.days or 0) * 86400) + ((self.hours or 0) * 3600) + ((self.minutes or 0) * 60)

        repeat_session_task = task.LoopingCall(self.repeat_session)
        reactor.callLater(delay, repeat_session_task.start, delay)

    def repeat_session(self):
        self.csv_database.update_from_csv()
        self.logger.info('STATUS WERE UPDATED')

    def run(self, args: list[str], opts: Namespace):
        reactor.callLater(0, self.execute, args, opts)
        reactor.run()
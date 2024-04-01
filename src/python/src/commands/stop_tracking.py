import csv
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task
from sqlalchemy import update
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes


from commands.base import BaseCommand
from database.models import *
from database.connection import get_db

class StopTracking(BaseCommand):
    """
    scrapy stop_tracking --model=ProductTargets --file=csv_file.csv
    """
    
    def init(self):
        self.model = None
        self.conn = get_db()

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-t",
            "--model",
            type=str,
            dest="model",
            help="SQLAlchemy model name",
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
    
    def execute(self, args, opts: Namespace): 
        self.init_model_name(opts)      
        self.init_csv_file_name(opts)
        with open(self.csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                self.update_tracking(row[0])
                    
    def update_tracking(self, url):
        try:
            stmt = update(self.model).where(self.model.url == url).values(is_tracked=0)
            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.loggerr.error("Error updating item: %s", e)

    def repeat_session(self):
        self.update_status()
        self.logger.warning('STATUS WERE UPDATED')

    def run(self, args: list[str], opts: Namespace):
        reactor.callLater(0, self.execute, args, opts)
        reactor.run()
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from commands.base import BaseCommand
from utils import CSVDatabase
from database.models import *
from database.connection import get_db

class InsertCSV(BaseCommand):
    """
    scrapy insert_csv --model=ProductTargets --file=csv_file.csv
    """
    
    def init(self):
        self.model = None
        self.csv_file = None
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
        self.csv_reader = CSVDatabase(self.csv_file, self.model)
        d = self.csv_reader.insert_from_csv()
        return d

    def __execute(self, args: list, opts: list) -> Deferred:
        d = self.execute(args, opts)
        d.addErrback(self.errback)
        d.addBoth(lambda _: reactor.stop())
        return d
    
    def errback(self, failure):
        self.logger.error(failure)

    def run(self, args: list[str], opts: Namespace):
        reactor.callFromThread(self.__execute, args, opts)
        reactor.run()

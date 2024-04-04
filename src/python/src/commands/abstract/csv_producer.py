import json, functools, pika
from argparse import Namespace
from sqlalchemy import Table

from commands.abstract import DomainProducer
from utils import CSVDatabase


class CSVProducer(DomainProducer):
    """
    Adjust parent class for working with CSV files, by using CSVDatabase class

    Inheriting this class require declaring sqlalchemy model and `domain_queue_map`
    """    
    model: Table = None

    def __init__(self):
        super().__init__()
        self.csv_file = None

    def add_options(self, parser):
        """
        add option to give csv file name as parameter
        """
        super().add_options(parser)
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="csv_file",
            help="path to csv file",
        )

    def init_csv_file_name(self, opts: Namespace):
        """
        initializing of `self.csv_file` variable that contains csv file name
        """
        csv_file = getattr(opts, "csv_file", None)
        if csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        self.csv_file = csv_file
        return csv_file
    
    def execute(self, _args: list[str], opts: Namespace):
        """
        initializing instance of `CSVDatabase` class, calling `CSVDatabase.insert_from_csv`
        then calling `super().execute`
        """
        self.init_csv_file_name(opts)
        if self.model is None:
            raise ValueError(
                "SQLAlchemy table model field must be provided in class"
            )
        self.csv_database = CSVDatabase(self.csv_file, self.model)
        self.csv_database.insert_from_csv()
        super().execute(_args, opts)

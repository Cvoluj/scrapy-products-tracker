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
        """
        You must init your `self.csv_file` here, 
        f. e. `from self.project_settings` 
        """
        super().__init__()
        
    
    def execute(self, _args: list[str], opts: Namespace):
        """
        initializing instance of `CSVDatabase` class, calling `CSVDatabase.insert_from_csv`
        then calling `super().execute`
        """
        if self.csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        if self.model is None:
            raise ValueError(
                "SQLAlchemy table model field must be provided in class"
            )
        self.csv_database = CSVDatabase(self.csv_file, self.model)
        self.csv_database.insert_from_csv()
        super().execute(_args, opts)

import csv
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task
from sqlalchemy import update
from rmq.utils.sql_expressions import compile_expression
from commands.base import BaseCommand
from database.models import *
from database.connection import get_db


class StopTracking(BaseCommand):
    """
    A command class for stopping tracking of items.

    Example of command line:
    scrapy stop_tracking --model=ProductTargets --file=csv_file.csv
    """

    def init(self):
        """
        Initialize the StopTracking instance.

        This method initializes instance variables and establishes a database connection.

        Returns:
            None
        """

        self.model = None
        self.conn = get_db()

    def add_options(self, parser):
        """
        Add command-line options for the StopTracking command.

        Args:
            parser (argparse.ArgumentParser): The ArgumentParser instance to which options will be added.

        Returns:
            None
        """

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
        """
        Initialize the CSV file name from the command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the CSV file name is not provided with options or overridden method.

        Returns:
            str: The CSV file name.
        """

        csv_file = getattr(opts, "csv_file", None)
        if csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        self.csv_file = csv_file
        return csv_file

    def init_model_name(self, opts: Namespace):
        """
        Initialize the model class from the command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the model name is not provided with options or overridden method.
            ImportError: If the model class is not found or is not a subclass of Table.

        Returns:
            class: The model class.
        """

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
        """
        Execute the StopTracking command.

        This method reads the CSV file and updates tracking status for each item.

        Args:
            args (list): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            None
        """

        self.init_model_name(opts)
        self.init_csv_file_name(opts)
        with open(self.csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                self.update_tracking(row[0])

    def update_tracking(self, url):
        """
        Update tracking status for an item.

        Args:
            url (str): The URL of the item to update.

        Returns:
            None
        """

        try:
            stmt = update(self.model).where(self.model.url == url).values(is_tracked=0)
            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.loggerr.error("Error updating item: %s", e)

    def repeat_session(self):
        """
        Repeat the session tracking process.

        Returns:
            None
        """

        self.update_status()
        self.logger.warning('STATUS WERE UPDATED')

    def run(self, args: list[str], opts: Namespace):
        """
        Run the StopTracking command.

        Args:
            args (list[str]): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            None
        """

        reactor.callLater(0, self.execute, args, opts)
        reactor.run()

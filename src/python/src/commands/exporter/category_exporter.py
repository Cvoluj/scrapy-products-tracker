import datetime
from os import path
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select
from commands.abstract import CSVExporter
from database.models import *


class CategoryExporter(CSVExporter):
    """
    A class for exporting category data to a CSV file.

    Example of command line:
    scrapy category_exporter --category=example.com/category

    Attributes:
        filename_prefix (str): The prefix for the CSV file name.
    """
    filename_prefix = 'category'

    def init(self):
        """
        Initialize the CategoryExporter instance.

        Returns:
            None
        """

        super().init()
        self.category = None

    def add_options(self, parser):
        """
        Add command-line options for the CategoryExporter command.

        Args:
            parser (argparse.ArgumentParser): The ArgumentParser instance to which options will be added.

        Returns:
            None
        """

        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            dest="category",
            help="Category url for select",
        )

    def init_category_url(self, opts: Namespace):
        """
        Initialize the category URL from the command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the category URL is not provided with options or overridden method.

        Returns:
            str: The category URL.
        """

        category = getattr(opts, "category", None)
        if category is None:
            raise NotImplementedError(
                "Category url must be provided with options or override this method to return it"
            )
        self.category = category
        return category

    def select_results(self):
        """
        Select results from the database for the given category.

        Returns:
            sqlalchemy.sql.selectable.Select: The select statement for fetching results.
        """

        stmt = select([ProductTargets]
        ).where(ProductTargets.category == self.category
        ).order_by(ProductTargets.position)

        return stmt

    def get_file_path(self, timestamp_format=None, prefix=None, postfix=None, extension=None):
        """
        Generate the file path for the exported CSV file.

        Args:
            timestamp_format (str, optional): The format for the timestamp. Defaults to None.
            prefix (str, optional): The prefix for the file name. Defaults to None.
            postfix (str, optional): The postfix for the file name. Defaults to None.
            extension (str, optional): The file extension. Defaults to None.

        Returns:
            str: The file path for the exported CSV file.
        """

        if timestamp_format is None:
            timestamp_format = self.file_timestamp_format
        if prefix is None:
            prefix = self.filename_prefix
        if postfix is None:
            postfix = self.filename_postfix
        if extension is None:
            extension = self.file_extension
        export_path = path.join(path.abspath(self.project_setting.get("STORAGE_PATH")), 'export')
        file_name = f'{prefix}_{datetime.datetime.now().strftime(timestamp_format)}{postfix}.{extension}'
        return path.join(export_path, file_name)

    def execute(self, args, opts: Namespace):
        """
        Execute the CategoryExporter command.

        Args:
            args (list): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            Any: The result of the execution.
        """

        self.init_category_url(opts)
        return super().execute(args, opts)

import datetime
from os import path
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select
from commands.abstract import CSVExporter
from database.models import *


class SessionExporter(CSVExporter):
    """
    A class for exporting session data to a CSV file.

    Attributes:
        filename_prefix (str): The prefix for the CSV file name.

    """

    filename_prefix = 'session'

    def init(self):
        """
        Initialize the SessionExporter instance.

        Returns:
            None
        """

        super().init()
        self.session = None

    def add_options(self, parser):
        """
        Add command-line options for the SessionExporter command.

        Args:
            parser (argparse.ArgumentParser): The ArgumentParser instance to which options will be added.

        Returns:
            None
        """

        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-s",
            "--session",
            type=int,
            dest="session",
            help="Session id for select",
        )

    def init_session_id(self, opts: Namespace):
        """
        Initialize the session ID from the command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the session ID is not provided with options or overridden method.

        Returns:
            int: The session ID.
        """

        session = getattr(opts, "session", None)
        if session is None:
            raise NotImplementedError(
                "Session id must be provided with options or override this method to return it"
            )
        self.session = session
        return session

    def select_results(self):
        """
        Select results from the database for the given session ID.

        Returns:
            sqlalchemy.sql.selectable.Select: The select statement for fetching results.
        """

        stmt = select([
                ProductTargets.url,
                ProductTargets.title,
                ProductTargets.brand,
                ProductHistory.regular_price,
                ProductHistory.current_price,
                ProductHistory.currency,
                ProductHistory.units,
                ProductHistory.is_in_stock,
                ProductHistory.stock,
                ProductTargets.additional_info,
                ProductTargets.description,
            ]).select_from(ProductHistory.__table__.join(ProductTargets)).where(ProductHistory.session == self.session)
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
        file_name = f'{prefix}_{self.session}_{datetime.datetime.now().strftime(timestamp_format)}{postfix}.{extension}'
        return path.join(export_path, file_name)

    def execute(self, args, opts: Namespace):
        """
        Execute the SessionExporter command.

        Args:
            args (list): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            Any: The result of the execution.
        """

        self.init_session_id(opts)
        return super().execute(args, opts)

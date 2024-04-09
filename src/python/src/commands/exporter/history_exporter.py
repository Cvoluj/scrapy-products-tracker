from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select
from commands.abstract import CSVExporter
from database.models import *


class HistoryExporter(CSVExporter):
    """
    A class for exporting history data of a product to a CSV file.

    Attributes:
        filename_prefix (str): The prefix for the CSV file name.

    """
    filename_prefix = 'history_'

    def init(self):
        """
        Initialize the HistoryExporter instance.

        Returns:
            None
        """

        super().init()
        self.url = None

    def add_options(self, parser):
        """
        Add command-line options for the HistoryExporter command.

        Args:
            parser (argparse.ArgumentParser): The ArgumentParser instance to which options will be added.

        Returns:
            None
        """

        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            dest="url",
            help="Url of product for select",
        )

    def init_url_name(self, opts: Namespace):
        """
        Initialize the URL of the product from the command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the URL is not provided with options or overridden method.

        Returns:
            str: The URL of the product.
        """

        url = getattr(opts, "url", None)
        if url is None:
            raise NotImplementedError(
                "Url must be provided with options or override this method to return it"
            )
        self.url = url
        return url

    def select_results(self):
        """
        Select results from the database for the given product URL.

        Returns:
            sqlalchemy.sql.selectable.Select: The select statement for fetching results.
        """

        stmt = select([
                ProductHistory.product_id.label('id'),
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
                ProductTargets.image_url,
                ProductTargets.image_file,
                ProductHistory.created_at.label('history_created_at'),
                ProductTargets.created_at.label('product_created_at')]
            ).select_from(ProductHistory.__table__.join(ProductTargets)
            ).where(ProductTargets.url == self.url
            ).order_by(ProductHistory.created_at)

        return stmt

    def execute(self, args, opts: Namespace):
        """
        Execute the HistoryExporter command.

        Args:
            args (list): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            Any: The result of the execution.
        """

        self.init_url_name(opts)
        return super().execute(args, opts)

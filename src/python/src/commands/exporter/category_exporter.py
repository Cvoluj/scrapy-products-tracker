import datetime
from os import path
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select

from commands.abstract import CSVExporter
from database.models import *

class CategoryExporter(CSVExporter):
    filename_prefix = 'category'
    def init(self):
        super().init()
        self.category = None

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            dest="category",
            help="Category url for select",
        )

    def init_category_url(self, opts: Namespace):
        category = getattr(opts, "category", None)
        if category is None:
            raise NotImplementedError(
                "Category url must be provided with options or override this method to return it"
            )
        self.category = category
        return category

    def select_results(self):
        stmt = select([ProductTargets]
        ).where(ProductTargets.category == self.category
        ).order_by(ProductTargets.position)

        return stmt

    def get_file_path(self, timestamp_format=None, prefix=None, postfix=None, extension=None):
        if timestamp_format is None:
            timestamp_format = self.file_timestamp_format
        if prefix is None:
            prefix = self.filename_prefix
        if postfix is None:
            postfix = self.filename_postfix
        if extension is None:
            extension = self.file_extension
        export_path = path.join(path.abspath('../../../../storage/'), 'export')
        file_name = f'{prefix}_{datetime.datetime.now().strftime(timestamp_format)}{postfix}.{extension}'
        return path.join(export_path, file_name)

    def execute(self, args, opts: Namespace):
        self.init_category_url(opts)
        return super().execute(args, opts)

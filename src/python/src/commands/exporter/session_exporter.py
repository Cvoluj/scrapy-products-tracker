import datetime
from os import path
from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select

from commands.abstract import CSVExporter
from database.models import *

class SessionExporter(CSVExporter):
    filename_prefix = 'session'
    def init(self):
        super().init()
        self.session = None

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-s",
            "--session",
            type=int,
            dest="session",
            help="Session id for select",
        )

    def init_session_id(self, opts: Namespace):
        session = getattr(opts, "session", None)
        if session is None:
            raise NotImplementedError(
                "Session id must be provided with options or override this method to return it"
            )
        self.session = session
        return session

    def select_results(self):
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
                ProductTargets.created_at.label('product_created_at')
            ]).select_from(ProductHistory.__table__.join(ProductTargets)).where(ProductHistory.session == self.session)
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
        export_path = path.join(path.abspath(self.project_setting.get("STORAGE_PATH")), 'export')
        file_name = f'{prefix}_{self.session}_{datetime.datetime.now().strftime(timestamp_format)}{postfix}.{extension}'
        return path.join(export_path, file_name)

    def execute(self, args, opts: Namespace):
        self.init_session_id(opts)
        return super().execute(args, opts)

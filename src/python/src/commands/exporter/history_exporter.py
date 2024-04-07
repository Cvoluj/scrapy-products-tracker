from argparse import Namespace
from scrapy.commands import ScrapyCommand
from sqlalchemy import select

from commands.abstract import CSVExporter
from database.models import *

class HistoryExporter(CSVExporter):
    filename_prefix = 'history_'
    def init(self):
        super().init()
        self.url = None

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            dest="url",
            help="Url of product for select",
        )

    def init_url_name(self, opts: Namespace):
        url = getattr(opts, "url", None)
        if url is None:
            raise NotImplementedError(
                "Url must be provided with options or override this method to return it"
            )
        self.url = url
        return url
    
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
                ProductTargets.created_at.label('product_created_at')]
            ).select_from(ProductHistory.__table__.join(ProductTargets)
            ).where(ProductTargets.url == self.url
            ).order_by(ProductHistory.created_at)
            
        return stmt

    def execute(self, args, opts: Namespace):
        self.init_url_name(opts)
        return super().execute(args, opts)
from sqlalchemy.dialects.mysql import insert
from furl import furl

from rmq.commands import Consumer
from rmq.utils import TaskStatusCodes
from database.models import ProductTargets


class CategoryResultConsumer(Consumer):
    """
    Example of calling this command:
    scrapy category_result_consumer -m worker
    """
    def __init__(self):
        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")

    def build_message_store_stmt(self, message_body):
        url = message_body.get('url')
        product_targets_stmt = insert(ProductTargets).values(
            url=url,
            domain=furl(url).netloc
            # position=message_body.get('position'),
            # session=message_body.get('session'),
        ).on_duplicate_key_update(
            status=TaskStatusCodes.NOT_PROCESSED.value
            # position=message_body.get('position'),
            # session=message_body.get('session'),
        )

        return product_targets_stmt


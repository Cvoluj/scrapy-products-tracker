from sqlalchemy.dialects.mysql import insert
from furl import furl

from rmq.commands import Consumer
from rmq.utils import TaskStatusCodes
from database.models import ProductTargets


class FromCategoryResultConsumer(Consumer):
    def __init__(self):
        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")

    def build_message_store_stmt(self, message_body):
        url = message_body.get('url')
        product_targets_stmt = insert(ProductTargets).values(
            # position=message_body.get('position'),
            url=url,
            external_id=url,
            domain=furl(url).netloc
        ).on_duplicate_key_update(
            status=TaskStatusCodes.NOT_PROCESSED.value
        )

        return product_targets_stmt


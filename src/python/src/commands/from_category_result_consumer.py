from sqlalchemy.dialects.mysql import insert

from rmq.commands import Consumer
from rmq.utils import TaskStatusCodes
from database.models import ProductTargets


class FromCategoryResultConsumer(Consumer):
    def __init__(self):
        super().__init__()
        self.queue_name = 'from_category_result_queue'

    def build_message_store_stmt(self, message_body):
        product_targets_stmt = insert(ProductTargets).values(
            # position=message_body.get('position'),
            url=message_body.get('url'),
            external_id=message_body.get('url'),
        ).on_duplicate_key_update(
            status=TaskStatusCodes.NOT_PROCESSED.value
        )

        return product_targets_stmt


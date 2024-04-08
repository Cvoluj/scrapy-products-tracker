from sqlalchemy.dialects.mysql import insert
from furl import furl
from rmq.commands import Consumer
from rmq.utils import TaskStatusCodes
from database.models import ProductTargets


class CategoryResultConsumer(Consumer):
    """
    A consumer class for processing messages related to category results.

    Example of calling this command:
    scrapy category_result_consumer -m worker
    """
    def __init__(self):
        """
        Initialize the CategoryResultConsumer.

        This sets the queue_name attribute using project_settings.

        Returns:
            None
        """

        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")

    def build_message_store_stmt(self, message_body):
        """
        Build an SQLAlchemy insert statement for storing message data.

        Args:
            message_body (dict): The body of the message containing 'url', 'position', 'session', and 'category'.

        Returns:
            sqlalchemy.sql.dml.Insert: The SQLAlchemy insert statement.
        """

        url = message_body.get('url')
        product_targets_stmt = insert(ProductTargets).values(
            url=url,
            domain=furl(url).netloc,
            position=message_body.get('position'),
            session=message_body.get('session'),
            category=message_body.get('category')
        ).on_duplicate_key_update(
            status=TaskStatusCodes.NOT_PROCESSED.value,
            position=message_body.get('position'),
            session=message_body.get('session'),
        )

        return product_targets_stmt


from sqlalchemy.sql import update, ClauseElement
from rmq.commands import Consumer
from database.models import ProductTargets
from rmq.utils.sql_expressions import compile_expression


class ProductReplyConsumer(Consumer):
    """
    A consumer class for processing messages related to product replies.

    Example of calling this command:
    scrapy product_reply_consumer -m worker
    """
    def __init__(self):
        """
        Initialize the ProductReplyConsumer.

        This sets the queue_name attribute using project_settings.

        Returns:
            None
        """

        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")

    def process_message(self, transaction, message_body):
        """
        Process a message received from the queue.

        Args:
            transaction: A database transaction object.
            message_body (dict): The body of the message containing 'id' and 'status'.

        Returns:
            bool: True.
        """

        stmt = (update(ProductTargets)
                .where(ProductTargets.id == message_body.get('id'))
                .values(status=message_body.get('status')))

        if isinstance(stmt, ClauseElement):
            transaction.execute(*compile_expression(stmt))
        else:
            transaction.execute(stmt)
        return True

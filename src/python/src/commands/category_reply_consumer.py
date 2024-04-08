from sqlalchemy.sql import update, ClauseElement
from rmq.commands import Consumer
from database.models import CategoryTargets
from rmq.utils.sql_expressions import compile_expression


class CategoryReplyConsumer(Consumer):
    """
    A consumer class for processing messages related to category replies.

    Example of calling this command:
    scrapy category_reply_consumer -m worker
    """
    def __init__(self):
        """
        Initialize the CategoryReplyConsumer.

        This sets the queue_name attribute using project_settings.

        Returns:
            None
        """

        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")

    def process_message(self, transaction, message_body):
        """
        Process a message received from the queue.

        Args:
            transaction: A database transaction object.
            message_body (dict): The body of the message containing 'id' and 'status'.

        Returns:
            bool: True.
        """

        stmt = (update(CategoryTargets)
                .where(CategoryTargets.id == message_body.get('id'))
                .values(status=message_body.get('status')))

        if isinstance(stmt, ClauseElement):
            transaction.execute(*compile_expression(stmt))
        else:
            transaction.execute(stmt)
        return True

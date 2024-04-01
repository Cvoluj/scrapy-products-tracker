from sqlalchemy.sql import update, ClauseElement

from rmq.commands import Consumer
from database.models import CategoryTargets
from rmq.utils.sql_expressions import compile_expression


class CategoryReplyConsumer(Consumer):
    """
    Example of calling this command:
    scrapy category_reply_consumer -m worker
    """
    def __init__(self):
        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")

    def process_message(self, transaction, message_body):
        stmt = (update(CategoryTargets)
                .where(CategoryTargets.id == message_body.get('id'))
                .values(status=message_body.get('status')))

        if isinstance(stmt, ClauseElement):
            transaction.execute(*compile_expression(stmt))
        else:
            transaction.execute(stmt)
        return True

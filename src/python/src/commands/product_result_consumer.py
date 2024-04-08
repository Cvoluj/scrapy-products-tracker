from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import select
from rmq.commands import Consumer
from database.models import ProductTargets, ProductHistory
from rmq.utils.sql_expressions import compile_expression


class ProductResultConsumer(Consumer):
    """
    A consumer class for processing messages related to product results.

    Example of calling this command:
    scrapy product_result_consumer --mode=worker
    """

    def __init__(self):
        """
        Initialize the ProductResultConsumer.

        This sets the queue_name attribute using project_settings.

        Returns:
            None
        """

        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")

    def build_message_store_stmt(self, message_body):
        """
        Build SQLAlchemy insert statements for storing message data.

        Args:
            message_body (dict): The body of the message containing product details.

        Returns:
            tuple: A tuple containing SQLAlchemy insert statements.
        """

        product_target_stmt = insert(ProductTargets).values(
            url=message_body.get('url'),
            title=message_body.get('title'),
            description=message_body.get('description'),
            brand=message_body.get('brand'),
            image_url=message_body.get('image_url'),
            image_file=message_body.get('image_file'),
            additional_info=message_body.get('additional_info')
        ).on_duplicate_key_update(
            title=message_body.get('title'),
            description=message_body.get('description'),
            brand=message_body.get('brand'),
            image_url=message_body.get('image_url'),
            image_file=message_body.get('image_file'),
            additional_info=message_body.get('additional_info'),
            session=message_body.get('session')
        )
        id_select_stmt = select(ProductTargets.id).where(ProductTargets.url == message_body.get('url'))
        product_history_stmt = insert(ProductHistory).values(
            product_id=None,
            regular_price=message_body.get('regular_price'),
            current_price=message_body.get('current_price'),
            is_in_stock=message_body.get('is_in_stock'),
            stock=message_body.get('stock'),
            position=message_body.get('position'),
            session=message_body.get('session'),
            currency=message_body.get('currency'),
            units=message_body.get('units')
        )

        return product_target_stmt, id_select_stmt, product_history_stmt

    def process_message(self, transaction, message_body):
        """
        Process a message received from the queue.

        Args:
            transaction: A database transaction object.
            message_body (dict): The body of the message containing product details.

        Returns:
            bool: True.
        """

        product_target_stmt, id_select_stmt, product_history_stmt = self.build_message_store_stmt(message_body)

        transaction.execute(*compile_expression(product_target_stmt))

        transaction.execute(*compile_expression(id_select_stmt))
        result = transaction.fetchone()
        product_history_stmt = product_history_stmt.values(product_id=result.get('id'))

        transaction.execute(*compile_expression(product_history_stmt))

        return True




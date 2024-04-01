import json, pika, functools
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import select, func
from twisted.internet import defer
from sqlalchemy.sql import ClauseElement
from rmq.commands import Consumer
from database.models import ProductTargets, ProductHistory
from rmq.utils import TaskStatusCodes
from rmq.utils.decorators import call_once
from rmq.utils.sql_expressions import compile_expression
import logging


class ResultConsumer(Consumer):
    def __init__(self):
        super().__init__()
        self.queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")
        self.logger = logging.getLogger(__name__)

    def build_message_store_stmt(self, message_body):
        product_target_stmt = insert(ProductTargets).values(
            url=message_body.get('url'),
            title=message_body.get('title'),
            description=message_body.get('description'),
            brand=message_body.get('brand'),
            image_url=message_body.get('image_url'),
            image_file=message_body.get('image_file'),
            additional_info=json.dumps(message_body.get('additional_info')),
            status=TaskStatusCodes.SUCCESS.value
        ).on_duplicate_key_update(
            title=message_body.get('title'),
            description=message_body.get('description'),
            brand=message_body.get('brand'),
            image_url=message_body.get('image_url'),
            image_file=message_body.get('image_file'),
            additional_info=json.dumps(message_body.get('additional_info')),
            status=TaskStatusCodes.SUCCESS.value
        )

        product_history_stmt = insert(ProductHistory).values(
            product_id=None,
            regular_price=message_body.get('regular_price'),
            current_price=message_body.get('current_price'),
            is_in_stock=message_body.get('is_in_stock'),
            stock=message_body.get('stock'),
            position=message_body.get('position'),
        )

        return product_target_stmt, product_history_stmt

    def process_message(self, transaction, message_body):
        product_target_stmt, product_history_stmt = self.build_message_store_stmt(message_body)

        transaction.execute(*compile_expression(product_target_stmt))

        select_stmt = select(ProductTargets.id).where(ProductTargets.url == message_body.get('url'))
        if isinstance(select_stmt, ClauseElement):
            transaction.execute(*compile_expression(select_stmt))
        else:
            transaction.execute(select_stmt)
        result = transaction.fetchone()
        self.logger.debug(result)
        product_history_stmt = product_history_stmt.values(product_id=result.get('id'))
        transaction.execute(*compile_expression(product_history_stmt))

        return True




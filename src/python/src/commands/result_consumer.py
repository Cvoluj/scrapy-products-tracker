import json, pika, functools
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import select, desc

from database.models import ProductTargets, ProductHistory, Sessions
from rmq.utils import TaskStatusCodes
from rmq.utils.decorators import call_once
from rmq.utils.sql_expressions import compile_expression
from rmq.commands import Consumer


class ResultConsumer(Consumer):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")

    def get_session(self):
        stmt = select(Sessions).order_by(desc(Sessions.id)).limit(1)
        deferred = self.db_connection_pool.runQuery(*compile_expression(stmt))
        deferred.addCallback(self.handle_session_result)
        return deferred

    def handle_session_result(self, result):
        self.session_id = result[0]['id'] if result else None

    def build_message_store_stmt(self, message_body):
        product_target_stmt = insert(ProductTargets).values(
            external_id=message_body.get('url'),
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
            product_external_id=message_body.get('url'),
            regular_price=message_body.get('regular_price'),
            current_price=message_body.get('current_price'),
            is_in_stock=message_body.get('is_in_stock'),
            stock=message_body.get('stock'),
            position=message_body.get('position'),
            session=self.session_id
        )

        return product_target_stmt, product_history_stmt

    def process_message(self, transaction, message_body):
        product_target_stmt, product_history_stmt = self.build_message_store_stmt(message_body)

        transaction.execute(*compile_expression(product_target_stmt))

        transaction.execute(*compile_expression(product_history_stmt))

        return True

    def on_basic_get_message(self, message):
        delivery_tag = message.get("method").delivery_tag
        ack_cb = nack_cb = None
        if isinstance(self.rmq_connection.connection, pika.SelectConnection):
            ack_cb = call_once(
                functools.partial(
                    self.rmq_connection.connection.ioloop.add_callback_threadsafe,
                    functools.partial(
                        self.rmq_connection.acknowledge_message, delivery_tag=delivery_tag
                    ),
                )
            )
            nack_cb = call_once(
                functools.partial(
                    self.rmq_connection.connection.ioloop.add_callback_threadsafe,
                    functools.partial(
                        self.rmq_connection.negative_acknowledge_message, delivery_tag=delivery_tag
                    ),
                )
            )

        message_body = json.loads(message["body"])

        d = self.get_session()
        d.addCallback(lambda _: self.db_connection_pool.runInteraction(self.process_message, message_body))
        d.addCallback(
            self.on_message_processed, ack_callback=ack_cb, nack_callback=nack_cb,
        ).addErrback(self.on_message_process_failure, nack_callback=nack_cb).addBoth(
            self._check_mode
        )

        self._can_get_next_message = True

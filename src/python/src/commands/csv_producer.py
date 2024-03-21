import json, functools, pika
from argparse import Namespace
from sqlalchemy import Table

from rmq.commands import Producer
from utils import CSVDatabase, parse_domain


class CSVProducer(Producer):
    """
    Inheriting this class require declaring sqlalcemy model and mapping for domain: queue
    Example:
    >>> model = <SQLAlchemyModel>
    >>> domain_queue_map = { 
        "www.zoro.com": "zoro_task",
        "chat.openai.com": "chat_task"
    }
    """
    model: Table = None
    domain_queue_map = {

    }
    unmapped_domain_queue = 'unmapped_domain'
    def __init__(self):
        super().__init__()
        self.csv_file = None

    def add_options(self, parser):
        super().add_options(parser)
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="csv_file",
            help="path to csv file",
        )

    def init_csv_file_name(self, opts: Namespace):
        csv_file = getattr(opts, "csv_file", None)
        if csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        self.csv_file = csv_file
        return csv_file
    
    def init_task_queue_name(self, opts: Namespace):
        task_queue_name = getattr(opts, "task_queue_name", None)
        self.task_queue_name = self.unmapped_domain_queue
        if task_queue_name:
            self.task_queue_name = task_queue_name
        return task_queue_name
    
    def execute(self, _args: list[str], opts: Namespace):
        self.init_csv_file_name(opts)
        self.csv_database = CSVDatabase(self.csv_file, self.model)
        self.csv_database.read_csv_and_insert()
        super().execute(_args, opts)
    
    def get_queue_name(self, msg_body):
        return self.domain_queue_map.get(parse_domain(msg_body.get("url")), self.task_queue_name)

    def _send_message(self, msg_body):
        if not isinstance(msg_body, dict):
            raise ValueError("Built message body is not a dictionary")
        msg_body = self._convert_unserializable_values(msg_body)
        cb = functools.partial(
            self.rmq_connection.publish_message,
            message=json.dumps(msg_body),
            queue_name=self.get_queue_name(msg_body), 
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=2, reply_to=self.reply_to_queue_name
            ),
        )
        self.rmq_connection.connection.ioloop.add_callback_threadsafe(cb)
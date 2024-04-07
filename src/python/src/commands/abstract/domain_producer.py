import json, functools, pika
from argparse import Namespace

from rmq.commands import Producer


class DomainProducer(Producer):
    """
    This Producer inherits from base Producer, but changes logic of sending task with using domain_queue_map
    Notice, parameter `--task_queue` became unnecessary. `self.task_queue_name` is queue used for urls that
    our system doesn't support
    
    Motivation of creating this class was adjust Producer to work with domain_queue_map
    """
    def __init__(self):
        """
        `self.unmapped_domain_queue` is new `self.task_queue_name`
        get `self.domain_queue_map` from settings
        """
        super().__init__()
        self.domain_queue_map = self.project_settings.get("RMQ_DOMAIN_QUEUE_MAP")
        self.unmapped_domain_queue = self.project_settings.get("RMQ_UNMAPPED_DOMAIN_QUEUE")

    def init_task_queue_name(self, opts: Namespace):
        """
        leave possibility to rename task_queue_name
        """
        task_queue_name = getattr(opts, "task_queue_name", None)
        self.task_queue_name = self.unmapped_domain_queue
        if task_queue_name:
            self.task_queue_name = task_queue_name
        return task_queue_name

    def execute(self, _args: list[str], opts: Namespace):
        super().execute(_args, opts)

    def get_queue_name(self, msg_body):
        """
        method for getting task_queue_name from settings, using domain
        """
        return self.domain_queue_map.get(msg_body.get('domain'), self.task_queue_name)

    def _send_message(self, msg_body):
        """
        all differences from parent class is `queue_name=self.get_queue_name(msg_body)` 
        """
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

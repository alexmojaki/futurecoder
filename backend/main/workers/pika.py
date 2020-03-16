import atexit
import json
import os
from contextlib import contextmanager
from functools import cached_property

from littleutils import retry

from main.utils import thread_separate_lru_cache
from main.workers.communications import AbstractCommunications


@thread_separate_lru_cache()
@retry(num_attempts=10, sleeptime=2)
def connection():
    import pika

    host = os.environ['RABBITMQ_HOST']
    result = pika.BlockingConnection(pika.ConnectionParameters(host))
    atexit.register(result.close)
    return result


def make_channel():
    return connection().channel()


class Queue:
    def __init__(self, name, channel=None, persist=None):
        self.name = name
        if persist is None:
            persist = bool(channel)
        self.persist = persist
        self.channel = channel or make_channel()
        self.channel.queue_declare(queue=name)
        if persist:
            atexit.register(self.cleanup)

    def cleanup(self):
        self.channel.cancel()
        self.channel.close()

    @cached_property
    def consume_generator(self):
        return self.channel.consume(self.name)

    @contextmanager
    def maybe_cleanup(self):
        try:
            yield
        finally:
            if not self.persist:
                self.cleanup()

    def consume(self):
        with self.maybe_cleanup():
            method_frame, properties, body = next(self.consume_generator)
            self.channel.basic_ack(method_frame.delivery_tag)

        return json.loads(body.decode('utf8'))

    def publish(self, value):
        body = json.dumps(value).encode('utf8')
        with self.maybe_cleanup():
            self.channel.basic_publish(
                exchange='',
                routing_key=self.name,
                body=body,
            )


def send_result(user_id, entry):
    Queue(str(user_id)).publish(entry)


class PikaCommunications(AbstractCommunications):
    def make_master_side_communications(self):
        return type(self)()

    @cached_property
    def entry_queue(self):
        return Queue('entry_queue', persist=True)

    def send_entry(self, entry):
        self.entry_queue.publish(entry)

    def recv_entry(self):
        return self.entry_queue.consume()

    def send_result(self, queue_name, result):
        Queue(queue_name).publish(result)

    def recv_result(self, queue_name):
        return Queue(queue_name).consume()

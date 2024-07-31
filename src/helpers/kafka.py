import socket

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from src.config import Config

CONSUMER_CONF = {
    **Config.KAFKA_CONF,
    "group.id": "HermesAPIGroup",
}


class KafkaAPI:
    def __init__(self):
        self._producer_client = None
        self._consumer_client = None
        self._admin_client = None

    @property
    def _admin(self):
        if self._admin_client:
            return self._admin_client
        self._admin_client = AdminClient(Config.KAFKA_CONF)
        return self._admin_client

    @property
    def _producer(self):
        if self._producer_client:
            return self._producer_client
        self._producer_client = Producer(
            {
                **Config.KAFKA_CONF,
                "client.id": socket.gethostname(),
            }
        )
        return self._producer_client

    @property
    def _consumer(self):
        if self._consumer_client:
            return self._consumer_client
        self._consumer_client = Producer(CONSUMER_CONF)
        return self._consumer_client

    def _list_topics(self):
        return self._admin.list_topics().topics

    def _create_topic(self, topic):
        self._admin.create_topics([NewTopic(topic)])

    def produce(self, topic, message):
        self._producer.produce(topic, message)
        self._producer.flush()


Kafka = KafkaAPI()

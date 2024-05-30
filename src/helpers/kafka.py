import socket

from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic

from src.config import Config

PRODUCER_CONF = {
    **Config.KAFKA_CONF,
    "client.id": socket.gethostname(),
}

CONSUMER_CONF = {
    **Config.KAFKA_CONF,
    "group.id": "HermesAPIGroup",
}


class KafkaAPI:
    def __init__(self):
        self.admin = AdminClient(Config.KAFKA_CONF)
        self.producer = Producer(PRODUCER_CONF)
        self.consumer = Consumer(CONSUMER_CONF)

    def _list_topics(self):
        return self.admin.list_topics().topics

    def _create_topic(self, topic):
        self.admin.create_topics([NewTopic(topic)])

    def produce(self, topic, message):
        if topic not in self._list_topics():
            self._create_topic(topic)
        
        self.producer.produce(topic, message)
        self.producer.flush()

Kafka = KafkaAPI()
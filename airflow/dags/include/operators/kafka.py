import asyncio
import json
import logging
from typing import Dict, Any, Tuple
from airflow.triggers.base import BaseTrigger, TriggerEvent
from confluent_kafka import Consumer, KafkaError, KafkaException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook


class KafkaMessageTrigger(BaseTrigger):
    def __init__(
        self,
        topic: str,
        kafka_config: Dict,
        batch_size: int = 100,
        poll_interval: float = 5.0
    ):
        super().__init__()
        self.topic = topic
        self.kafka_config = kafka_config
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self._logger = logging.getLogger(__name__)

    def serialize(self) -> Tuple[str, Dict]:
        return ("dags.include.operators.kafka.KafkaMessageTrigger", {
            "topic": self.topic,
            "kafka_config": self.kafka_config,
            "batch_size": self.batch_size,
            "poll_interval": self.poll_interval,
        })

    async def run(self):
        self._logger.info(f"KafkaMessageTrigger.run() started for topic: {self.topic}")

        while True:
            try:
                messages = await self._poll_kafka()
                if messages:
                    self._logger.info(f"Yielding {len(messages)} messages from topic: {self.topic}")
                    yield TriggerEvent({"messages": messages})
                else:
                    self._logger.info(f"No messages found for topic: {self.topic}")

                self._logger.info(f"Sleeping for {self.poll_interval} seconds")
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                self._logger.error(f"Error in KafkaMessageTrigger for topic {self.topic}: {str(e)}")
                yield TriggerEvent({"status": "error", "message": str(e)})
                return

    async def _poll_kafka(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._poll_kafka_sync)

    def _poll_kafka_sync(self):
        self._logger.info(f"Polling Kafka for topic: {self.topic}")
        self._logger.info(self.kafka_config)
        consumer = Consumer(self.kafka_config)
        consumer.subscribe([self.topic])
        messages = []

        try:
            while len(messages) < self.batch_size:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                try:
                    messages.append(json.loads(msg.value().decode('utf-8')))
                except json.JSONDecodeError:
                    self._logger.error(f"Failed to decode message: {msg.value()}")

            consumer.commit()
        finally:
            consumer.close()

        self._logger.info(f"Returning {len(messages)} processed messages")
        return messages


class KafkaMessageOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        topic: str,
        kafka_conn_id: str = 'kafka_default',
        batch_size: int = 100,
        poll_interval: float = 5.0,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.topic = topic
        self.kafka_conn_id = kafka_conn_id
        self.batch_size = batch_size
        self.poll_interval = poll_interval

        connection = BaseHook.get_connection(self.kafka_conn_id)
        kafka_config = {
            'bootstrap.servers': connection.host,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': connection.login,
            'sasl.password': connection.password,
            'group.id': f'airflow_operator_{self.task_id}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        }
        if connection.extra_dejson:
            kafka_config.update(connection.extra_dejson)
        self.kafka_config = kafka_config

    def execute(self, context):
        self.log.info("KafkaMessageOperator.execute() started")


        self.log.info("Deferring to KafkaMessageTrigger")
        self.defer(
            trigger=KafkaMessageTrigger(
                topic=self.topic,
                kafka_config=self.kafka_config,
                batch_size=self.batch_size,
                poll_interval=self.poll_interval
            ),
            method_name="process_messages"
        )

    def process_messages(self, context, event=None):
        self.log.info("process_messages() called")
        if event:
            if event.get("status") == "error":
                self.log.info(self.kafka_config)
                self.log.info(event)
                return
            messages = event.get('messages', [])
            self.log.info(f"Received {len(messages)} messages from Kafka")
            for message in messages:
                self.log.info(f"Message: {message}")
        else:
            self.log.info("No messages received from Kafka")
        self.defer(
            trigger=KafkaMessageTrigger(
                topic=self.topic,
                kafka_config=self.kafka_config,
                batch_size=self.batch_size,
                poll_interval=self.poll_interval
            ),
            method_name="process_messages"
        )

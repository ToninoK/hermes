import asyncio
import json
import logging
from typing import Dict, Any, Tuple, Callable
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
        poll_interval: float = 5.0,
    ):
        super().__init__()
        self.topic = topic
        self.kafka_config = kafka_config
        self.batch_size = batch_size
        self.poll_interval = poll_interval

    def serialize(self) -> Tuple[str, Dict]:
        return (
            "dags.include.operators.kafka.KafkaMessageTrigger",
            {
                "topic": self.topic,
                "kafka_config": self.kafka_config,
                "batch_size": self.batch_size,
                "poll_interval": self.poll_interval,
            },
        )

    async def run(self):
        self.log.info(f"KafkaMessageTrigger.run() started for topic: {self.topic}")

        while True:
            try:
                messages = await self._poll_kafka()
                if messages:
                    self.log.info(
                        f"Yielding {len(messages)} messages from topic: {self.topic}"
                    )
                    yield TriggerEvent({"messages": messages})
                else:
                    self.log.info(f"No messages found for topic: {self.topic}")

                self.log.info(f"Sleeping for {self.poll_interval} seconds")
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                self.log.error(
                    f"Error in KafkaMessageTrigger for topic {self.topic}: {str(e)}"
                )
                yield TriggerEvent({"status": "error", "message": str(e)})
                return

    async def _poll_kafka(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._poll_kafka_sync)

    def _poll_kafka_sync(self):
        self.log.info(f"Polling Kafka for topic: {self.topic}")
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
                    messages.append(json.loads(msg.value().decode("utf-8")))
                except json.JSONDecodeError:
                    self.log.error(f"Failed to decode message: {msg.value()}")

            consumer.commit()
        finally:
            consumer.close()

        self.log.info(f"Returning {len(messages)} processed messages")
        return messages


class KafkaMessageCallbackOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        topic: str,
        callback: Callable,
        kafka_conn_id: str = "kafka_default",
        batch_size: int = 100,
        poll_interval: float = 5.0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.topic = topic
        self.kafka_conn_id = kafka_conn_id
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.callback = callback
        self.kafka_config = self._init_kafka_config()

    def _init_kafka_config(self):
        connection = BaseHook.get_connection(self.kafka_conn_id)
        kafka_config = {
            "bootstrap.servers": connection.host,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": connection.login,
            "sasl.password": connection.password,
            "group.id": f"airflow_operator_{self.task_id}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        if connection.extra_dejson:
            kafka_config.update(connection.extra_dejson)
        return kafka_config

    def execute(self, context):
        self.log.info("KafkaMessageOperator.execute() started")
        self.log.info("Deferring to KafkaMessageTrigger")
        self.defer(
            trigger=KafkaMessageTrigger(
                topic=self.topic,
                kafka_config=self.kafka_config,
                batch_size=self.batch_size,
                poll_interval=self.poll_interval,
            ),
            method_name="_apply_callback",
        )

    def _apply_callback(self, context, event=None):
        self.log.info(f"Applying callback {self.callback.__name__} to messages")
        if event and event.get("status") == "error":
            self.log.error(
                f"KafkaMessageTrigger yielded error with message: {event.get('message')}"
            )
        elif event:
            messages = event.get("messages") or []
            self.log.info(f"Received {len(messages)} messages from Kafka")
            for message in messages:
                self.callback(message, **context)
        else:
            self.log.info("No messages received from Kafka")
        self.defer(
            trigger=KafkaMessageTrigger(
                topic=self.topic,
                kafka_config=self.kafka_config,
                batch_size=self.batch_size,
                poll_interval=self.poll_interval,
            ),
            method_name="_apply_callback",
        )

from datetime import datetime
import uuid
import json

from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.apache.kafka.sensors.kafka import (
    AwaitMessageTriggerFunctionSensor,
)

KAFKA_TOPIC = "report_requests"


def trigger_report_generation_dag(event, **context):
    print("Triggering report: ", event)
    TriggerDagRunOperator(
        trigger_dag_id="report_generation",
        task_id=f"triggered_downstream_report_generation_dag_{uuid.uuid4()}",
        wait_for_completion=False,  # wait for downstream DAG completion
        conf={
            "config": event,
        },
        poke_interval=5,
    ).execute(context)

    print("Concluded report generation")


def process_report_request(message):
    message_content = json.loads(message.value())
    return message_content


@dag(
    start_date=datetime(2024, 5, 20),
    schedule="@continuous",
    catchup=False,
    max_active_runs=1,
    dag_id="kafka_listener",
)
def kafka_listener():

    topic_sensor = AwaitMessageTriggerFunctionSensor(
        task_id="topic_sensor",
        topics=[KAFKA_TOPIC],
        apply_function="kafka_listener.process_report_request",
        event_triggered_function=trigger_report_generation_dag,
        poll_interval=1,
        poll_timeout=5,
    )

    topic_sensor


kafka_listener()

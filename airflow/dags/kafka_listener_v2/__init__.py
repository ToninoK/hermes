from datetime import datetime, timedelta
import uuid
import json

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from dags.include.operators.kafka import KafkaMessageCallbackOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


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

@dag(
    default_args=default_args,
    schedule_interval="@continuous",
    max_active_runs=1,
    catchup=False,
)
def kafka_custom_triggerer():
    kafka_task = KafkaMessageCallbackOperator(
        task_id="poll_kafka_messages",
        topic="report_requests",
        callback=trigger_report_generation_dag,
        kafka_conn_id="kafka_listener_v2",
        batch_size=5,
        poll_interval=3.0,
    )

    kafka_task

kafka_custom_triggerer()
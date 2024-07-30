from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from dags.include.operators.kafka import KafkaMessageOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kafka_message_processing',
    default_args=default_args,
    schedule_interval="@once",
    catchup=False
)

def process_messages(ti):
    messages = ti.xcom_pull(task_ids='poll_kafka_messages')
    for message in messages:
        # Process each message here
        print(f"Processing message: {message}")

kafka_task = KafkaMessageOperator(
    task_id='poll_kafka_messages',
    topic='report_requests',
    kafka_conn_id='kafka_listener_v2',
    batch_size=5,
    poll_interval=3.0,
    dag=dag,
)


kafka_task

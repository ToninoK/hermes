from airflow.decorators import dag, task
from pendulum import datetime
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator
import json


KAFKA_TOPIC = "reports"

def consume_function(message):
    key = json.loads(message.key())
    message_content = json.loads(message.value())
    print(
        f"Report Configuration #{key}: Hello {message_content}"
    )


@dag(
    start_date=datetime(2024, 5, 20),
    schedule=None,
    catchup=False,
    render_template_as_native_obj=True,
)
def consume_reports():
    consume_report = ConsumeFromTopicOperator(
        task_id="consume_report",
        kafka_config_id="kafka_default",
        topics=[KAFKA_TOPIC],
        apply_function=consume_function,
        apply_function_kwargs={
            "name": "{{ ti.xcom_pull(task_ids='get_pet_owner_name')}}"
        },
        poll_timeout=20,
        max_messages=20,
        max_batch_size=20,
    )

    consume_report

consume_reports()

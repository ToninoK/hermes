from airflow.decorators import dag, task
from pendulum import datetime
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator
import json

from airflow.providers.smtp.hooks.smtp import SmtpHook
from airflow.operators.python_operator import PythonOperator

KAFKA_TOPIC = "reports"


def send_mail(**kwargs):
    hook = SmtpHook(smtp_conn_id='mailtrap_smtp')
    sender = "Hermes Demo <hermes.demo.tk@gmail.com>"
    emails = kwargs.get("emails")
    file_path = "./include/reports/" + kwargs.get("config_key", "")
    with hook.get_conn() as smtp_client:
        smtp_client.send_email_smtp(
            to=emails,
            subject="Your Report by Hermes",
            from_email=sender,
            html_content="<h1>Your report is ready!</h1>The report you requested is attached in the email.",
            files=[file_path]
        )


def consume_next_message():
    return "consume_next_message"


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
            "name": "{{ ti.xcom_pull(task_ids='consume_next_message')}}"
        },
        poll_timeout=20,
        max_messages=20,
        max_batch_size=20,
    )

    email = PythonOperator(
        task_id="send_email",
        python_callable=send_mail,
    )

    consume_report >> email

consume_reports()

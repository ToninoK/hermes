import json

from airflow.decorators import dag, task
from pendulum import datetime
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator

from airflow.operators.python_operator import PythonOperator

from dags.report_generation.report_factory import ReportGenerator


def send_mail(**kwargs):
    # hook = SmtpHook(smtp_conn_id='mailtrap_smtp')
    # sender = "Hermes Demo <hermes.demo.tk@gmail.com>"
    # emails = kwargs.get("emails")
    # file_path = "./include/reports/" + kwargs.get("config_key", "")
    # with hook.get_conn() as smtp_client:
    #     smtp_client.send_email_smtp(
    #         to=emails,
    #         subject="Your Report by Hermes",
    #         from_email=sender,
    #         html_content="<h1>Your report is ready!</h1>The report you requested is attached in the email.",
    #         files=[file_path]
        # )
    pass


@dag(
    start_date=datetime(2024, 5, 20),
    schedule=None,  # @continuous
    catchup=False,
    dag_id="report_generation",
)
def consume_reports():

    @task
    def generate_report(**context):
        ReportGenerator.generate(context["params"]["config"])

    email = PythonOperator(
        task_id="send_email",
        python_callable=send_mail,
    )

    generate_report() >> email

consume_reports()

import csv

from airflow.decorators import dag, task
from pendulum import datetime
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator

from airflow.operators.python_operator import PythonOperator
from airflow.providers.smtp.hooks.smtp import SmtpHook

from dags.report_generation.report_factory import ReportGenerator


@dag(
    start_date=datetime(2024, 5, 20),
    schedule=None,
    catchup=False,
    dag_id="report_generation",
)
def consume_reports():

    @task
    def generate_report(**context):
        results = ReportGenerator.generate(context["params"]["config"])
        return results
    
    @task
    def store_to_csv(**context):
        results = context["task_instance"].xcom_pull(task_ids="generate_report")
        file_path = "./dags/include/reports/" + context["params"]["config"]["config_key"] + ".csv"
        import os
        with open(file_path, "w") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    @task
    def send_mail(**context):
        config_key = context["params"]["config"]["config_key"]
        emails = context["params"]["config"]["emails"]
        hook = SmtpHook(smtp_conn_id='mailtrap_smtp')
        sender = "Hermes Demo <hermes.demo.tk@gmail.com>"
        file_path = "./dags/include/reports/" + config_key + ".csv"
        with hook.get_conn() as smtp_client:
            smtp_client.send_email_smtp(
                to=emails,
                subject="Your Report by Hermes",
                from_email=sender,
                html_content="<h1>Your report is ready!</h1>The report you requested is attached in the email.",
                files=[file_path]
            )


    generate_report() >> store_to_csv() >> send_mail()

consume_reports()

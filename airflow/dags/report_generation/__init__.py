import csv

from airflow.decorators import dag, task
from airflow.hooks.postgres_hook import PostgresHook
from pendulum import datetime

from airflow.providers.smtp.hooks.smtp import SmtpHook


@dag(
    start_date=datetime(2024, 5, 20),
    schedule=None,
    catchup=False,
    dag_id="report_generation",
)
def consume_reports():

    @task
    def generate_report(**context):
        hook = PostgresHook(postgres_conn_id="postgres_conn")
        conn = hook.get_conn()
        with conn.cursor() as cursor:
            query = context["params"]["config"]["query"]
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col.name for col in cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    @task
    def store_to_csv(**context):
        results = context["task_instance"].xcom_pull(task_ids="generate_report")
        if not results:
            return
        file_path = "./dags/include/reports/" + context["params"]["config"]["config_key"] + ".csv"
        with open(file_path, "w") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    @task
    def send_mail(**context):
        results = context["task_instance"].xcom_pull(task_ids="generate_report")
        if not results:
            return
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

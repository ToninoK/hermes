from os import environ
from datetime import datetime
import asyncio
import json

from celery import Celery
from celery.schedules import crontab
from dateutil.relativedelta import relativedelta

from src.db.schedules import get_schedules_all
from src.helpers.kafka import Kafka
from src.helpers.report_factory import ReportGenerator


REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}"
app = Celery(__name__, broker=redis_url, result_backend=redis_url)
app.conf.beat_schedule = {
    "sr_daily": {
        "task": "scheduled_reports_daily",
        "schedule": 25,
    },
    "sr_weekly": {
        "task": "scheduled_reports_weekly",
        "schedule": crontab(hour="7", minute="0", day_of_week="mon"),
    },
    "sr_monthly": {
        "task": "scheduled_reports_monthly",
        "schedule": crontab(day_of_month="1", hour="7", minute="0"),
    },
}
app.conf.timezone = "UTC"


def _prep_date_filters(date, frequency):
    if frequency == "daily":
        start_date = date - relativedelta(days=1)
    elif frequency == "weekly":
        start_date = date - relativedelta(weeks=1)
    else:
        start_date = date - relativedelta(months=1)

    return (
        {
            "field": "start_date",
            "operator": ">=",
            "value": start_date.strftime("%Y-%m-%d"),
        },
        {"field": "end_date", "operator": "<", "value": date.strftime("%Y-%m-%d")},
    )


def _prep_config(schedule, current_date=None):
    report_config = schedule["config"]
    frequency = schedule["frequency"]
    filters = report_config["config"]["filters"]
    filters = [
        filt for filt in filters if filt["field"] not in ["start_date", "end_date"]
    ]

    start_date, end_date = _prep_date_filters(
        current_date or datetime.now().date(), frequency
    )
    filters.append(start_date)
    filters.append(end_date)
    report_config["config"]["filters"] = filters
    query = ReportGenerator.generate(report_config.pop("config", {}))
    report_config["query"] = query
    return report_config


def _handle_report_schedules(frequency):
    loop = asyncio.get_event_loop()
    schedules = loop.run_until_complete(get_schedules_all(frequency))
    for schedule in schedules:
        config = _prep_config(schedule)
        Kafka.produce("report_requests", json.dumps(config))


@app.task(name="scheduled_reports_daily")
def daily_schedule():
    print("Starting task scheduled_reports_daily")
    _handle_report_schedules("daily")
    print("Finished task scheduled_reports_daily")


@app.task(name="scheduled_reports_weekly")
def weekly_schedule():
    print("Starting task scheduled_reports_weekly")
    _handle_report_schedules("weekly")
    print("Finished task scheduled_reports_weekly")


@app.task(name="scheduled_reports_monthly")
def monthly_schedule():
    print("Starting task scheduled_reports_monthly")
    _handle_report_schedules("monthly")
    print("Finished task scheduled_reports_monthly")

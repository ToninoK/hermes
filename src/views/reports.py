from fastapi import APIRouter, Depends
import json

from src.db.schedules import get_schedules, create_schedule
from src.helpers.auth import JWTBearer, get_current_user
from src.helpers.kafka import Kafka
from src.helpers.report_factory import ReportGenerator
from src.schemas.report_config import ReportConfig

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/create")
async def create_report(report_config: ReportConfig, token=Depends(JWTBearer())):
    await report_config.verify_acl(token)
    report = await report_config.generate_config(token=token)
    query = ReportGenerator.generate(report.pop("config", {}))
    report["query"] = query
    Kafka.produce("report_requests", message=json.dumps(report))
    return {"message": "Report request sent", "report_config": report}


@router.post("/schedule/<frequency>")
async def schedule_report(frequency: str, report_config: ReportConfig, token=Depends(JWTBearer())):
    await report_config.verify_acl(token)
    user = await get_current_user(token)
    data = await report_config.generate_config(token=token)
    schedule = {
        "frequency": frequency,
        "config": json.dumps(data),
        "email": user["email"],
    }
    schedule = await create_schedule(**schedule)
    return schedule


@router.get("/schedule/<frequency>")
async def index(frequency: str, token=Depends(JWTBearer())):
    user = await get_current_user(token)
    schedules = await get_schedules(frequency, user["email"])
    return schedules

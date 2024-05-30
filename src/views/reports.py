from fastapi import APIRouter, Depends
import pickle

from src.helpers.auth import JWTBearer
from src.helpers.kafka import Kafka
from src.schemas.report_config import ReportConfig

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/create")
async def create_report(report_config: ReportConfig, token=Depends(JWTBearer())):
    await report_config.verify_acl(token)
    message = await report_config.generate_config(token=token)
    Kafka.produce("report_requests", pickle.dumps(message))
    return {"message": "Report request sent", "report_config": message}

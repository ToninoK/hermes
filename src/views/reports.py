from fastapi import APIRouter, Depends

from src.helpers.auth import JWTBearer
from src.schemas.report_config import ReportConfig

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/create")
async def create_report(report_config: ReportConfig, token=Depends(JWTBearer())):
    await report_config.verify_acl(token)

    return {"report_config": report_config.model_dump()}

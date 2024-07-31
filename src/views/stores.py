from fastapi import APIRouter, Depends

from src.db.stores import fetch_stores
from src.helpers.auth import JWTBearer

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", dependencies=[Depends(JWTBearer())])
async def index():
    return await fetch_stores()

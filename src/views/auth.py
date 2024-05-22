from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Depends

from src.helpers.auth import create_access_token, get_current_user, JWTBearer, get_password_hash, verify_password
from src.db.users import create_user, get_user_by_email
from src.schemas.user import UserAuth

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post('/signup')
async def signup(user_data: UserAuth):
    user = await get_user_by_email(user_data["email"])
    if user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user_data = {**user_data, "password": get_password_hash(user_data["password"])}
    await create_user(user_data)
    token_data = {
        "sub": user_data["email"],
        "level": "unknown",
    }
    token = create_access_token(token_data)
    return token


@router.post('/login')
async def login(user: UserAuth):

    db_user = await get_user_by_email(user["email"])
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Email not registered",
        )
    if not verify_password(user["password"], db_user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )
    token_data = {
        "sub": db_user["email"],
        "level": db_user["role"],
    }
    token = create_access_token(token_data)
    return token


@router.get("/identify/me")
async def identify(token=Depends(JWTBearer)):
    user = get_current_user(token)
    return user

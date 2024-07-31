from fastapi import APIRouter, HTTPException, Depends, Response

from src.helpers.auth import (
    create_access_token,
    get_current_user,
    JWTBearer,
    get_password_hash,
    verify_password,
    blacklist_token,
)
from src.helpers.cache import acl_cache
from src.db.users import create_user, get_user_by_email, update_user_by_email
from src.schemas.user import UserAuth, UserData, UserLogin

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup")
async def signup(user_data: UserAuth):
    user_data = dict(user_data)
    user = await get_user_by_email(user_data["email"], fields=["email"])
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


@router.post("/login")
async def login(user: UserLogin):
    user = user.model_dump()
    db_user = await get_user_by_email(
        user["email"], fields=["email", "password", "role"]
    )
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


@router.post("/<email>/grant")
async def grant(email: str, user: UserData, token=Depends(JWTBearer())):
    current_user = await get_current_user(token)
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action",
        )
    user = await update_user_by_email(email, user)
    return user


@router.get("/logout")
async def logout(token=Depends(JWTBearer())):
    blacklist_token(token)
    return Response(status_code=200)


@router.get("/identify/me")
async def identify(token=Depends(JWTBearer())):
    user = await get_current_user(token)
    return user


@router.get("/my/access")
async def access(token=Depends(JWTBearer())):
    user = await get_current_user(token)
    data, _ = acl_cache.get(user["role"])
    return data or {}

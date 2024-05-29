from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from src.helpers.cache import Cache
from src.db.users import get_user_by_email
from src.config import Config

ALGORITHM = "HS256"

auth_cache = Cache(namespace="blacklisted_tokens")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[int] = 24 * 60):
    """Create an access token with an expiration timestamp

    :param data: dictionary containing data to encode in the token
    :param expires_delta: integer representing number of minutes the token should last
    :rtype: dict
    :return: dictionary containing access_token, token_type, and role
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=ALGORITHM)
    return {
        "access_token": encoded_jwt,
        "level": data["level"],
        "token_type": "bearer",
        "expires_at": expire,
        "email": data["sub"],
    }


def blacklist_token(token: str):
    """Add token to redis

    Adding the token to redis will serve as a means of blacklisting a token once a
    user requests a logout
    :param token: the token to blacklist
    :rtype: bool
    :returns: True if token was successfully blacklisted, otherwise False
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload.get("exp", 0))
        ttl = (datetime.utcnow() - exp).seconds
    except PyJWTError as ex:
        raise HTTPException(status_code=401) from ex
    return auth_cache.set(token, "True", ttl=ttl)


def decode_jwt(token: str):
    """Decode the jwt token while raising exceptions for invalid tokens

    :param token: token to decode
    :rtype: dict
    :return: data decoded from the token
    """
    try:
        _, hit = auth_cache.get(token)
        if hit:
            raise HTTPException(status_code=401, detail="Token invalid, request a new one")

        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload.get("exp", 0))
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalid")
        if exp <= datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired, request a new one")
    except PyJWTError as ex:
        raise HTTPException(status_code=401, detail="Error while decoding token.") from ex

    return payload


async def get_current_user(token: str):
    """Return the currently logged in user

    :param token: token that belongs to the specific user
    :rtype: dict
    :return: currently logged in user
    """
    payload = decode_jwt(token)
    user = await get_user_by_email(payload.get("sub"), ["id", "email", "role", "store_id"])
    if user is None:
        raise HTTPException(status_code=401)

    return user


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error, bearerFormat="JWT")

    async def __call__(self, request: Request):
        """Method which is called when the class is invoked
        Checks if the credentials passed in during the course of invoking the class are valid
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=401, detail="Invalid authentication scheme."
                )
            self.verify_jwt(credentials.credentials)
            return credentials.credentials
        raise HTTPException(status_code=401, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(token: str) -> bool:
        """Verify if the token is valid"""
        try:
            decode_jwt(token)
        except:
            return False
        return True

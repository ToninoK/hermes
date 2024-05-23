from pydantic import BaseModel


class UserAuth(BaseModel):
    email: str
    password: str


class UserData(BaseModel):
    email: str
    role: str
    password: str

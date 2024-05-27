from pydantic import BaseModel


class UserAuth(BaseModel):
    email: str
    password: str
    name: str
    store_id: int


class UserData(BaseModel):
    email: str
    role: str
    password: str

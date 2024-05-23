from contextlib import asynccontextmanager


from fastapi import FastAPI

from src.views import auth
from src.helpers.acl import load_acl


app = FastAPI()

routers = [
    auth
]

for router in routers:
    app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_acl()
    yield

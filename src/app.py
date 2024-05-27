from contextlib import asynccontextmanager


from fastapi import FastAPI

from src.views import auth, stores
from src.helpers.acl import load_acl


app = FastAPI()

routers = [
    auth,
    stores,
]

for router in routers:
    app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_acl()
    yield

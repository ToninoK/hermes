from fastapi import FastAPI
from confluent_kafka import Producer
from uuid import uuid4

from src.config import Config
from src.views import auth

app = FastAPI()

routers = [
    auth
]

for router in routers:
    app.include_router(router)


producer = Producer(Config.KAFKA_CONF)


@app.get("/test")
async def test():
    return {"message": "Hello world!"}


@app.get("/submit-topic")
async def post_topic():
    uuid = str(uuid4())
    producer.produce("test-topics", key=str(uuid), value="first-test")
    return uuid

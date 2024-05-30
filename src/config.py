import socket
from os import environ


class Config:
    KAFKA_USERNAME = environ.get('KAFKA_USERNAME')
    KAFKA_PASSWORD = environ.get('KAFKA_PASSWORD')
    KAFKA_BOOTSTRAP_SERVERS_URL = environ.get('KAFKA_BOOTSTRAP_SERVERS_URL')
    KAFKA_CONF = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS_URL,
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": KAFKA_USERNAME,
        "sasl.password": KAFKA_PASSWORD,
    }

    POSTGRES_HOST = environ.get("POSTGRES_HOST", "hermes_db")
    POSTGRES_DB = environ.get("POSTGRES_DB", "hermes_db")
    POSTGRES_USER = environ.get("POSTGRES_USER", "hermes")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", "semreh")

    REDIS_HOST = environ.get("REDIS_HOST", "hermes_cache")
    REDIS_PORT = environ.get("REDIS_PORT", 6379)

    SECRET_KEY = environ.get("SECRET_KEY", "secret_key")
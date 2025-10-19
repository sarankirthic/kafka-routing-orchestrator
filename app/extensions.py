from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from confluent_kafka import Producer

db = SQLAlchemy()
migrate = Migrate()


class RedisClient:
    def __init__(self):
        self._client = None

    def init_app(self, app):
        url = app.config["REDIS_URL"]
        # Lazy connect; allow app to start even if Redis is not yet up
        self._client = Redis.from_url(url, decode_responses=True)

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("Redis not initialized")
        return self._client


redis_client = RedisClient()


class KafkaProducerWrapper:
    def __init__(self):
        self._producer = None

    def init_app(self, app):
        conf = {
            "bootstrap.servers": app.config["KAFKA_BOOTSTRAP_SERVERS"],
            "client.id": app.config["KAFKA_CLIENT_ID"],
            # Idempotence for safer delivery on retries
            "enable.idempotence": True,
            "acks": "all",
            # Reasonable defaults; tune in production
            "linger.ms": 5,
            "batch.num.messages": 1000,
        }
        self._producer = Producer(conf)

    @property
    def producer(self):
        if self._producer is None:
            raise RuntimeError("Kafka producer not initialized")
        return self._producer


kafka_producer = KafkaProducerWrapper()

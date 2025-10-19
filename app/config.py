import os


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/appdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "contact-center-api")
    # Topic names (override per env if needed)
    TOPIC_ROUTING_REQUESTS = os.getenv("TOPIC_ROUTING_REQUESTS", "customer.routing.requests")
    TOPIC_ASSIGNMENTS = os.getenv("TOPIC_ASSIGNMENTS", "customer.assignments")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config(name: str):
    mapping = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return mapping.get(name, DevelopmentConfig)

from flask import Flask
from .config import get_config
from .extensions import db, migrate, redis_client, kafka_producer
from .api import create_api_blueprint


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Lazy init external clients so app can boot without hard deps
    redis_client.init_app(app)
    kafka_producer.init_app(app)

    # Register blueprints (optional; shown as a hook)
    app.register_blueprint(create_api_blueprint(), url_prefix="/api")

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app

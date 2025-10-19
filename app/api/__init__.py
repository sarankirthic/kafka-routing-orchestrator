from flask import Blueprint
from .agents import bp as agents_bp
from .customers import bp as customers_bp
from .assignments import bp as assignments_bp


def create_api_blueprint() -> Blueprint:
    api = Blueprint("api", __name__)
    api.register_blueprint(agents_bp, url_prefix="/agents")
    api.register_blueprint(customers_bp, url_prefix="/customers")
    api.register_blueprint(assignments_bp, url_prefix="/assignments")
    return api

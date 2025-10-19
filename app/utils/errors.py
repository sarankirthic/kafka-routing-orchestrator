from flask import jsonify
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    """Base class for application-specific exceptions."""
    status_code = 500
    message = "Internal server error"

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message)
        self.message = message or self.message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["status_code"] = self.status_code
        return rv


class BadRequestError(AppError):
    status_code = 400
    message = "Invalid request parameters"


class UnauthorizedError(AppError):
    status_code = 401
    message = "Unauthorized access"


class NotFoundError(AppError):
    status_code = 404
    message = "Requested resource not found"


class ConflictError(AppError):
    status_code = 409
    message = "Resource conflict"


def register_error_handlers(app):
    """
    Register structured error responses globally for the Flask app.
    """
    @app.errorhandler(AppError)
    def handle_custom_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handles Flask/Werkzeug HTTP exceptions uniformly."""
        payload = {"error": error.description, "status_code": error.code}
        return jsonify(payload), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Catch-all fallback for unhandled exceptions."""
        payload = {"error": str(error), "status_code": 500}
        return jsonify(payload), 500

    return app

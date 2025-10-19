# app/utils/logging.py
import logging.config
import sys
from pythonjsonlogger import jsonlogger


def configure_logging(log_level: str = "INFO"):
    """
    Configures project-wide structured JSON logging for Flask and background workers.
    """
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    json_handler = jsonlogger.JsonFormatter(log_format)

    # Stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(json_handler)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"stdout": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout"}},
        "root": {"handlers": ["stdout"], "level": log_level},
    }

    logging.config.dictConfig(logging_config)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    logging.getLogger("werkzeug").setLevel("WARNING")  # Mute excessive HTTP logs

    root_logger.info("Structured JSON logging initialized", extra={"level": log_level})
    return root_logger


def get_logger(name: str):
    """
    Obtain a structured logger instance by name.
    """
    logger = logging.getLogger(name)
    return logger

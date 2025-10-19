"""
Run the entire system locally with docker-compose or as individual services.

This script assumes you have Kafka, Zookeeper, Redis, and Postgres running locally.
It just runs the Flask API service for local development.
"""

import os
from app import create_app


def main():
    app = create_app("development")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()

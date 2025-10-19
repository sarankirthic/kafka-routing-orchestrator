# kafka-routing-orchestrator
A scalable, SaaS-ready contact center customer routing system built with Flask and Apache Kafka. It is a stateless 
REST and streaming system that routes customers to the best available agent using Kafka event streams.

#### Contact Center Routing

## Overview

This project implements a distributed, stateless yet stateful routing system that assigns customers to agents in real-time, 
supporting elastic scaling of services across machines without downtime. It uses:

- Flask REST APIs for customer, agent, and assignment management.
- Kafka topics to process routing requests and agent status events asynchronously.
- PostgreSQL and Redis as the durable and caching data stores.
- Structured JSON logging and centralized error handling for production readiness.

## Features

- Per-customer Kafka keyed routing ensuring ordered event processing.
- Seamless horizontal scaling with Kafka consumer groups and cooperative re-balancing.
- REST endpoints for agent/customer registration, status updates, and assignment queries.
- Background Kafka consumers that process routing requests and update agent states.
- Modular architecture with Flask application factory, Blueprints, service and repository layers.

## Getting Started

1. Configure environment variables in `.env.example`.
2. Run `scripts/create_topics.py` to ensure Kafka topics exist.
3. Seed data with `scripts/seed_data.py`.
4. Start services locally with `scripts/run_local.py`.
5. Use `wsgi.py` as the production entry point behind a WSGI server like Gunicorn.

## License

MIT License

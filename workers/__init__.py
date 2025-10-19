"""
Kafka stream processing workers for contact-center routing system.

- router_worker.py: consumes customer routing requests and assigns agents.
- agent_status_worker.py: consumes agent status updates and maintains presence.
- kafka_utils.py: shared config, serialization, and consumer utility functions.
"""

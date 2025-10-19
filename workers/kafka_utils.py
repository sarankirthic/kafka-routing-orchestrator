import json
from confluent_kafka import Consumer, KafkaException


def create_consumer(group_id, bootstrap_servers="localhost:9092", auto_offset_reset="earliest"):
    """
    Create and return a configured Kafka consumer with best practices for websockets microservices.

    Uses cooperative sticky assignor for graceful scaling and rebalance with minimal disruption.
    """
    conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": auto_offset_reset,
        "enable.auto.commit": False,
        "partition.assignment.strategy": "cooperative-sticky",
        "max.poll.interval.ms": 300000,
        "session.timeout.ms": 10000,
        "heartbeat.interval.ms": 3000,
        "enable.partition.eof": False,
    }
    consumer = Consumer(conf)
    return consumer


def json_deserializer(message):
    """
    Decode Kafka message value bytes to Python dict.
    """
    if message is None:
        return None
    try:
        return json.loads(message.decode("utf-8"))
    except Exception as ex:
        raise KafkaException(f"Failed to deserialize message: {ex}")


def parse_message(message):
    """
    Parse Kafka message to dict with key and value.
    """
    key = message.key()
    if key:
        key = key.decode("utf-8")
    value = json_deserializer(message.value())
    return key, value

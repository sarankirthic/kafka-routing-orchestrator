import json
from confluent_kafka import Producer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from flask import current_app


class KafkaAdapter:
    """High-level Kafka adapter for managing producers and administrative actions."""

    def __init__(self, bootstrap_servers: str, client_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.producer = None
        self.admin_client = None

    def init_app(self, app=None):
        config = {
            "bootstrap.servers": app.config.get("KAFKA_BOOTSTRAP_SERVERS", self.bootstrap_servers),
            "client.id": app.config.get("KAFKA_CLIENT_ID", self.client_id),
            "enable.idempotence": True,
            "acks": "all",
        }
        self.producer = Producer(config)
        self.admin_client = AdminClient({"bootstrap.servers": config["bootstrap.servers"]})

    def produce_json(self, topic: str, key: str, value: dict):
        """Publish a JSON payload to Kafka with key-based partitioning."""
        payload = json.dumps(value).encode("utf-8")
        try:
            self.producer.produce(topic, key=key.encode("utf-8"), value=payload)
            self.producer.poll(0)
        except BufferError as e:
            raise RuntimeError(f"Kafka buffer full: {e}")
        except KafkaError as e:
            raise RuntimeError(f"Kafka error: {e.str()}")

    def create_topic(self, topic_name: str, num_partitions: int = 3, replication_factor: int = 1):
        """Create Kafka topic if it doesn’t already exist."""
        topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        try:
            fs = self.admin_client.create_topics([topic])
            for _, f in fs.items():
                f.result(timeout=5)
        except Exception as e:
            if "TopicExistsError" not in str(e):
                raise RuntimeError(f"Failed to create topic {topic_name}: {e}")

    @classmethod
    def from_current_app(cls):
        """Convenience constructor for use inside Flask request context."""
        conf = current_app.config
        adapter = cls(conf["KAFKA_BOOTSTRAP_SERVERS"], conf.get("KAFKA_CLIENT_ID", "app"))
        adapter.init_app(current_app)
        return adapter

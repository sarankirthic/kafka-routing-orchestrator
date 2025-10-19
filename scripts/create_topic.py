import sys
from app import create_app
from app.adapters.kafka import KafkaAdapter


def main():
    app = create_app("development")
    app.app_context().push()

    kafka_adapter = KafkaAdapter.from_current_app()
    topics = [
        (app.config.get("TOPIC_ROUTING_REQUESTS"), 5, 1),
        (app.config.get("TOPIC_ASSIGNMENTS"), 5, 1),
        ("agent.status", 3, 1),
    ]

    for topic, partitions, replication in topics:
        try:
            kafka_adapter.create_topic(topic, partitions, replication)
            print(f"Created or verified topic: {topic} (partitions={partitions}, replication={replication})")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

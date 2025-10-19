import logging
import time
from confluent_kafka import KafkaException
from app.extensions import db
from app.services.agent_service import AgentService
from workers.kafka_utils import create_consumer, parse_message
from app import create_app

logger = logging.getLogger("agent_status_worker")


def main():
    app = create_app("production")
    app.app_context().push()

    consumer = create_consumer(group_id="agent_status_worker_group", bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'])
    topic = "agent.status"
    consumer.subscribe([topic])
    logger.info(f"Agent Status worker subscribed to topic: {topic}")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            key, data = parse_message(msg)
            logger.info(f"Consumed agent status message key={key}, value={data}")

            try:
                AgentService.upsert_agent(
                    agent_id=data.get("agent_id"),
                    tenant_id=data.get("tenant_id"),
                    status=data.get("status"),
                    skills=data.get("skills"),
                    current_load=data.get("current_load"),
                )
                consumer.commit(message=msg)
            except Exception as e:
                logger.exception(f"Error processing agent status message key={key}: {e}")

            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        logger.info("Agent Status worker shutdown gracefully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

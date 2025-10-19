import logging
import time
from confluent_kafka import KafkaException
from app.extensions import db
from app.services.routing_service import RoutingService
from workers.kafka_utils import create_consumer, parse_message
from app import create_app

logger = logging.getLogger("router_worker")


def main():
    app = create_app("production")
    app.app_context().push()

    consumer = create_consumer(group_id="router_worker_group", bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'])
    topic = app.config.get("TOPIC_ROUTING_REQUESTS", "customer.routing.requests")
    consumer.subscribe([topic])
    logger.info(f"Router worker subscribed to topic: {topic}")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            key, data = parse_message(msg)
            logger.info(f"Consumed message with key={key}, value={data}")

            try:
                result, status = RoutingService.assign_customer(
                    customer_id=data.get("customer_id"),
                    tenant_id=data.get("tenant_id"),
                    requested_skill=data.get("requested_skill"),
                    topic=app.config.get("TOPIC_ASSIGNMENTS", "customer.assignments")
                )
                logger.info(f"Routing result: {result}, status: {status}")
                if status == 200:
                    consumer.commit(message=msg)
            except Exception as e:
                logger.exception(f"Error processing message key={key}: {e}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        logger.info("Router worker shutdown gracefully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

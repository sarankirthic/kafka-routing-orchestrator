from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus
from sqlalchemy import select
from ..extensions import db, kafka_producer
from ..models import Customer, CustomerStatus

bp = Blueprint("customers", __name__)

@bp.get("")
def list_customers():
    # Filters: tenant_id, status, skill
    tenant_id = request.args.get("tenant_id")
    status = request.args.get("status")
    skill = request.args.get("skill")

    stmt = select(Customer)
    if tenant_id:
        stmt = stmt.where(Customer.tenant_id == tenant_id)
    if status:
        try:
            st = CustomerStatus(status)
            stmt = stmt.where(Customer.status == st)
        except ValueError:
            return jsonify({"error": "invalid status"}), HTTPStatus.BAD_REQUEST
    if skill:
        stmt = stmt.where(Customer.requested_skill.ilike(f"%{skill}%"))

    customers = db.session.execute(stmt).scalars().all()
    return jsonify([c.to_dict() for c in customers]), HTTPStatus.OK

@bp.post("/route")
def enqueue_route_request():
    # Body: { customer_id, tenant_id, requested_skill?, priority?, correlation_id? }
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    tenant_id = data.get("tenant_id")
    if not customer_id or not tenant_id:
        return jsonify({"error": "customer_id and tenant_id are required"}), HTTPStatus.BAD_REQUEST

    requested_skill = data.get("requested_skill")
    priority = int(data.get("priority") or 0)
    correlation_id = data.get("correlation_id")

    # Upsert customer row (Queued)
    existing: Customer | None = db.session.execute(
        select(Customer).where(Customer.customer_id == customer_id, Customer.tenant_id == tenant_id)
    ).scalars().first()

    if existing is None:
        cust = Customer(
            customer_id=customer_id,
            tenant_id=tenant_id,
            requested_skill=requested_skill,
            priority=priority,
            status=CustomerStatus.QUEUED,
        )
        db.session.add(cust)
    else:
        existing.requested_skill = requested_skill or existing.requested_skill
        existing.priority = priority
        existing.status = CustomerStatus.QUEUED
    db.session.commit()

    # Produce routing request keyed by customer_id
    topic = current_app.config["TOPIC_ROUTING_REQUESTS"]
    value = {
        "customer_id": customer_id,
        "tenant_id": tenant_id,
        "requested_skill": requested_skill,
        "priority": priority,
        "correlation_id": correlation_id,
    }

    def _delivery(err, msg):
        # Optional: log or metric on delivery outcome
        pass

    try:
        producer = kafka_producer.producer
        # Simple JSON serialization; replace with schema if needed
        import json
        producer.produce(
            topic=topic,
            key=customer_id.encode("utf-8"),
            value=json.dumps(value).encode("utf-8"),
            on_delivery=_delivery,
        )
        producer.poll(0)  # trigger delivery callbacks
    except Exception as e:
        # Do not fail the API if Kafka is temporarily unavailable; caller can retry
        return jsonify({"status": "enqueued_failed", "error": str(e)}), HTTPStatus.ACCEPTED

    return jsonify({"status": "enqueued", "topic": topic, "customer_id": customer_id}), HTTPStatus.ACCEPTED

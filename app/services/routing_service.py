import json
import random
from datetime import datetime
from http import HTTPStatus
from sqlalchemy import select
from ..extensions import db, redis_client, kafka_producer
from ..models import Agent, Assignment, Customer, CustomerStatus


class RoutingService:
    """Handles customer-to-agent assignment logic and Kafka event dispatch."""

    @staticmethod
    def assign_customer(customer_id: str, tenant_id: str, requested_skill=None, topic=None):
        """Select an agent for a given customer and emit to Kafka."""
        # Step 1: Retrieve eligible agents (available or least loaded)
        available_agents = RoutingService._get_available_agents(tenant_id, requested_skill)
        if not available_agents:
            return {"status": "no_agents_available"}, HTTPStatus.ACCEPTED

        # Step 2: Simple load-balancing - pick the least loaded or random
        agent = min(available_agents, key=lambda a: a.get("current_load", 0) or 0)

        # Step 3: Atomically reserve the agent
        if not RoutingService._reserve_agent(agent["agent_id"], tenant_id):
            return {"status": "reservation_conflict_retry"}, HTTPStatus.CONFLICT

        # Step 4: Persist assignment
        assignment = Assignment(
            customer_uid=customer_id,
            agent_uid=agent["agent_id"],
            tenant_id=tenant_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(assignment)
        RoutingService._mark_customer_in_progress(customer_id, tenant_id)
        db.session.commit()

        # Step 5: Emit Kafka event for confirmation
        topic = topic or "customer.assignments"
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "agent_id": agent["agent_id"],
            "status": "assigned",
        }

        producer = kafka_producer.producer
        producer.produce(topic, key=customer_id.encode(), value=json.dumps(payload).encode())
        producer.poll(0)

        return {"status": "assigned", "agent": agent}, HTTPStatus.OK

    @staticmethod
    def _get_available_agents(tenant_id, skill=None):
        """Retrieve available agents from Redis or DB fallback."""
        r = redis_client.client
        pattern = f"agent:{tenant_id}:*"
        agents = []
        for key in r.scan_iter(match=pattern):
            info = r.hgetall(key)
            if info.get("status") != "available":
                continue
            if skill and skill not in (info.get("skills") or ""):
                continue
            try:
                info["current_load"] = int(info.get("current_load", 0))
            except ValueError:
                info["current_load"] = 0
            agents.append(info)
        # Fallback to DB if Redis empty
        if not agents:
            rows = db.session.execute(
                select(Agent).where(Agent.tenant_id == tenant_id, Agent.status == "available")
            ).scalars().all()
            agents = [a.to_dict() for a in rows]
        return agents

    @staticmethod
    def _reserve_agent(agent_id: str, tenant_id: str) -> bool:
        """Optimistic reservation to prevent two customers claiming same agent."""
        r = redis_client.client
        key = f"lock:agent:{tenant_id}:{agent_id}"
        # Use Redis SETNX pattern
        success = r.set(name=key, value="locked", nx=True, ex=30)
        return bool(success)

    @staticmethod
    def _mark_customer_in_progress(customer_id: str, tenant_id: str):
        """Mark customer as being served."""
        cust = db.session.execute(
            select(Customer).where(Customer.customer_id == customer_id, Customer.tenant_id == tenant_id)
        ).scalars().first()
        if cust:
            cust.status = CustomerStatus.IN_PROGRESS
            cust.updated_at = datetime.utcnow()

from datetime import datetime
from sqlalchemy import select
from ..extensions import db, redis_client
from ..models import Agent, AgentStatus


class AgentService:
    """Provides business logic for managing agents and their presence/load tracking."""

    @staticmethod
    def list_agents(tenant_id=None, skill=None, status=None):
        stmt = select(Agent)
        if tenant_id:
            stmt = stmt.where(Agent.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Agent.status == status)
        if skill:
            stmt = stmt.where(Agent.skills.ilike(f"%{skill}%"))
        return db.session.execute(stmt).scalars().all()

    @staticmethod
    def upsert_agent(agent_id, tenant_id, status, skills=None, current_load=None):
        """Create or update an agent’s status and store state in Redis for low-latency lookups."""
        agent = db.session.execute(
            select(Agent).where(Agent.agent_id == agent_id, Agent.tenant_id == tenant_id)
        ).scalars().first()

        if agent is None:
            agent = Agent(agent_id=agent_id, tenant_id=tenant_id)
            db.session.add(agent)

        agent.status = AgentStatus(status)
        agent.skills = skills or agent.skills
        if current_load is not None and isinstance(current_load, int):
            agent.current_load = max(current_load, 0)
        agent.updated_at = datetime.utcnow()

        db.session.commit()

        # Mirror state in Redis for real-time consumption by routers/workers
        try:
            r = redis_client.client
            key = f"agent:{tenant_id}:{agent_id}"
            r.hset(key, mapping={
                "status": agent.status.value,
                "skills": agent.skills or "",
                "current_load": str(agent.current_load),
                "updated_at": agent.updated_at.isoformat(),
            })
            r.expire(key, 300)
        except Exception:
            # Non-critical: worker will rely on DB if cache fails
            pass

        return agent

    @staticmethod
    def get_agent(agent_id, tenant_id):
        """Fetch agent info from Redis if possible, otherwise DB."""
        r = redis_client.client
        key = f"agent:{tenant_id}:{agent_id}"
        data = r.hgetall(key)
        if data:
            data["cached"] = True
            return data
        agent = db.session.execute(
            select(Agent).where(Agent.agent_id == agent_id, Agent.tenant_id == tenant_id)
        ).scalars().first()
        return agent.to_dict() if agent else None

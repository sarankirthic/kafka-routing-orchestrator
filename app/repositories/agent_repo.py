from sqlalchemy import select
from ..extensions import db
from ..models import Agent, AgentStatus


class AgentRepository:
    """Repository for Agent model operations."""

    def add(self, agent: Agent):
        db.session.add(agent)
        db.session.commit()
        return agent

    def get_by_id(self, id_: int):
        return db.session.get(Agent, id_)

    def get_by_agent_id(self, agent_id: str, tenant_id: str):
        stmt = select(Agent).where(
            Agent.agent_id == agent_id,
            Agent.tenant_id == tenant_id
        )
        return db.session.execute(stmt).scalars().first()

    def list_all(self, tenant_id=None, status=None, skill=None):
        stmt = select(Agent)
        if tenant_id:
            stmt = stmt.where(Agent.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Agent.status == AgentStatus(status))
        if skill:
            stmt = stmt.where(Agent.skills.ilike(f"%{skill}%"))
        return db.session.execute(stmt).scalars().all()

    def update_status(self, agent_id: str, tenant_id: str, status: AgentStatus):
        agent = self.get_by_agent_id(agent_id, tenant_id)
        if not agent:
            return None
        agent.status = status
        db.session.commit()
        return agent

    def delete_by_agent_id(self, agent_id: str, tenant_id: str):
        agent = self.get_by_agent_id(agent_id, tenant_id)
        if agent:
            db.session.delete(agent)
            db.session.commit()
            return True
        return False

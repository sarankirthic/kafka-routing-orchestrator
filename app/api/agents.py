# app/api/agents.py
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from sqlalchemy import select
from ..extensions import db, redis_client
from ..models import Agent, AgentStatus

bp = Blueprint("agents", __name__)


@bp.get("")
def list_agents():
    # Filters: tenant_id, status, skill
    tenant_id = request.args.get("tenant_id")
    status = request.args.get("status")
    skill = request.args.get("skill")

    stmt = select(Agent)
    if tenant_id:
        stmt = stmt.where(Agent.tenant_id == tenant_id)
    if status:
        try:
            st = AgentStatus(status)
            stmt = stmt.where(Agent.status == st)
        except ValueError:
            return jsonify({"error": "invalid status"}), HTTPStatus.BAD_REQUEST
    if skill:
        # naive skill matching; replace with JSON/ARRAY field if needed
        stmt = stmt.where(Agent.skills.ilike(f"%{skill}%"))

    agents = db.session.execute(stmt).scalars().all()
    return jsonify([a.to_dict() for a in agents]), HTTPStatus.OK


@bp.post("/status")
def upsert_agent_status():
    # Body: { agent_id, tenant_id, status, skills?, current_load? }
    data = request.get_json(silent=True) or {}
    agent_id = data.get("agent_id")
    tenant_id = data.get("tenant_id")
    status = data.get("status")

    if not agent_id or not tenant_id or not status:
        return jsonify({"error": "agent_id, tenant_id, status are required"}), HTTPStatus.BAD_REQUEST
    try:
        status_enum = AgentStatus(status)
    except ValueError:
        return jsonify({"error": "invalid status"}), HTTPStatus.BAD_REQUEST

    skills = data.get("skills")
    current_load = data.get("current_load")

    agent: Agent | None = db.session.execute(
        select(Agent).where(Agent.agent_id == agent_id, Agent.tenant_id == tenant_id)
    ).scalars().first()

    if agent is None:
        agent = Agent(agent_id=agent_id, tenant_id=tenant_id)
        db.session.add(agent)

    agent.status = status_enum
    if skills is not None:
        agent.skills = skills
    if isinstance(current_load, int) and current_load >= 0:
        agent.current_load = current_load

    db.session.commit()

    # Optional: reflect presence in Redis cache for fast worker reads
    try:
        r = redis_client.client
        r.hset(f"agent:{tenant_id}:{agent_id}", mapping={
            "status": agent.status.value,
            "skills": agent.skills or "",
            "current_load": str(agent.current_load),
        })
    except Exception as e:
        print(e)

    return jsonify(agent.to_dict()), HTTPStatus.OK

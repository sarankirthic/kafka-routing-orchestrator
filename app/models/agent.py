from enum import Enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class Agent(db.Model):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    skills: Mapped[str] = mapped_column(String(256), nullable=True)  # comma-separated or JSON in a text field
    status: Mapped[AgentStatus] = mapped_column(SAEnum(AgentStatus), default=AgentStatus.OFFLINE, nullable=False)
    current_load: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "skills": self.skills,
            "status": self.status.value,
            "current_load": self.current_load,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

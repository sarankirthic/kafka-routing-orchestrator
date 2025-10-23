from typing import Optional
from pydantic import BaseModel, Field, constr
from enum import Enum


class AgentStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"


class AgentCreate(BaseModel):
    agent_id: constr(min_length=2, max_length=64)
    tenant_id: constr(min_length=1, max_length=64)
    skills: Optional[str] = Field(None, description="Comma-separated skills")
    status: AgentStatus = Field(default=AgentStatus.offline, description="Initial agent status")
    current_load: int = Field(default=0, ge=0, description="Number of active customers")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "A1001",
                "tenant_id": "T001",
                "skills": "billing,support",
                "status": "available",
                "current_load": 0,
            }
        }


class AgentUpdate(BaseModel):
    status: Optional[AgentStatus]
    skills: Optional[str]
    current_load: Optional[int] = Field(default=None, ge=0)


class AgentResponse(BaseModel):
    agent_id: str
    tenant_id: str
    skills: Optional[str]
    status: AgentStatus
    current_load: int

    class Config:
        orm_mode = True

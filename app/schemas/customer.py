from typing import Optional
from pydantic import BaseModel, Field, constr
from enum import Enum


class CustomerStatus(str, Enum):
    queued = "queued"
    in_progress = "in_progress"
    completed = "completed"


class CustomerCreate(BaseModel):
    customer_id: constr(min_length=2, max_length=64)
    tenant_id: constr(min_length=1, max_length=64)
    requested_skill: Optional[str] = Field(None, description="Skill required for routing")
    priority: int = Field(default=0, ge=0)
    status: CustomerStatus = Field(default=CustomerStatus.queued)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "C5678",
                "tenant_id": "T001",
                "requested_skill": "billing",
                "priority": 1,
                "status": "queued",
            }
        }


class CustomerResponse(BaseModel):
    customer_id: str
    tenant_id: str
    requested_skill: Optional[str]
    priority: int
    status: CustomerStatus

    class Config:
        orm_mode = True

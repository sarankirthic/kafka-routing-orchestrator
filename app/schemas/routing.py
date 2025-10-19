from typing import Optional
from pydantic import BaseModel, Field, constr


class RoutingRequest(BaseModel):
    customer_id: constr(min_length=2, max_length=64)
    tenant_id: constr(min_length=1, max_length=64)
    requested_skill: Optional[str] = Field(None, description="Routing skill preference")
    priority: int = Field(default=0, ge=0)
    correlation_id: Optional[str] = Field(None, description="Trace across systems")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "C1234",
                "tenant_id": "T001",
                "requested_skill": "support",
                "priority": 2,
                "correlation_id": "abcd-efgh-1234",
            }
        }


class RoutingResponse(BaseModel):
    status: str = Field(..., description="Routing status, e.g. assigned or queued")
    agent_id: Optional[str] = Field(None, description="Assigned agent if available")
    tenant_id: str
    customer_id: str

    class Config:
        orm_mode = True

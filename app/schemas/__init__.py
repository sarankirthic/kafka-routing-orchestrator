"""
Pydantic data models (DTOs) for request validation and response serialization.
Used by Flask endpoints and services.

Each schema enforces type safety, required fields, and minimal defaults.
"""
from .agent import AgentCreate, AgentUpdate, AgentResponse
from .customer import CustomerCreate, CustomerResponse
from .routing import RoutingRequest, RoutingResponse

__all__ = [
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "CustomerCreate",
    "CustomerResponse",
    "RoutingRequest",
    "RoutingResponse",
]

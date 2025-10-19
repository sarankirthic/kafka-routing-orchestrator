"""
Repository layer implementing persistence encapsulation for domain models.

Provides:
- Common CRUD operations (BaseRepository)
- Model-specific repositories (AgentRepository, CustomerRepository, AssignmentRepository)
"""
from .agent_repo import AgentRepository
from .customer_repo import CustomerRepository
from .assignment_repo import AssignmentRepository

__all__ = ["AgentRepository", "CustomerRepository", "AssignmentRepository"]

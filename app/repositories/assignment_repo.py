from sqlalchemy import select
from ..extensions import db
from ..models import Assignment


class AssignmentRepository:
    """Repository for managing customer-agent assignments."""

    def add(self, assignment: Assignment):
        """Insert a new assignment."""
        db.session.add(assignment)
        db.session.commit()
        return assignment

    def get_by_customer_uid(self, customer_uid: str, tenant_id: str):
        stmt = select(Assignment).where(
            Assignment.customer_uid == customer_uid,
            Assignment.tenant_id == tenant_id
        )
        return db.session.execute(stmt).scalars().first()

    def list_all(self, tenant_id=None):
        stmt = select(Assignment)
        if tenant_id:
            stmt = stmt.where(Assignment.tenant_id == tenant_id)
        return db.session.execute(stmt).scalars().all()

    def update_agent_mapping(self, customer_uid: str, tenant_id: str, new_agent_uid: str):
        assignment = self.get_by_customer_uid(customer_uid, tenant_id)
        if not assignment:
            return None
        assignment.agent_uid = new_agent_uid
        db.session.commit()
        return assignment

    def delete_by_customer_uid(self, customer_uid: str, tenant_id: str):
        assignment = self.get_by_customer_uid(customer_uid, tenant_id)
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return True
        return False

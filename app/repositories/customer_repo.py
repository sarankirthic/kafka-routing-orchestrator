from sqlalchemy import select
from ..extensions import db
from ..models import Customer, CustomerStatus


class CustomerRepository:
    """Repository for Customer model operations."""

    def add(self, customer: Customer):
        db.session.add(customer)
        db.session.commit()
        return customer

    def get_by_id(self, id_: int):
        return db.session.get(Customer, id_)

    def get_by_customer_id(self, customer_id: str, tenant_id: str):
        stmt = select(Customer).where(
            Customer.customer_id == customer_id,
            Customer.tenant_id == tenant_id
        )
        return db.session.execute(stmt).scalars().first()

    def list_all(self, tenant_id=None, status=None):
        stmt = select(Customer)
        if tenant_id:
            stmt = stmt.where(Customer.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Customer.status == CustomerStatus(status))
        return db.session.execute(stmt).scalars().all()

    def update_status(self, customer_id: str, tenant_id: str, new_status: CustomerStatus):
        cust = self.get_by_customer_id(customer_id, tenant_id)
        if not cust:
            return None
        cust.status = new_status
        db.session.commit()
        return cust

    def delete_by_customer_id(self, customer_id: str, tenant_id: str):
        cust = self.get_by_customer_id(customer_id, tenant_id)
        if cust:
            db.session.delete(cust)
            db.session.commit()
            return True
        return False

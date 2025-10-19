from app import create_app
from app.extensions import db
from app.models.agent import Agent, AgentStatus
from app.models.customer import Customer, CustomerStatus


def main():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        # Seed example agents with diverse skills and statuses
        agents = [
            Agent(agent_id="agent001", tenant_id="tenant01", skills="billing,support", status=AgentStatus.AVAILABLE, current_load=0),
            Agent(agent_id="agent002", tenant_id="tenant01", skills="support", status=AgentStatus.BUSY, current_load=2),
            Agent(agent_id="agent101", tenant_id="tenant02", skills="sales", status=AgentStatus.AVAILABLE),
        ]

        # Seed example customers waiting for routing
        customers = [
            Customer(customer_id="cust001", tenant_id="tenant01", requested_skill="billing", status=CustomerStatus.QUEUED, priority=1),
            Customer(customer_id="cust002", tenant_id="tenant01", requested_skill="support", status=CustomerStatus.QUEUED, priority=0),
            Customer(customer_id="cust100", tenant_id="tenant02", requested_skill="sales", status=CustomerStatus.QUEUED, priority=0),
        ]

        db.session.bulk_save_objects(agents + customers)
        db.session.commit()
        print(f"Seeded {len(agents)} agents and {len(customers)} customers.")


if __name__ == "__main__":
    main()

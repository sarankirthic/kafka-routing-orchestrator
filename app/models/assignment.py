from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class Assignment(db.Model):
    __tablename__ = "assignments"
    __table_args__ = (
        UniqueConstraint("customer_id", name="uq_assignments_customer_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Business identifiers (not FK) for idempotent upserts by app logic
    customer_uid: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # same as Customer.customer_id
    agent_uid: Mapped[str] = mapped_column(String(64), index=True, nullable=False)      # same as Agent.agent_id
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    # Optional relational links for convenience
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)

    customer = relationship("Customer", lazy="joined")
    agent = relationship("Agent", lazy="joined")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_uid": self.customer_uid,
            "agent_uid": self.agent_uid,
            "tenant_id": self.tenant_id,
            "customer_id": self.customer_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

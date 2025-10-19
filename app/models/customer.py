from enum import Enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class CustomerStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Customer(db.Model):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    requested_skill: Mapped[str] = mapped_column(String(64), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[CustomerStatus] = mapped_column(SAEnum(CustomerStatus), default=CustomerStatus.QUEUED, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "tenant_id": self.tenant_id,
            "requested_skill": self.requested_skill,
            "priority": self.priority,
            "status": self.status.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

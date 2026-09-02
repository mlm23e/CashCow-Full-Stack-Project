"""
CashCow Command Center
Service Call Model - Refill/repair tasks assigned to ATMs
"""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ServicePriority, ServiceStatus

if TYPE_CHECKING:
    from .atm import ATM
    from .diagnostic_report import DiagnosticReport


class ServiceCall(Base):
    __tablename__ = "service_calls"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    priority: Mapped[ServicePriority] = mapped_column(
        SQLEnum(
            ServicePriority, 
            name = "service_priority",
            values_callable = lambda enum_cls : [member.value for member in enum_cls]
        ),
        nullable=False
    )

    status: Mapped[ServiceStatus] = mapped_column(
        SQLEnum(
            ServiceStatus,
            name = "service_status",
            values_callable = lambda enum_cls : [member.value for member in enum_cls]
        ),
        nullable=False,
        default = ServiceStatus.PENDING
    )

    atm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("atms.id"),
        ondelete="CASCADE",
        nullable=False
    )

    technician_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    started_at: Mapped[datetime | None] = mapped_column(DateTime)

    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # ATM associated with service call
    atm: Mapped["ATM"] = relationship(back_populates="service_calls")

    # Diagnostic reports attached to call
    diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(
        back_populates="service_call"
    )

    def __repr__(self) -> str:
        return (f"ServiceCall(id={self.id}, "
                f"title={self.title!r}, "
                f"priority={self.priority.value}, "
                f"status={self.status.value}, "
                f"atm_id={self.atm_id}, "
                f"technician_id={self.technician_id})")
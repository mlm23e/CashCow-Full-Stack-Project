from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .atm import ATM
    from .user import User
    from .diagnostic_report import DiagnosticReport


class ServiceCall(Base):
    __tablename__ = "service_calls"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Medium"
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Pending"
    )

    atm_id: Mapped[int] = mapped_column(
        ForeignKey("atms.id"),
        nullable=False
    )

    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    # ATM associated with service call
    atm: Mapped["ATM"] = relationship(
        "ATM",
        back_populates="service_calls"
    )

    # Technician assigned to service call
    technician: Mapped["User | None"] = relationship(
        "User",
        back_populates="service_calls"
    )

    # Diagnostic reports attached to call
    diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(
        "DiagnosticReport",
        back_populates="service_call",
        cascade="all, delete-orphan"
    )
"""
CashCow Command Center
Diagnostic Report Model - Maintenance attachments and inspection files
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from .base import Base
from .service_call import ServiceCall

from sqlalchemy import ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DiagnosticReport(Base):
    id : Mapped[int] = mapped_column(Integer, primary_key=True)

    file_url : Mapped[str] = mapped_column(Text)

    notes : Mapped[str] = mapped_column(Text, nullable=True)

    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    service : Mapped["ServiceCall"] = relationship(back_populates="service_calls")

    def __repr__(self) -> str:
        return (f"DiagnosticReport(id={self.id}, "
                f"file_url={self.file_url!r}, "
                f"notes={self.notes!r}, "
                f"created_at={self.created_at})")
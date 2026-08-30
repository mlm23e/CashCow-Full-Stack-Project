"""
CashCow Command Center
Branch Model - Physical sites housing ATM pools
"""

from __future__ import annotations # postpone type evaluations until runtime
from typing import TYPE_CHECKING

from decimal import Decimal

from sqlalchemy import ForeignKey, String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .atm import ATM


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    location_region: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    supervisor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id")
    )

    # ATMs physically located at this branch
    atms: Mapped[list["ATM"]] = relationship(back_populates="branch")

    def __repr__(self) -> str:
        return (f" Branch(id={self.id}, "
                f"name={self.name!r}, "
                f"location_region={self.location_region!r})")
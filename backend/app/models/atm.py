"""
CashCow Command Center
ATM Model - Individual cash machine units
"""

from __future__ import annotations # postpone type evaluations until runtime
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enums import ATMStatus

if TYPE_CHECKING:
    from .branch import Branch
    from .service_call import ServiceCall


class ATM(Base):
    __tablename__ = "atms"

    __table_args__ = (
        CheckConstraint(
            "cash_level BETWEEN 0 AND 100",
            name="cash_level_range"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    atm_status: Mapped[ATMStatus] = mapped_column(
        SQLEnum(
            ATMStatus,
            name = "atm_status",
            values_callable = lambda enum_cls : [member.value for member in enum_cls]
        ),
        default = ATMStatus.OPERATIONAL
    )

    cash_level: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=100
    )

    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id"),
        nullable=False
    )
    
    # Service calls associated with this ATM
    service_calls: Mapped[list["ServiceCall"]] = relationship(
        back_populates="atm",
        passive_deletes=True
    )

    # Physical branch
    branch: Mapped["Branch"] = relationship(
        back_populates="atms"
    )

    LOW_CASH_THRESHOLD = 20

    def is_low_on_cash(self, threshold : int | None = None) -> bool:
        low_limit = threshold if threshold is not None else ATM.LOW_CASH_THRESHOLD
        return self.cash_level < low_limit


    def __repr__(self) -> str:
        return (f"ATM(id={self.id}, "
                f"serial_number={self.serial_number!r}, "
                f"model={self.model!r}, "
                f"status={self.status.value}, "
                f"cash_level={self.cash_level}, "
                f"branch_id={self.branch_id})")
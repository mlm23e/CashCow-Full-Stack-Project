from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .branch import Branch
    from .service_call import ServiceCall


class ATM(Base):
    __tablename__ = "atms"

    __table_args__ = (
        CheckConstraint(
            "cash_level >= 0 AND cash_level <= 100",
            name="cash_level_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Operational"
    )

    cash_level: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=100
    )

    facility_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id"),
        nullable=False
    )

    # Physical branch
    branch: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="atms"
    )

    # Service calls associated with this ATM
    service_calls: Mapped[list["ServiceCall"]] = relationship(
        "ServiceCall",
        back_populates="atm"
    )
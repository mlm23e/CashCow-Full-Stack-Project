from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .atm import ATMsourc


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    location_region: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        nullable=False
    )

    supervisor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    # Regional Operations Supervisor
    supervisor: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[supervisor_id],
        back_populates="supervised_branches"
    )

    # Users assigned to this branch
    technicians: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys="User.branch_id",
        back_populates="branch"
    )

    # ATMs physically located at this branch
    atms: Mapped[list["ATM"]] = relationship(
        "ATM",
        back_populates="branch"
    )
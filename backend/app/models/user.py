from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .branch import Branch
    from .service_call import ServiceCall


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        nullable=False
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id"),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Technician's assigned/home branch
    branch: Mapped["Branch | None"] = relationship(
        "Branch",
        back_populates="technicians",
        foreign_keys=[branch_id]
    )

    supervised_branches: Mapped[list["Branch"]] = relationship(
    "Branch",
    foreign_keys="Branch.supervisor_id",
    back_populates="supervisor"
    )

    # Service calls assigned to this user
    service_calls: Mapped[list["ServiceCall"]] = relationship(
        "ServiceCall",
        back_populates="technician"
    )

    
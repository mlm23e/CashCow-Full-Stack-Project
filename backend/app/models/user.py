"""
CashCow Command Center
User model -- used for RBAC
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Boolean, ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import UserRole

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        Text,
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

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls : [member.value for member in enum_cls]
        ),
        nullable=False
    )

    branch_id : Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True
    )

    def __repr__(self) -> str:
        return (f"User(id={self.id}, "
                f"username={self.username!r}, "
                f"role={self.role.value})")
    
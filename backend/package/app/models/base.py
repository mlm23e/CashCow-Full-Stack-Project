"""
CashCow Command Center

Shared declarative Base class for every 
object relational mapping (ORM) model
to inherit from
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
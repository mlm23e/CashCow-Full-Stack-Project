"""
CashCow Command Center
Pydantic v2 Schema for ATM resource
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import ATMStatus

class ATMBase(BaseModel):
    serial_number : str = Field(min_length=1, max_length=100)
    model : str = Field(min_length=1, max_length=100)
    atm_status : ATMStatus = ATMStatus.OPERATIONAL
    cash_level : Decimal = Field(ge=0, le=100)
    branch_id : int

class ATMCreate(ATMBase):
    """Shape of request body for POST /atms"""

class ATMRead(ATMBase):
    """Shape of an ATM in any API response"""
    id : int
    model_config = ConfigDict(from_attributes=True)

class ATMUpdate(BaseModel):
    serial_number: str | None = Field(default=None, min_length=1, max_length=100)
    mode: str | None = Field(default=None, min_length=1, max_length=100)
    status: ATMStatus | None = None
    cash_level: Decimal | None = Field(default=None, ge=0, le=100)
    facility_id: int | None = None
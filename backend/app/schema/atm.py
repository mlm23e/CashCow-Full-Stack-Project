from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import ATMStatus

class ATMBase(BaseModel):
    serial_number : str = Field(min_length=1, max_length=100)
    mode : str = Field(min_length=1, max_length=100)
    status : ATMStatus = ATMStatus.OPERATIONAL
    cash_level : Decimal = Field(ge=0, le=100)
    facility_id : int

class ATMCreate(ATMBase):
    """Shape of request body for POST /atms"""

class ATMRead(ATMBase):
    """Shape of an ATM in any API response"""
    id : int
    model_config = ConfigDict(from_attributes=True)
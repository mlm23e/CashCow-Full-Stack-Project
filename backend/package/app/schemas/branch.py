from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

class BranchBase(BaseModel):
    name : str = Field(min_length=1, max_length=150)
    location_region : str = Field(min_length=1, max_length=100)
    capacity : int = Field(ge=0)
    supervisor_id : int | None = None

class BranchCreate(BranchBase):
    """Shape of body for POST /branches"""

class BranchRead(BranchBase):
    id : int
    model_config = ConfigDict(from_attributes=True)

class BranchUpdate(BranchBase):
    name : str | None = Field(default=None, min_length=1, max_length=150)
    location_region : str | None = Field(default=None, min_length=1, max_length=100)
    capacity : int | None = None
    supervisor_id : int | None = None

class MaintenanceFlagRead(BaseModel):
    id : int
    name : str
    atm_total : int
    maintenance_atms : int
    maintenance_rate : float
    
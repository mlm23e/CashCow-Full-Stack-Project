"""
CashCow Command Center
Pydantic v2 Schema for ServiceCall resource
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.models.service_call import ServiceStatus, ServicePriority

class ServiceBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    priority: ServicePriority
    atm_id: int
    technician_id: int | None = None
    status: ServiceStatus = ServiceStatus.PENDING

class ServiceCreate(ServiceBase):
    """Shape of body for POST /service_calls"""

class ServiceRead(BaseModel):
    id : int 
    title : str
    priority : ServicePriority
    status : ServiceStatus
    atm_id : int 
    technician_id : int | None
    completed_at : datetime | None
    model_config = ConfigDict(from_attributes=True)

class DiscrepancyRead(BaseModel):
    service_id: int
    title: str
    atm_id : int
    atm_branch_id : int
    technician_id : int
    technician_branch_id: int

    # Since we expect this coming back from our ORM
    model_config = ConfigDict(from_attributes=True)
    # Allows us to create a DiscrepancyRead Object from an object with the exact same attributes

class ServiceStatusUpdate(BaseModel):
    status : ServiceStatus

class ServiceUpdate(BaseModel):
    title : str | None = Field(default=None, min_length=1, max_length=255)
    priority : ServicePriority | None = None
    technician_id : int | None = None
    status : ServiceStatus | None = None

class ATMReliabilityRead(BaseModel):
    model: str
    total_calls: int
    completed_calls: int
    failed_calls: int
    completion_rate: Decimal = Field(ge=0, le=100)
    failure_rate: Decimal = Field(ge=0, le=100)
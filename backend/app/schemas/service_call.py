"""
CashCow Command Center
Pydantic v2 Schema for ServiceCall resource
"""

from pydantic import BaseModel, ConfigDict
from app.models.service_call import ServiceStatus, ServicePriority

class DiscrepancyRead(BaseModel):
    service_id: int
    title: str
    atm_facility_id: int
    technician_facility_id: int

    # Since we expect this coming back from our ORM
    model_config = ConfigDict(from_attributes=True)
    # Allows us to create a DiscrepancyRead Object from an object with the exact same attributes

class ServiceStatusUpdate(BaseModel):
    status : ServiceStatus

class ServiceRead(BaseModel):
    id : int 
    title : str
    priority : ServicePriority
    status : ServiceStatus
    atm_id : int 
    technician_id : int
    model_config = ConfigDict(from_attributes=True)
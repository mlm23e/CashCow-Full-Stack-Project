from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class DiagnosticReportBase(BaseModel):
    service_call_id: int
    file_url : str = Field(min_length=1)
    notes : str | None = None

class DiagnosticReportCreate(DiagnosticReportBase):
    """shape of body for POST /diagnostic_reports"""

class DiagnosticReportRead(DiagnosticReportBase):
    id : int
    created_at : datetime | None
    model_config = ConfigDict(from_attributes=True)

class DiagnosticReportUpdate(BaseModel):
    service_call_id : int | None = None
    file_url : str | None = Field(default=None, min_length=1)
    notes : str | None = None
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    recovery_case_id: Optional[int] = None
    event_type: str
    description: str
    actor: str = "SYSTEM"
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="metadata_")


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(BaseModel):
    id: int
    recovery_case_id: Optional[int] = None
    event_type: str
    description: str
    actor: str
    metadata_: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

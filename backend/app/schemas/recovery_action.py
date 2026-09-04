from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import RecoveryActionType, ActionExecutionStatus


class RecoveryActionBase(BaseModel):
    recovery_case_id: int
    action_type: RecoveryActionType
    reason: Optional[str] = None
    status: ActionExecutionStatus = ActionExecutionStatus.PENDING
    result: Optional[str] = None
    recovered_amount: Decimal = Decimal("0.00")


class RecoveryActionCreate(RecoveryActionBase):
    pass


class RecoveryActionRead(RecoveryActionBase):
    id: int
    executed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

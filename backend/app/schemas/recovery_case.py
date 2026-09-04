from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import RecoveryCaseStatus
from app.schemas.payment import PaymentRead
from app.schemas.recovery_action import RecoveryActionRead


class RecoveryCaseBase(BaseModel):
    payment_id: int
    revenue_at_risk: Decimal
    recoverability_score: float = 0.0
    diagnosis: Optional[str] = None
    recommended_action: Optional[str] = None
    status: RecoveryCaseStatus = RecoveryCaseStatus.OPEN
    recovered_amount: Decimal = Decimal("0.00")
    ai_diagnosis: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_summary: Optional[str] = None
    ai_evidence: Optional[List[dict]] = None
    ai_recommended_action: Optional[str] = None
    policy_result: Optional[str] = None
    final_action: Optional[str] = None
    escalation_required: bool = False


class RecoveryCaseCreate(RecoveryCaseBase):
    pass


class RecoveryCaseRead(RecoveryCaseBase):
    id: int
    payment: Optional[PaymentRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecoveryCaseDetail(RecoveryCaseRead):
    payment: Optional[PaymentRead] = None
    recovery_actions: List[RecoveryActionRead] = []

    model_config = ConfigDict(from_attributes=True)

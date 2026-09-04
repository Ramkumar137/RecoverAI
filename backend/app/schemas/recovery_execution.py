from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RecoveryExecutionResponse(BaseModel):
    case_id: int
    payment_id: str
    action: str
    status: str
    previous_amount: float
    recovered_amount: float
    retry_count: int
    idempotent: bool
    message: str


class BatchRecoveryResponse(BaseModel):
    cases_processed: int
    actions_executed: int
    payments_recovered: int
    payments_failed: int
    escalated: int
    stopped: int
    revenue_at_risk: float
    potentially_recoverable: float
    recovered_revenue: float
    recovery_rate: float


class AnalyticsOverviewResponse(BaseModel):
    revenue_at_risk: float
    potentially_recoverable: float
    recovered_revenue: float
    recovery_rate: float
    active_cases: int
    recovered_cases: int
    escalated_cases: int
    stopped_cases: int


class RecoveryTrendItem(BaseModel):
    date: str
    revenue_at_risk: float
    recovered: float


class ActionBreakdownItem(BaseModel):
    action: str
    attempts: int
    successful: int
    recovered_amount: float


class FailureBreakdownItem(BaseModel):
    failure_reason: str
    count: int
    amount_at_risk: float
    recovered_amount: float
    recovery_rate: float


class TimelineEventItem(BaseModel):
    event: str
    timestamp: Optional[str] = None
    actor: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

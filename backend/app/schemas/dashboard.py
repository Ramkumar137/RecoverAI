from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class KpiMetrics(BaseModel):
    revenue_at_risk: Decimal
    potentially_recoverable: Decimal
    recovered_revenue: Decimal
    recovery_rate: float
    total_cases: int
    active_cases: int


class RecoveryTrendPoint(BaseModel):
    date: str
    at_risk: float
    recovered: float


class ActionDistributionItem(BaseModel):
    action_type: str
    count: int
    percentage: float


class RecentCaseItem(BaseModel):
    id: int
    case_ref: str
    payment_ref: str
    customer_name: str
    amount: float
    failure_reason: Optional[str] = None
    recoverability_score: float
    recommended_action: Optional[str] = None
    status: str
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    kpis: KpiMetrics
    recovery_trends: List[RecoveryTrendPoint]
    action_distribution: List[ActionDistributionItem]
    recent_cases: List[RecentCaseItem]

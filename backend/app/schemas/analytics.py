from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class RevenueRiskAnalyticsResponse(BaseModel):
    revenue_at_risk: Decimal = Field(..., description="Total uncollected monetary amount currently at risk")
    potentially_recoverable: Decimal = Field(..., description="Estimated salvageable revenue based on recoverability scores")
    recovered_revenue: Decimal = Field(..., description="Monetary revenue successfully recovered")
    recovery_rate: float = Field(..., description="Percentage of at-risk revenue successfully recovered")
    failed_payments: int = Field(..., description="Count of failed transactions")
    abandoned_payments: int = Field(..., description="Count of abandoned checkouts")
    expired_payments: int = Field(default=0, description="Count of expired payment sessions")
    open_recovery_cases: int = Field(..., description="Count of active recovery cases currently open")
    recovered_cases: int = Field(..., description="Count of cases successfully resolved and recovered")
    escalated_cases: int = Field(..., description="Count of cases escalated to human operators")
    stopped_cases: int = Field(..., description="Count of cases where recovery was halted due to risk or fatigue")


class BatchAnalysisResponse(BaseModel):
    payments_analyzed: int = Field(..., description="Number of payments evaluated in this batch")
    revenue_at_risk: float = Field(..., description="Total revenue exposure across evaluated payments")
    potentially_recoverable: float = Field(..., description="Total salvageable revenue across evaluated payments")
    high_recoverability: int = Field(..., description="Cases with score >= 70%")
    medium_recoverability: int = Field(..., description="Cases with score 30% - 69%")
    low_recoverability: int = Field(..., description="Cases with score < 30%")

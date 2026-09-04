from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import RevenueRiskAnalyticsResponse
from app.schemas.recovery_execution import (
    AnalyticsOverviewResponse,
    RecoveryTrendItem,
    ActionBreakdownItem,
    FailureBreakdownItem,
)
from app.services.analytics_service import AnalyticsService
from app.services.recovery_analytics_service import RecoveryAnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Revenue Risk"])


@router.get(
    "/revenue-risk",
    response_model=RevenueRiskAnalyticsResponse,
    summary="Get revenue at risk metrics",
    description="Returns aggregate revenue at risk, potentially recoverable revenue, settled recovered revenue, recovery rate, and transaction status breakdown counts.",
)
def get_revenue_risk_analytics(
    db: Session = Depends(get_db),
) -> RevenueRiskAnalyticsResponse:
    return AnalyticsService.get_revenue_risk_metrics(db)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get high-level recovery overview KPIs",
    description="Returns aggregate revenue at risk, potentially recoverable, recovered revenue, recovery rate, and case counts.",
)
def get_recovery_overview(
    db: Session = Depends(get_db),
) -> AnalyticsOverviewResponse:
    return AnalyticsOverviewResponse(**RecoveryAnalyticsService.get_overview(db))


@router.get(
    "/recovery-trend",
    response_model=List[RecoveryTrendItem],
    summary="Get daily recovery trend data",
    description="Returns time-series data showing revenue at risk versus recovered revenue by day.",
)
def get_recovery_trend(
    days: int = Query(14, ge=1, le=90, description="Lookback window in days"),
    db: Session = Depends(get_db),
) -> List[RecoveryTrendItem]:
    data = RecoveryAnalyticsService.get_recovery_trend(db, days=days)
    return [RecoveryTrendItem(**item) for item in data]


@router.get(
    "/action-breakdown",
    response_model=List[ActionBreakdownItem],
    summary="Get breakdown by recovery action",
    description="Returns recovery performance grouped by action type (attempts, successful, recovered amount).",
)
def get_action_breakdown(
    db: Session = Depends(get_db),
) -> List[ActionBreakdownItem]:
    data = RecoveryAnalyticsService.get_action_breakdown(db)
    return [ActionBreakdownItem(**item) for item in data]


@router.get(
    "/failure-breakdown",
    response_model=List[FailureBreakdownItem],
    summary="Get breakdown by failure reason",
    description="Returns failure counts, amount at risk, recovered amount, and recovery rate grouped by failure reason.",
)
def get_failure_breakdown(
    db: Session = Depends(get_db),
) -> List[FailureBreakdownItem]:
    data = RecoveryAnalyticsService.get_failure_breakdown(db)
    return [FailureBreakdownItem(**item) for item in data]

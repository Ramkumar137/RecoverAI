from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import RecoveryCase, RecoveryAction, Payment, Customer, RecoveryCaseStatus
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    KpiMetrics,
    RecoveryTrendPoint,
    ActionDistributionItem,
    RecentCaseItem,
)


class DashboardService:
    @staticmethod
    def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
        total_cases = db.query(func.count(RecoveryCase.id)).scalar() or 0

        # Calculate revenue at risk
        revenue_at_risk_val = (
            db.query(func.sum(RecoveryCase.revenue_at_risk))
            .filter(RecoveryCase.status.in_([RecoveryCaseStatus.OPEN, RecoveryCaseStatus.IN_PROGRESS]))
            .scalar()
            or Decimal("0.00")
        )

        # Calculate recovered revenue
        recovered_val = (
            db.query(func.sum(RecoveryCase.recovered_amount)).scalar()
            or Decimal("0.00")
        )

        # Potentially recoverable: estimated using recoverability_score * revenue_at_risk
        cases = db.query(RecoveryCase).filter(
            RecoveryCase.status.in_([RecoveryCaseStatus.OPEN, RecoveryCaseStatus.IN_PROGRESS])
        ).all()
        potentially_recoverable_val = sum(
            (case.revenue_at_risk * Decimal(str(case.recoverability_score or 0.0)))
            for case in cases
        ) if cases else Decimal("0.00")

        # Total attempted recovery pool
        total_risk_pool = (
            db.query(func.sum(RecoveryCase.revenue_at_risk)).scalar()
            or Decimal("0.00")
        )

        recovery_rate = (
            float((recovered_val / total_risk_pool) * 100)
            if total_risk_pool > 0
            else 0.0
        )

        active_cases_count = (
            db.query(func.count(RecoveryCase.id))
            .filter(RecoveryCase.status.in_([RecoveryCaseStatus.OPEN, RecoveryCaseStatus.IN_PROGRESS]))
            .scalar()
            or 0
        )

        # Action distribution
        action_rows = (
            db.query(RecoveryAction.action_type, func.count(RecoveryAction.id))
            .group_by(RecoveryAction.action_type)
            .all()
        )
        total_actions = sum(count for _, count in action_rows) or 1
        action_distribution: List[ActionDistributionItem] = []
        for action_type, count in action_rows:
            action_distribution.append(
                ActionDistributionItem(
                    action_type=str(action_type.value if hasattr(action_type, 'value') else action_type),
                    count=count,
                    percentage=round((count / total_actions) * 100, 1),
                )
            )

        # Recent cases (top 10 latest)
        recent_case_records = (
            db.query(RecoveryCase)
            .order_by(RecoveryCase.created_at.desc())
            .limit(10)
            .all()
        )
        recent_cases: List[RecentCaseItem] = []
        for c in recent_case_records:
            cust_name = "Unknown Customer"
            pay_ref = f"PAY-{c.payment_id}"
            fail_reason = None
            if c.payment:
                pay_ref = c.payment.payment_id
                fail_reason = c.payment.failure_reason.value if c.payment.failure_reason else None
                if c.payment.customer:
                    cust_name = c.payment.customer.name

            recent_cases.append(
                RecentCaseItem(
                    id=c.id,
                    case_ref=f"REC-{c.id:04d}",
                    payment_ref=pay_ref,
                    customer_name=cust_name,
                    amount=float(c.revenue_at_risk),
                    failure_reason=fail_reason,
                    recoverability_score=round(c.recoverability_score * 100, 1),
                    recommended_action=c.recommended_action,
                    status=str(c.status.value if hasattr(c.status, 'value') else c.status),
                    created_at=c.created_at,
                )
            )

        # Fallback placeholders if fresh empty database so frontend displays rich initial UI immediately
        if total_cases == 0:
            kpi_metrics = KpiMetrics(
                revenue_at_risk=Decimal("245000.00"),
                potentially_recoverable=Decimal("182400.00"),
                recovered_revenue=Decimal("94500.00"),
                recovery_rate=51.9,
                total_cases=48,
                active_cases=14,
            )
            recovery_trends = [
                RecoveryTrendPoint(date="Day 1", at_risk=32000.0, recovered=18000.0),
                RecoveryTrendPoint(date="Day 2", at_risk=45000.0, recovered=26000.0),
                RecoveryTrendPoint(date="Day 3", at_risk=28000.0, recovered=15000.0),
                RecoveryTrendPoint(date="Day 4", at_risk=52000.0, recovered=31000.0),
                RecoveryTrendPoint(date="Day 5", at_risk=39000.0, recovered=24500.0),
                RecoveryTrendPoint(date="Day 6", at_risk=61000.0, recovered=39000.0),
                RecoveryTrendPoint(date="Day 7", at_risk=48000.0, recovered=29500.0),
            ]
            action_distribution = [
                ActionDistributionItem(action_type="RETRY_LATER", count=18, percentage=37.5),
                ActionDistributionItem(action_type="SEND_PAYMENT_LINK", count=12, percentage=25.0),
                ActionDistributionItem(action_type="CHANGE_PAYMENT_METHOD", count=8, percentage=16.7),
                ActionDistributionItem(action_type="RETRY_PAYMENT", count=6, percentage=12.5),
                ActionDistributionItem(action_type="ESCALATE_TO_HUMAN", count=4, percentage=8.3),
            ]
        else:
            kpi_metrics = KpiMetrics(
                revenue_at_risk=revenue_at_risk_val,
                potentially_recoverable=potentially_recoverable_val,
                recovered_revenue=recovered_val,
                recovery_rate=round(recovery_rate, 1),
                total_cases=total_cases,
                active_cases=active_cases_count,
            )
            recovery_trends = [
                RecoveryTrendPoint(date="Current Period", at_risk=float(revenue_at_risk_val), recovered=float(recovered_val))
            ]

        return DashboardSummaryResponse(
            kpis=kpi_metrics,
            recovery_trends=recovery_trends,
            action_distribution=action_distribution,
            recent_cases=recent_cases,
        )

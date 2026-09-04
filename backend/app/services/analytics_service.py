from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    Payment,
    PaymentStatus,
    RecoveryCase,
    RecoveryCaseStatus,
    RecoveryAction,
    RecoveryActionType,
)
from app.schemas.analytics import RevenueRiskAnalyticsResponse


class AnalyticsService:
    @staticmethod
    def get_revenue_risk_metrics(db: Session) -> RevenueRiskAnalyticsResponse:
        """
        Computes accurate platform-wide revenue risk, recoverability potential,
        and transaction breakdown metrics directly from PostgreSQL.
        """
        # 1. Revenue at Risk: sum of all active FAILED, ABANDONED, EXPIRED payments
        at_risk_statuses = [PaymentStatus.FAILED, PaymentStatus.ABANDONED, PaymentStatus.EXPIRED]
        total_risk = (
            db.query(func.sum(Payment.amount))
            .filter(Payment.status.in_(at_risk_statuses))
            .scalar()
            or Decimal("0.00")
        )

        # 2. Recovered Revenue: total amount settled from recovered cases/payments
        recovered_revenue = (
            db.query(func.sum(RecoveryCase.recovered_amount))
            .scalar()
            or Decimal("0.00")
        )

        # 3. Potentially Recoverable: sum of (revenue_at_risk * (recoverability_score / 100)) for active cases
        open_cases = (
            db.query(RecoveryCase)
            .filter(RecoveryCase.status.in_([RecoveryCaseStatus.OPEN, RecoveryCaseStatus.IN_PROGRESS]))
            .all()
        )
        potentially_recoverable = sum(
            (case.revenue_at_risk * (Decimal(str(case.recoverability_score or 0.0)) / Decimal("100.0")))
            for case in open_cases
        ) if open_cases else Decimal("0.00")

        # 4. Recovery Rate
        total_pool = total_risk + recovered_revenue
        if total_pool > Decimal("0.00"):
            recovery_rate = float((recovered_revenue / total_pool) * Decimal("100.0"))
        else:
            recovery_rate = 0.0

        # 5. Counts
        failed_count = db.query(func.count(Payment.id)).filter(Payment.status == PaymentStatus.FAILED).scalar() or 0
        abandoned_count = db.query(func.count(Payment.id)).filter(Payment.status == PaymentStatus.ABANDONED).scalar() or 0
        expired_count = db.query(func.count(Payment.id)).filter(Payment.status == PaymentStatus.EXPIRED).scalar() or 0

        open_case_count = (
            db.query(func.count(RecoveryCase.id))
            .filter(RecoveryCase.status.in_([RecoveryCaseStatus.OPEN, RecoveryCaseStatus.IN_PROGRESS]))
            .scalar()
            or 0
        )
        recovered_case_count = (
            db.query(func.count(RecoveryCase.id))
            .filter(RecoveryCase.status == RecoveryCaseStatus.RECOVERED)
            .scalar()
            or 0
        )

        escalated_case_count = (
            db.query(func.count(RecoveryCase.id))
            .filter(RecoveryCase.recommended_action == RecoveryActionType.ESCALATE_TO_HUMAN.value)
            .scalar()
            or 0
        )

        stopped_case_count = (
            db.query(func.count(RecoveryCase.id))
            .filter(RecoveryCase.recommended_action == RecoveryActionType.STOP_RECOVERY.value)
            .scalar()
            or 0
        )

        return RevenueRiskAnalyticsResponse(
            revenue_at_risk=total_risk,
            potentially_recoverable=Decimal(str(round(float(potentially_recoverable), 2))),
            recovered_revenue=recovered_revenue,
            recovery_rate=round(recovery_rate, 2),
            failed_payments=failed_count,
            abandoned_payments=abandoned_count,
            expired_payments=expired_count,
            open_recovery_cases=open_case_count,
            recovered_cases=recovered_case_count,
            escalated_cases=escalated_case_count,
            stopped_cases=stopped_case_count,
        )

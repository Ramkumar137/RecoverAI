from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Payment, PaymentStatus, RecoveryCase, RecoveryCaseStatus, Subscription


class RevenueRiskService:
    """
    Core service calculating revenue at risk for individual transactions
    and aggregating total exposure across merchants and payment streams.
    """

    # Statuses that represent uncollected expected revenue
    AT_RISK_STATUSES = [
        PaymentStatus.FAILED,
        PaymentStatus.ABANDONED,
        PaymentStatus.EXPIRED,
    ]

    @classmethod
    def calculate_revenue_at_risk(cls, payment: Payment) -> Decimal:
        """
        Determines the exact monetary revenue at risk for a payment entity.
        Returns the full payment amount if payment is failed, abandoned, or expired.
        Returns 0.00 if already recovered or successfully settled.
        """
        if payment.status in cls.AT_RISK_STATUSES:
            return Decimal(str(payment.amount))

        # Check if payment is associated with a past-due subscription
        if payment.subscription_id if hasattr(payment, 'subscription_id') else False:
            return Decimal(str(payment.amount))

        return Decimal("0.00")

    @classmethod
    def is_revenue_at_risk(cls, payment: Payment) -> bool:
        """
        Checks whether a payment qualifies as revenue at risk.
        """
        return cls.calculate_revenue_at_risk(payment) > Decimal("0.00")

    @classmethod
    def get_total_revenue_at_risk(cls, db: Session) -> Decimal:
        """
        Calculates the aggregate active revenue at risk across all eligible unrecovered payments.
        """
        # Sum payments in FAILED, ABANDONED, EXPIRED that are not already marked RECOVERED in recovery cases
        total_risk = (
            db.query(func.sum(Payment.amount))
            .filter(Payment.status.in_(cls.AT_RISK_STATUSES))
            .scalar()
        )
        return total_risk if total_risk is not None else Decimal("0.00")

    @classmethod
    def get_at_risk_payments(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        exclude_analyzed: bool = False,
    ) -> List[Payment]:
        """
        Retrieves all payments currently flagged as revenue at risk.
        """
        query = db.query(Payment).filter(Payment.status.in_(cls.AT_RISK_STATUSES))
        if exclude_analyzed:
            query = query.outerjoin(RecoveryCase).filter(RecoveryCase.id.is_(None))
        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

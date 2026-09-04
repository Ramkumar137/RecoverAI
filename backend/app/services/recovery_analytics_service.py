from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Payment,
    Customer,
    Merchant,
    RecoveryCase,
    RecoveryAction,
    AuditLog,
    PaymentStatus,
    RecoveryCaseStatus,
    ActionExecutionStatus,
)


class RecoveryAnalyticsService:
    """
    Dedicated analytics service for computing platform-wide recovery KPIs,
    trend curves, action effectiveness distributions, failure taxonomies,
    and chronological case investigation timelines.
    """

    @classmethod
    def get_overview(cls, db: Session) -> Dict[str, Any]:
        """
        Calculates headline revenue recovery KPIs.
        Guarantees zero-division safety and idempotent accounting.
        """
        cases = db.query(RecoveryCase).all()

        total_risk = Decimal("0.00")
        total_potential = Decimal("0.00")
        total_recovered = Decimal("0.00")

        active_count = 0
        recovered_count = 0
        escalated_count = 0
        stopped_count = 0

        for c in cases:
            total_risk += Decimal(str(c.revenue_at_risk or 0.0))
            potential_portion = Decimal(str(c.revenue_at_risk or 0.0)) * (Decimal(str(c.recoverability_score or 0.0)) / Decimal("100.0"))
            total_potential += potential_portion
            total_recovered += Decimal(str(c.recovered_amount or 0.0))

            st = c.status
            if st == RecoveryCaseStatus.RECOVERED:
                recovered_count += 1
            elif st == RecoveryCaseStatus.ESCALATED:
                escalated_count += 1
            elif st == RecoveryCaseStatus.STOPPED:
                stopped_count += 1
            else:
                active_count += 1

        recovery_rate = (
            round(float((total_recovered / total_potential) * Decimal("100.0")), 1)
            if total_potential > Decimal("0.00")
            else 0.0
        )

        return {
            "revenue_at_risk": round(float(total_risk), 2),
            "potentially_recoverable": round(float(total_potential), 2),
            "recovered_revenue": round(float(total_recovered), 2),
            "recovery_rate": recovery_rate,
            "active_cases": active_count,
            "recovered_cases": recovered_count,
            "escalated_cases": escalated_count,
            "stopped_cases": stopped_count,
        }

    @classmethod
    def get_recovery_trend(cls, db: Session, days: int = 14) -> List[Dict[str, Any]]:
        """
        Aggregates daily revenue at risk vs. recovered revenue over the specified lookback window.
        """
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        cases = (
            db.query(RecoveryCase)
            .filter(RecoveryCase.created_at >= start_date)
            .order_by(RecoveryCase.created_at.asc())
            .all()
        )

        daily_data = defaultdict(lambda: {"revenue_at_risk": Decimal("0.00"), "recovered": Decimal("0.00")})

        # Pre-populate dates for continuity
        for i in range(days + 1):
            d = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_data[d] = {"revenue_at_risk": Decimal("0.00"), "recovered": Decimal("0.00")}

        for c in cases:
            date_key = c.created_at.strftime("%Y-%m-%d") if c.created_at else now.strftime("%Y-%m-%d")
            daily_data[date_key]["revenue_at_risk"] += Decimal(str(c.revenue_at_risk or 0.0))
            daily_data[date_key]["recovered"] += Decimal(str(c.recovered_amount or 0.0))

        return [
            {
                "date": date_str,
                "revenue_at_risk": round(float(vals["revenue_at_risk"]), 2),
                "recovered": round(float(vals["recovered"]), 2),
            }
            for date_str, vals in sorted(daily_data.items())
        ]

    @classmethod
    def get_action_breakdown(cls, db: Session) -> List[Dict[str, Any]]:
        """
        Calculates volume, success count, and recovered revenue by recovery action type.
        """
        actions = db.query(RecoveryAction).all()
        breakdown = defaultdict(lambda: {"attempts": 0, "successful": 0, "recovered_amount": Decimal("0.00")})

        for a in actions:
            action_name = a.action_type.value if hasattr(a.action_type, "value") else str(a.action_type)
            breakdown[action_name]["attempts"] += 1
            if a.status == ActionExecutionStatus.EXECUTED and (a.recovered_amount or 0) > 0:
                breakdown[action_name]["successful"] += 1
                breakdown[action_name]["recovered_amount"] += Decimal(str(a.recovered_amount))

        return [
            {
                "action": action_name,
                "attempts": data["attempts"],
                "successful": data["successful"],
                "recovered_amount": round(float(data["recovered_amount"]), 2),
            }
            for action_name, data in sorted(breakdown.items(), key=lambda x: x[1]["attempts"], reverse=True)
        ]

    @classmethod
    def get_failure_breakdown(cls, db: Session) -> List[Dict[str, Any]]:
        """
        Calculates incidence, revenue at risk, and recovery effectiveness grouped by failure cause.
        """
        payments = db.query(Payment).all()
        breakdown = defaultdict(lambda: {"count": 0, "amount_at_risk": Decimal("0.00"), "recovered_amount": Decimal("0.00")})

        for p in payments:
            reason = "CHECKOUT_ABANDONED" if p.status == PaymentStatus.ABANDONED else (
                p.failure_reason.value if p.failure_reason else ("EXPIRED" if p.status == PaymentStatus.EXPIRED else "UNSPECIFIED_FAILURE")
            )
            if reason == "NONE":
                reason = "UNSPECIFIED_FAILURE"

            if p.status != PaymentStatus.SUCCESS:
                breakdown[reason]["count"] += 1
                breakdown[reason]["amount_at_risk"] += Decimal(str(p.amount))
                if p.status == PaymentStatus.RECOVERED:
                    breakdown[reason]["recovered_amount"] += Decimal(str(p.amount))

        results = []
        for reason, data in breakdown.items():
            if reason in ["NONE", "SUCCESS"] or data["count"] == 0:
                continue
            risk_flt = float(data["amount_at_risk"])
            rec_flt = float(data["recovered_amount"])
            rec_rate = round((rec_flt / risk_flt) * 100.0, 1) if risk_flt > 0 else 0.0
            results.append(
                {
                    "failure_reason": reason,
                    "count": data["count"],
                    "amount_at_risk": round(risk_flt, 2),
                    "recovered_amount": round(rec_flt, 2),
                    "recovery_rate": rec_rate,
                }
            )

        return sorted(results, key=lambda x: x["amount_at_risk"], reverse=True)

    @classmethod
    def get_case_timeline(cls, case_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Assembles the complete chronological investigation & execution audit trail for a case.
        """
        case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return []

        payment = case.payment

        audit_logs = (
            db.query(AuditLog)
            .filter(AuditLog.recovery_case_id == case.id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )

        timeline = []

        # Synthetic Genesis Event if not in audit logs
        has_genesis = any(log.event_type in ["PAYMENT_FAILED", "RECOVERY_CASE_CREATED"] for log in audit_logs)
        if not has_genesis and payment:
            timeline.append(
                {
                    "event": "PAYMENT_FAILED",
                    "timestamp": payment.created_at.isoformat() if payment.created_at else case.created_at.isoformat(),
                    "actor": "GATEWAY",
                    "description": (
                        f"Payment {payment.payment_id} of ₹{float(payment.amount):,.2f} failed due to "
                        f"{payment.failure_reason.value if payment.failure_reason else payment.status.value}."
                    ),
                    "metadata": {"amount": float(payment.amount), "method": payment.payment_method},
                }
            )

        for log in audit_logs:
            timeline.append(
                {
                    "event": log.event_type,
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                    "actor": log.actor,
                    "description": log.description,
                    "metadata": log.metadata_ or {},
                }
            )

        return timeline

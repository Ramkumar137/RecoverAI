from typing import Any, Dict, List, Optional, Union
from collections import Counter
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.recovery_case import RecoveryCase
from app.models.recovery_action import RecoveryAction
from app.models.enums import PaymentStatus


def get_customer_profile(customer_id: Union[int, str], db: Session) -> Dict[str, Any]:
    """
    Fetch customer telemetry profile and historical metrics.
    Safe read-only operation.
    """
    query = db.query(Customer)
    if isinstance(customer_id, int) or (isinstance(customer_id, str) and customer_id.isdigit()):
        customer = query.filter(Customer.id == int(customer_id)).first()
    else:
        customer = query.filter(Customer.customer_id == str(customer_id)).first()

    if not customer:
        return {}

    total = customer.total_payments or 0
    successful = customer.successful_payments or 0
    failed = customer.failed_payments or 0
    success_rate = round(successful / total, 4) if total > 0 else 0.0

    return {
        "id": customer.id,
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "account_age_days": customer.account_age_days,
        "total_payments": total,
        "successful_payments": successful,
        "failed_payments": failed,
        "average_payment_amount": float(customer.average_payment_amount or 0.0),
        "success_rate": success_rate,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
    }


def get_payment_details(payment_id: Union[int, str], db: Session) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive payment details including associated customer and merchant data.
    Safe read-only operation.
    """
    query = db.query(Payment)
    if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
        payment = query.filter(Payment.id == int(payment_id)).first()
    else:
        payment = query.filter(Payment.payment_id == str(payment_id)).first()

    if not payment:
        return None

    return {
        "id": payment.id,
        "payment_id": payment.payment_id,
        "customer_id": payment.customer_id,
        "customer_name": payment.customer.name if payment.customer else None,
        "customer_email": payment.customer.email if payment.customer else None,
        "merchant_id": payment.merchant_id,
        "merchant_name": payment.merchant.name if payment.merchant else None,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "payment_method": payment.payment_method,
        "status": payment.status.value if payment.status else None,
        "failure_reason": payment.failure_reason.value if payment.failure_reason else None,
        "retry_count": payment.retry_count,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
    }


def get_payment_history(customer_id: int, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch recent chronological payment records for a customer.
    Safe read-only operation.
    """
    payments = (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "payment_id": p.payment_id,
            "amount": float(p.amount),
            "currency": p.currency,
            "payment_method": p.payment_method,
            "status": p.status.value if p.status else None,
            "failure_reason": p.failure_reason.value if p.failure_reason else None,
            "retry_count": p.retry_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]


def get_failure_history(customer_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Fetch failed and abandoned transactions for a customer to analyze recurrence.
    Safe read-only operation.
    """
    failures = (
        db.query(Payment)
        .filter(
            Payment.customer_id == customer_id,
            Payment.status.in_([PaymentStatus.FAILED, PaymentStatus.ABANDONED, PaymentStatus.EXPIRED]),
        )
        .order_by(Payment.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "payment_id": p.payment_id,
            "amount": float(p.amount),
            "payment_method": p.payment_method,
            "status": p.status.value if p.status else None,
            "failure_reason": p.failure_reason.value if p.failure_reason else None,
            "retry_count": p.retry_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in failures
    ]


def get_recovery_history(customer_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Fetch past recovery cases and action outcomes for a customer.
    Safe read-only operation.
    """
    cases = (
        db.query(RecoveryCase)
        .join(Payment, RecoveryCase.payment_id == Payment.id)
        .filter(Payment.customer_id == customer_id)
        .order_by(RecoveryCase.created_at.desc())
        .all()
    )

    history = []
    for c in cases:
        actions = (
            db.query(RecoveryAction)
            .filter(RecoveryAction.recovery_case_id == c.id)
            .order_by(RecoveryAction.executed_at.desc())
            .all()
        )
        for a in actions:
            history.append(
                {
                    "case_id": c.id,
                    "payment_id": c.payment.payment_id if c.payment else None,
                    "action_type": a.action_type.value if a.action_type else None,
                    "status": a.status.value if a.status else None,
                    "recovered_amount": float(a.recovered_amount or 0.0),
                    "result": a.result,
                    "executed_at": a.executed_at.isoformat() if a.executed_at else None,
                    "case_status": c.status.value if c.status else None,
                }
            )
    return history


def get_subscription_status(customer_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Fetch subscriptions tied to the customer to assess recurring revenue impacts.
    Safe read-only operation.
    """
    subs = (
        db.query(Subscription)
        .filter(Subscription.customer_id == customer_id)
        .order_by(Subscription.created_at.desc())
        .all()
    )

    return [
        {
            "id": s.id,
            "subscription_id": s.subscription_id,
            "amount": float(s.amount),
            "billing_cycle": s.billing_cycle,
            "status": s.status,
            "retry_count": s.retry_count,
            "next_payment_date": s.next_payment_date.isoformat() if s.next_payment_date else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in subs
    ]


def get_customer_payment_patterns(customer_id: int, db: Session) -> Dict[str, Any]:
    """
    Analyze customer behavioral telemetry, payment method preferences, and failure distributions.
    Safe read-only operation.
    """
    payments = (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .all()
    )

    if not payments:
        return {
            "total_recorded": 0,
            "preferred_method": None,
            "method_distribution": {},
            "failure_rate_by_method": {},
            "abandonment_rate": 0.0,
        }

    methods = [p.payment_method for p in payments if p.payment_method]
    method_counts = Counter(methods)

    successful_methods = [
        p.payment_method
        for p in payments
        if p.status in [PaymentStatus.SUCCESS, PaymentStatus.RECOVERED] and p.payment_method
    ]
    preferred_method = Counter(successful_methods).most_common(1)[0][0] if successful_methods else None

    # Failure rate by method
    method_failures: Dict[str, int] = {}
    method_totals: Dict[str, int] = {}
    abandonment_count = 0

    for p in payments:
        m = p.payment_method or "UNKNOWN"
        method_totals[m] = method_totals.get(m, 0) + 1
        if p.status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED]:
            method_failures[m] = method_failures.get(m, 0) + 1
        elif p.status == PaymentStatus.ABANDONED:
            abandonment_count += 1
            method_failures[m] = method_failures.get(m, 0) + 1

    failure_rate_by_method = {
        m: round(method_failures.get(m, 0) / count, 4)
        for m, count in method_totals.items()
    }

    abandonment_rate = round(abandonment_count / len(payments), 4) if payments else 0.0

    return {
        "total_recorded": len(payments),
        "preferred_method": preferred_method,
        "method_distribution": dict(method_counts),
        "failure_rate_by_method": failure_rate_by_method,
        "abandonment_rate": abandonment_rate,
    }

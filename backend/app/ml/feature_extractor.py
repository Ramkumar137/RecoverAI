from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np


class FeatureExtractor:
    """
    Reusable feature engineering module for payment recoverability prediction.
    Transforms payment, customer, and subscription signals into clean numerical vectors.
    """

    FAILURE_REASON_MAP: Dict[str, int] = {
        "NONE": 0,
        "BANK_TIMEOUT": 1,
        "NETWORK_ERROR": 2,
        "INSUFFICIENT_FUNDS": 3,
        "AUTHENTICATION_FAILED": 4,
        "CARD_DECLINED": 5,
        "LIMIT_EXCEEDED": 6,
        "UNKNOWN": 7,
    }

    PAYMENT_METHOD_MAP: Dict[str, int] = {
        "UPI": 0,
        "CARD": 1,
        "NETBANKING": 2,
        "WALLET": 3,
        "EMI": 4,
        "OTHER": 5,
    }

    FEATURE_NAMES: List[str] = [
        "payment_amount",
        "customer_average_payment",
        "customer_successful_payment_rate",
        "customer_failed_payment_rate",
        "number_of_previous_successful_payments",
        "number_of_previous_failed_payments",
        "retry_count",
        "failure_reason_encoded",
        "payment_method_encoded",
        "customer_account_age",
        "time_since_failure_hours",
        "subscription_status",
        "historical_recovery_rate",
    ]

    @classmethod
    def extract_features(
        cls,
        amount: float,
        customer_avg_amount: float = 0.0,
        customer_successful_payments: int = 0,
        customer_failed_payments: int = 0,
        customer_account_age_days: int = 0,
        retry_count: int = 0,
        failure_reason: Optional[str] = None,
        payment_method: str = "UPI",
        created_at: Optional[datetime] = None,
        is_subscription: bool = False,
        merchant_recovery_rate: float = 0.5,
    ) -> Dict[str, float]:
        """
        Computes the feature dictionary from raw business signals without direct DB coupling.
        """
        total_prev = customer_successful_payments + customer_failed_payments
        success_rate = (
            float(customer_successful_payments / total_prev)
            if total_prev > 0
            else 0.8  # Default prior for new users
        )
        failure_rate = (
            float(customer_failed_payments / total_prev)
            if total_prev > 0
            else 0.2
        )

        reason_str = str(failure_reason or "UNKNOWN").upper()
        reason_enc = float(cls.FAILURE_REASON_MAP.get(reason_str, cls.FAILURE_REASON_MAP["UNKNOWN"]))

        method_str = str(payment_method or "UPI").upper()
        method_enc = float(cls.PAYMENT_METHOD_MAP.get(method_str, cls.PAYMENT_METHOD_MAP["OTHER"]))

        # Time since failure in hours
        now = datetime.now(timezone.utc)
        if created_at:
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            delta_hours = max(0.0, (now - created_at).total_seconds() / 3600.0)
        else:
            delta_hours = 0.0

        sub_status = 1.0 if is_subscription else 0.0

        return {
            "payment_amount": float(amount),
            "customer_average_payment": float(customer_avg_amount if customer_avg_amount > 0 else amount),
            "customer_successful_payment_rate": round(success_rate, 4),
            "customer_failed_payment_rate": round(failure_rate, 4),
            "number_of_previous_successful_payments": float(customer_successful_payments),
            "number_of_previous_failed_payments": float(customer_failed_payments),
            "retry_count": float(retry_count),
            "failure_reason_encoded": reason_enc,
            "payment_method_encoded": method_enc,
            "customer_account_age": float(customer_account_age_days),
            "time_since_failure_hours": round(delta_hours, 2),
            "subscription_status": sub_status,
            "historical_recovery_rate": round(float(merchant_recovery_rate), 4),
        }

    @classmethod
    def to_vector(cls, feature_dict: Dict[str, float]) -> np.ndarray:
        """
        Converts feature dictionary to a 1D NumPy array ordered by FEATURE_NAMES.
        """
        return np.array([feature_dict[name] for name in cls.FEATURE_NAMES], dtype=np.float32)

    @classmethod
    def extract_from_payment_entity(cls, payment: Any) -> Dict[str, float]:
        """
        Convenience adapter to extract features from a SQLAlchemy Payment object with loaded relations.
        """
        customer = getattr(payment, "customer", None)
        has_sub = getattr(payment, "subscription", None) is not None

        c_avg = float(customer.average_payment_amount) if customer and hasattr(customer, "average_payment_amount") else float(payment.amount)
        c_succ = int(customer.successful_payments) if customer and hasattr(customer, "successful_payments") else 0
        c_fail = int(customer.failed_payments) if customer and hasattr(customer, "failed_payments") else 0
        c_age = int(customer.account_age_days) if customer and hasattr(customer, "account_age_days") else 30

        f_reason = payment.failure_reason.value if hasattr(payment.failure_reason, "value") else str(payment.failure_reason)

        return cls.extract_features(
            amount=float(payment.amount),
            customer_avg_amount=c_avg,
            customer_successful_payments=c_succ,
            customer_failed_payments=c_fail,
            customer_account_age_days=c_age,
            retry_count=int(payment.retry_count or 0),
            failure_reason=f_reason,
            payment_method=str(payment.payment_method or "UPI"),
            created_at=payment.created_at,
            is_subscription=has_sub,
            merchant_recovery_rate=0.55,
        )

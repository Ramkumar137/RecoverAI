from dataclasses import dataclass
from typing import Optional
from app.models.enums import FailureReason, PaymentStatus


@dataclass
class FailureDiagnosis:
    diagnosis: str
    explanation: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    retry_appropriate: bool


class DiagnosisEngine:
    """
    Deterministic diagnosis engine that maps failure signals and payment statuses
    to structured root-cause explanations and severity classifications.
    """

    # Static signal diagnosis lookup
    DIAGNOSIS_MAP = {
        FailureReason.INSUFFICIENT_FUNDS: FailureDiagnosis(
            diagnosis="INSUFFICIENT_FUNDS",
            explanation="The customer's account or card does not have sufficient balance to complete the transaction.",
            severity="MEDIUM",
            retry_appropriate=True,
        ),
        FailureReason.BANK_TIMEOUT: FailureDiagnosis(
            diagnosis="TEMPORARY_BANK_FAILURE",
            explanation="The issuing or acquiring bank failed to respond within the gateway timeout window. Transient issue.",
            severity="LOW",
            retry_appropriate=True,
        ),
        FailureReason.NETWORK_ERROR: FailureDiagnosis(
            diagnosis="TEMPORARY_PAYMENT_FAILURE",
            explanation="A network disruption occurred during communication between merchant, gateway, and bank.",
            severity="LOW",
            retry_appropriate=True,
        ),
        FailureReason.CARD_DECLINED: FailureDiagnosis(
            diagnosis="PAYMENT_METHOD_DECLINED",
            explanation="The customer's card was explicitly declined by the issuer (card inactive, blocked, or expired).",
            severity="HIGH",
            retry_appropriate=False,
        ),
        FailureReason.AUTHENTICATION_FAILED: FailureDiagnosis(
            diagnosis="CUSTOMER_AUTHENTICATION_REQUIRED",
            explanation="Two-factor authentication (OTP / 3D Secure) failed or was incorrectly entered by the customer.",
            severity="MEDIUM",
            retry_appropriate=True,
        ),
        FailureReason.LIMIT_EXCEEDED: FailureDiagnosis(
            diagnosis="PAYMENT_LIMIT_EXCEEDED",
            explanation="Transaction amount exceeds the daily, monthly, or per-transaction limit set by customer or bank.",
            severity="HIGH",
            retry_appropriate=False,
        ),
        FailureReason.UNKNOWN: FailureDiagnosis(
            diagnosis="UNSPECIFIED_FAILURE",
            explanation="The gateway reported an unspecified or unmapped technical error.",
            severity="MEDIUM",
            retry_appropriate=True,
        ),
    }

    @classmethod
    def diagnose(
        cls,
        failure_reason: Optional[FailureReason] = None,
        status: Optional[PaymentStatus] = None,
    ) -> FailureDiagnosis:
        """
        Evaluates failure reason and payment status to produce a deterministic diagnosis.
        """
        # Handle abandonment and expiration by status first
        if status == PaymentStatus.ABANDONED:
            return FailureDiagnosis(
                diagnosis="CHECKOUT_ABANDONMENT",
                explanation="The customer initiated checkout but abandoned the session before authorization.",
                severity="MEDIUM",
                retry_appropriate=True,
            )

        if status == PaymentStatus.EXPIRED:
            return FailureDiagnosis(
                diagnosis="PAYMENT_SESSION_EXPIRED",
                explanation="The payment session or payment link expired before completion by the user.",
                severity="MEDIUM",
                retry_appropriate=True,
            )

        # Fallback to failure reason lookup
        if failure_reason in cls.DIAGNOSIS_MAP:
            return cls.DIAGNOSIS_MAP[failure_reason]

        # Default fallback
        return FailureDiagnosis(
            diagnosis="UNSPECIFIED_FAILURE",
            explanation="Payment did not complete due to an undetermined transaction event.",
            severity="MEDIUM",
            retry_appropriate=True,
        )

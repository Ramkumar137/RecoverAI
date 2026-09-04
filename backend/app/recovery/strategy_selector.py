from dataclasses import dataclass
from typing import Optional
from app.models.enums import RecoveryActionType


@dataclass
class StrategyRecommendation:
    action_type: RecoveryActionType
    reason: str
    priority: str  # LOW, MEDIUM, HIGH


class StrategySelector:
    """
    Deterministic policy engine that selects the optimal recovery strategy
    based on failure diagnosis, recoverability score (0-100), retry count,
    transaction amount, and customer history.
    """

    MAX_RETRIES: int = 3
    HIGH_VALUE_THRESHOLD: float = 10000.0

    @classmethod
    def select_strategy(
        cls,
        diagnosis: str,
        recoverability_score: float,
        retry_count: int = 0,
        amount: float = 0.0,
        customer_success_rate: float = 1.0,
        customer_failed_payments: int = 0,
    ) -> StrategyRecommendation:
        """
        Determines the appropriate recovery action and justification.
        """
        # Rule 1: Exceeded maximum allowed retry threshold -> Hard STOP
        if retry_count >= cls.MAX_RETRIES:
            return StrategyRecommendation(
                action_type=RecoveryActionType.STOP_RECOVERY,
                reason=f"Exceeded maximum automated retry attempts ({retry_count}/{cls.MAX_RETRIES}). Recovery halted to prevent customer fatigue and issuer penalty.",
                priority="LOW",
            )

        # Rule 2: Checkout Abandonment / Session Expired
        if diagnosis in ["CHECKOUT_ABANDONMENT", "PAYMENT_SESSION_EXPIRED"]:
            if recoverability_score >= 50.0:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.SEND_REMINDER,
                    reason="Customer initiated checkout but abandoned session. Gentle prompt/reminder has high conversion probability.",
                    priority="HIGH" if amount >= cls.HIGH_VALUE_THRESHOLD else "MEDIUM",
                )
            else:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.SEND_PAYMENT_LINK,
                    reason="Abandoned checkout with moderate confidence. Direct multi-channel payment link simplifies completion.",
                    priority="MEDIUM",
                )

        # Rule 3: Transient Bank / Network Disruption
        if diagnosis in ["TEMPORARY_BANK_FAILURE", "TEMPORARY_PAYMENT_FAILURE"]:
            if recoverability_score >= 70.0 and retry_count < 2:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.RETRY_LATER,
                    reason="Transient bank switch or network error detected with high recoverability. Scheduling retry after cooling off period (15-30m).",
                    priority="HIGH",
                )
            elif retry_count == 0:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.RETRY_PAYMENT,
                    reason="Transient network drop on initial attempt. Immediate gateway secondary retry recommended.",
                    priority="HIGH",
                )
            elif recoverability_score < 30.0 or retry_count >= 2:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
                    reason="Repeated transient errors with declining score. Escalate to operations team for gateway telemetry review.",
                    priority="HIGH",
                )

        # Rule 4: Insufficient Funds
        if diagnosis == "INSUFFICIENT_FUNDS":
            if recoverability_score >= 40.0:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.SEND_PAYMENT_LINK,
                    reason="Insufficient funds detected on reliable customer. Instant payment link enables payment via alternative funding source or later liquidity window.",
                    priority="HIGH" if amount >= cls.HIGH_VALUE_THRESHOLD else "MEDIUM",
                )
            else:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.RETRY_LATER,
                    reason="Low balance reported. Holding automated retry until estimated customer billing/payroll replenishment cycle.",
                    priority="LOW",
                )

        # Rule 5: Authentication / Card Declined
        if diagnosis in ["CUSTOMER_AUTHENTICATION_REQUIRED", "PAYMENT_METHOD_DECLINED"]:
            if customer_failed_payments >= 3 or (amount >= cls.HIGH_VALUE_THRESHOLD and recoverability_score < 40.0):
                return StrategyRecommendation(
                    action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
                    reason="High-value or chronic card decline detected. Route to merchant VIP account management.",
                    priority="HIGH",
                )
            else:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.CHANGE_PAYMENT_METHOD,
                    reason="Payment instrument blocked or declined. Prompt customer to switch to alternative card, UPI Autopay, or Netbanking.",
                    priority="HIGH",
                )

        # Rule 6: Payment Limit Exceeded
        if diagnosis == "PAYMENT_LIMIT_EXCEEDED":
            if amount >= cls.HIGH_VALUE_THRESHOLD:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
                    reason="Transaction amount exceeds customer banking limit. Manual merchant intervention needed to split invoice or arrange wire transfer.",
                    priority="HIGH",
                )
            else:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.CHANGE_PAYMENT_METHOD,
                    reason="Daily/single limit exceeded on selected payment method. Prompt user to switch to Netbanking or NEFT.",
                    priority="MEDIUM",
                )

        # Rule 7: Low recoverability or repeated systemic failure
        if recoverability_score < 30.0:
            if amount >= cls.HIGH_VALUE_THRESHOLD:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
                    reason="Low algorithmic recoverability score for high-value transaction. Escalate to manual account specialist.",
                    priority="HIGH",
                )
            else:
                return StrategyRecommendation(
                    action_type=RecoveryActionType.STOP_RECOVERY,
                    reason="Low recoverability score below salvageable threshold. Stop recovery to minimize operational cost.",
                    priority="LOW",
                )

        # Default fallback
        return StrategyRecommendation(
            action_type=RecoveryActionType.SEND_PAYMENT_LINK,
            reason="Standard smart recovery payment link dispatch.",
            priority="MEDIUM",
        )

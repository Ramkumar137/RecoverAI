from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
from app.models.enums import PaymentStatus, RecoveryCaseStatus


class RecoveryConfig:
    """
    Centralized configuration for bounded payment recovery.
    Enforces business safety constraints and execution parameters.
    """

    MAX_RETRIES: int = 3
    RECOVERY_WINDOW_HOURS: int = 48
    MIN_RECOVERABILITY_SCORE: float = 20.0
    HIGH_VALUE_THRESHOLD: float = 10000.0
    CRITICAL_VALUE_THRESHOLD: float = 50000.0


class StoppingRules:
    """
    Centralized evaluation of explicit stopping conditions.
    Guarantees no payment is retried indefinitely or against business policy.
    """

    @classmethod
    def evaluate(
        cls,
        payment_status: PaymentStatus,
        case_status: RecoveryCaseStatus,
        retry_count: int,
        recoverability_score: float,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        policy_result: Optional[str] = None,
        final_action: Optional[str] = None,
        escalation_required: bool = False,
    ) -> Tuple[bool, str, Optional[RecoveryCaseStatus]]:
        """
        Returns (should_stop, reason, target_status).
        """
        # 1. Already Recovered
        if payment_status == PaymentStatus.RECOVERED or case_status == RecoveryCaseStatus.RECOVERED:
            return True, "Payment is already successfully recovered. No further action needed.", RecoveryCaseStatus.RECOVERED

        # 2. Case is in a terminal state
        if case_status == RecoveryCaseStatus.STOPPED:
            return True, "Recovery for this case has already been stopped.", RecoveryCaseStatus.STOPPED

        if case_status == RecoveryCaseStatus.ESCALATED or escalation_required or final_action == "ESCALATE_TO_HUMAN":
            return True, "Case is escalated to merchant operations/human oversight. Automated attempts halted.", RecoveryCaseStatus.ESCALATED

        # 3. Maximum retry count reached
        if retry_count >= RecoveryConfig.MAX_RETRIES:
            return True, f"Maximum retry attempts reached ({retry_count}/{RecoveryConfig.MAX_RETRIES}). Enforcing safety stop.", RecoveryCaseStatus.STOPPED

        # 4. Low recoverability score below minimum cutoff
        if recoverability_score < RecoveryConfig.MIN_RECOVERABILITY_SCORE:
            return True, f"Recoverability score ({recoverability_score:.1f}%) is below minimum salvageability threshold ({RecoveryConfig.MIN_RECOVERABILITY_SCORE}%).", RecoveryCaseStatus.STOPPED

        # 5. Recovery window expired (48 hours)
        now = datetime.now(timezone.utc)
        deadline = expires_at
        if not deadline and created_at:
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            deadline = created_at + timedelta(hours=RecoveryConfig.RECOVERY_WINDOW_HOURS)

        if deadline:
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if now > deadline:
                return True, f"Recovery window of {RecoveryConfig.RECOVERY_WINDOW_HOURS} hours expired on {deadline.isoformat()}.", RecoveryCaseStatus.STOPPED

        # 6. Policy engine explicitly denied or mandated stop
        if final_action == "STOP_RECOVERY":
            return True, "Policy engine mandated STOP_RECOVERY for this transaction.", RecoveryCaseStatus.STOPPED

        return False, "Case is eligible for recovery.", None

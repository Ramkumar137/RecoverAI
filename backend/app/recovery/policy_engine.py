from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.agents.schemas import AIInvestigationResponse
from app.agents.investigation_context import InvestigationContext
from app.models.enums import RecoveryActionType, FailureReason


@dataclass
class PolicyEvaluationResult:
    result: str  # "ALLOWED" or "DENIED"
    ai_recommended_action: str
    final_action: str
    policy_applied: str
    reason: str
    escalation_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result,
            "ai_recommended_action": self.ai_recommended_action,
            "final_action": self.final_action,
            "policy_applied": self.policy_applied,
            "reason": self.reason,
            "escalation_required": self.escalation_required,
        }


class PolicyEngine:
    """
    Deterministic governance & policy enforcement engine.
    The AI agent is strictly advisory; this engine validates proposed recommendations
    against immutable business safety rails and makes the definitive recovery decision.
    """

    MAX_RETRIES: int = 3
    HIGH_VALUE_THRESHOLD: float = 10000.0
    CRITICAL_VALUE_THRESHOLD: float = 50000.0
    LOW_RECOVERABILITY_CUTOFF: float = 30.0

    @classmethod
    def evaluate(
        cls,
        context: InvestigationContext,
        ai_response: AIInvestigationResponse,
    ) -> PolicyEvaluationResult:
        """
        Evaluates the AI agent's proposal against hard safety policies.
        Returns a PolicyEvaluationResult indicating ALLOWED / DENIED and the final binding action.
        """
        payment = context.payment
        amount = float(payment.get("amount", 0.0))
        retries = int(payment.get("retry_count", 0))
        failure_reason = str(payment.get("failure_reason") or "").upper()
        score = float(context.ml_prediction.get("score", 50.0))
        ai_action = ai_response.recommended_action.strip().upper()

        # Validate action is recognized
        valid_actions = {a.value for a in RecoveryActionType}
        if ai_action not in valid_actions:
            # Fallback to deterministic strategy
            default_action = context.deterministic_strategy.get("action_type", RecoveryActionType.SEND_PAYMENT_LINK.value)
            return PolicyEvaluationResult(
                result="DENIED",
                ai_recommended_action=ai_action,
                final_action=default_action,
                policy_applied="OVERRIDE_INVALID_ACTION",
                reason=f"AI suggested unrecognized action '{ai_action}'. Reverted to deterministic policy: {default_action}.",
                escalation_required=default_action == RecoveryActionType.ESCALATE_TO_HUMAN.value,
            )

        # 1. HARD SAFETY RULE: Max Retries Exceeded
        if retries >= cls.MAX_RETRIES:
            if ai_action == RecoveryActionType.STOP_RECOVERY.value:
                return PolicyEvaluationResult(
                    result="ALLOWED",
                    ai_recommended_action=ai_action,
                    final_action=RecoveryActionType.STOP_RECOVERY.value,
                    policy_applied="POLICY_MAX_RETRIES_COMPLIANT",
                    reason=f"Compliant with max retry policy ({retries}/{cls.MAX_RETRIES}). Recovery halted.",
                    escalation_required=False,
                )
            else:
                return PolicyEvaluationResult(
                    result="DENIED",
                    ai_recommended_action=ai_action,
                    final_action=RecoveryActionType.STOP_RECOVERY.value,
                    policy_applied="OVERRIDE_MAX_RETRIES_EXCEEDED",
                    reason=f"AI recommended '{ai_action}', but retry limit reached ({retries}/{cls.MAX_RETRIES}). Enforced STOP_RECOVERY to protect customer experience.",
                    escalation_required=False,
                )

        # 2. HARD SAFETY RULE: Cannot retry hard card decline or blocked instrument
        if failure_reason == FailureReason.CARD_DECLINED.value or ai_response.diagnosis == "PAYMENT_METHOD_DECLINED":
            if ai_action in [RecoveryActionType.RETRY_PAYMENT.value, RecoveryActionType.RETRY_LATER.value]:
                override_action = (
                    RecoveryActionType.ESCALATE_TO_HUMAN.value
                    if (amount >= cls.HIGH_VALUE_THRESHOLD or score < cls.LOW_RECOVERABILITY_CUTOFF)
                    else RecoveryActionType.CHANGE_PAYMENT_METHOD.value
                )
                return PolicyEvaluationResult(
                    result="DENIED",
                    ai_recommended_action=ai_action,
                    final_action=override_action,
                    policy_applied="OVERRIDE_CARD_DECLINE_NO_RETRY",
                    reason=f"Cannot retry a hard card decline without changing payment instruments. Overridden to '{override_action}'.",
                    escalation_required=override_action == RecoveryActionType.ESCALATE_TO_HUMAN.value,
                )

        # 3. HARD SAFETY RULE: Cannot retry Limit Exceeded
        if failure_reason == FailureReason.LIMIT_EXCEEDED.value or ai_response.diagnosis == "PAYMENT_LIMIT_EXCEEDED":
            if ai_action in [RecoveryActionType.RETRY_PAYMENT.value, RecoveryActionType.RETRY_LATER.value]:
                override_action = (
                    RecoveryActionType.ESCALATE_TO_HUMAN.value
                    if amount >= cls.HIGH_VALUE_THRESHOLD
                    else RecoveryActionType.CHANGE_PAYMENT_METHOD.value
                )
                return PolicyEvaluationResult(
                    result="DENIED",
                    ai_recommended_action=ai_action,
                    final_action=override_action,
                    policy_applied="OVERRIDE_LIMIT_EXCEEDED_NO_RETRY",
                    reason=f"Card or banking limit exceeded; automated retry will fail again. Overridden to '{override_action}'.",
                    escalation_required=override_action == RecoveryActionType.ESCALATE_TO_HUMAN.value,
                )

        # 4. SAFETY RULE: Low recoverability cannot perform expensive retries
        if score < cls.LOW_RECOVERABILITY_CUTOFF:
            if ai_action in [RecoveryActionType.RETRY_PAYMENT.value, RecoveryActionType.RETRY_LATER.value]:
                override_action = (
                    RecoveryActionType.ESCALATE_TO_HUMAN.value
                    if amount >= cls.HIGH_VALUE_THRESHOLD
                    else RecoveryActionType.STOP_RECOVERY.value
                )
                return PolicyEvaluationResult(
                    result="DENIED",
                    ai_recommended_action=ai_action,
                    final_action=override_action,
                    policy_applied="OVERRIDE_LOW_RECOVERABILITY",
                    reason=f"Recoverability score ({score:.1f}) is below cutoff ({cls.LOW_RECOVERABILITY_CUTOFF}). Retries prohibited. Overridden to '{override_action}'.",
                    escalation_required=override_action == RecoveryActionType.ESCALATE_TO_HUMAN.value,
                )

        # 5. SAFETY RULE: Critical Value Risk Protection
        if amount >= cls.CRITICAL_VALUE_THRESHOLD and score < 50.0:
            if ai_action != RecoveryActionType.ESCALATE_TO_HUMAN.value:
                return PolicyEvaluationResult(
                    result="DENIED",
                    ai_recommended_action=ai_action,
                    final_action=RecoveryActionType.ESCALATE_TO_HUMAN.value,
                    policy_applied="OVERRIDE_CRITICAL_VALUE_RISK",
                    reason=f"Critical transaction amount ₹{amount:,.2f} with sub-50% recoverability requires VIP human oversight.",
                    escalation_required=True,
                )

        # 6. EXPLICIT ESCALATION HANDLING
        is_escalation = ai_action == RecoveryActionType.ESCALATE_TO_HUMAN.value
        return PolicyEvaluationResult(
            result="ALLOWED",
            ai_recommended_action=ai_action,
            final_action=ai_action,
            policy_applied="AI_RECOMMENDATION_APPROVED",
            reason=ai_response.recommended_action_rationale or "AI recommendation passed all deterministic safety validation checks.",
            escalation_required=is_escalation,
        )

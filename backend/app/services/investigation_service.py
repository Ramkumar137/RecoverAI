import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.models import (
    Payment,
    RecoveryCase,
    RecoveryAction,
    AuditLog,
    RecoveryActionType,
    ActionExecutionStatus,
    RecoveryCaseStatus,
)
from app.services.recovery_case_service import RecoveryCaseService
from app.agents.investigation_context import InvestigationContextBuilder
from app.agents.gemini_agent import GeminiAgent
from app.recovery.policy_engine import PolicyEngine
from app.utils.logger import logger

_locks_guard = threading.Lock()
_payment_locks: Dict[str, threading.Lock] = {}


def _get_payment_lock(key: str) -> threading.Lock:
    with _locks_guard:
        if key not in _payment_locks:
            _payment_locks[key] = threading.Lock()
        return _payment_locks[key]


class InvestigationService:
    """
    Orchestration service for forensic payment failure investigations.
    Bridges the read-only investigation tools, Gemini 2.5 Flash agent,
    deterministic policy governance, and database persistence.
    """

    @classmethod
    def investigate_payment(
        cls,
        payment_id: Union[int, str],
        db: Session,
        force_refresh: bool = False,
    ) -> Optional[Dict[str, Any]]:
        # 1. Resolve payment entity
        payment = None
        if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
            payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()

        if not payment:
            payment = db.query(Payment).filter(Payment.payment_id == str(payment_id)).first()

        if not payment:
            logger.warning(f"Payment '{payment_id}' not found for investigation.")
            return None

        # 2. Ensure baseline recovery case exists
        case = RecoveryCaseService.create_or_update_recovery_case(payment.id, db)
        if not case:
            return None

        # Serialize concurrent investigations for the same payment to prevent duplicate AI API dispatch
        payment_key = str(payment.payment_id or payment.id)
        with _get_payment_lock(payment_key):
            db.refresh(case)
            # 3. If already investigated and not forcing refresh, return existing
            if case.ai_diagnosis and not force_refresh:
                return cls._format_investigation_response(case, ai_available=True)

            # 4. Assemble investigation context using read-only telemetry tools
            context = InvestigationContextBuilder.build(payment.id, db)
            if not context:
                logger.error(f"Failed to assemble investigation context for payment {payment.id}")
                return None

            # 5. Conduct AI forensic investigation via Gemini (with offline fallback)
            ai_response, ai_available = GeminiAgent.investigate(context)

            # 6. Evaluate recommendation through deterministic Policy Engine
            policy_result = PolicyEngine.evaluate(context, ai_response)

            # 7. Update RecoveryCase with findings
            case.ai_diagnosis = ai_response.diagnosis
            case.ai_confidence = ai_response.confidence
            case.ai_summary = ai_response.summary
            case.ai_evidence = [e.model_dump() for e in ai_response.evidence]
            case.ai_recommended_action = ai_response.recommended_action
            case.policy_result = policy_result.result
            case.final_action = policy_result.final_action
            case.escalation_required = policy_result.escalation_required
            case.diagnosis = ai_response.diagnosis
            case.recommended_action = policy_result.final_action
            case.updated_at = datetime.now(timezone.utc)

            if policy_result.final_action == RecoveryActionType.STOP_RECOVERY.value:
                case.status = RecoveryCaseStatus.CLOSED
            else:
                case.status = RecoveryCaseStatus.IN_PROGRESS

            # 8. Record Pending Recovery Action
            try:
                action_enum = RecoveryActionType(policy_result.final_action)
                action_record = RecoveryAction(
                    recovery_case_id=case.id,
                    action_type=action_enum,
                    reason=policy_result.reason,
                    status=ActionExecutionStatus.PENDING,
                )
                db.add(action_record)
            except Exception as e:
                logger.error(f"Failed to persist recovery action: {e}")

            # 9. Record Immutable Audit Log
            audit_entry = AuditLog(
                recovery_case_id=case.id,
                event_type="AI_INVESTIGATION_COMPLETED",
                description=(
                    f"AI investigation concluded: {ai_response.diagnosis}. "
                    f"Agent proposed: {ai_response.recommended_action}. "
                    f"Policy evaluated: {policy_result.result} -> Final Action: {policy_result.final_action}. "
                    f"Escalation required: {policy_result.escalation_required}."
                ),
                actor="GEMINI_2_5_FLASH" if ai_available else "POLICY_ENGINE_FALLBACK",
                metadata_={
                    "ai_available": ai_available,
                    "ai_diagnosis": ai_response.diagnosis,
                    "ai_confidence": ai_response.confidence,
                    "ai_recommended_action": ai_response.recommended_action,
                    "policy_result": policy_result.result,
                    "final_action": policy_result.final_action,
                    "policy_applied": policy_result.policy_applied,
                    "policy_reason": policy_result.reason,
                    "escalation_required": policy_result.escalation_required,
                    "recovery_channel": ai_response.recovery_channel,
                    "wait_time_minutes": ai_response.wait_time_minutes,
                    "recoverability_score": case.recoverability_score,
                },
            )
            db.add(audit_entry)
            db.commit()
            db.refresh(case)

            return cls._format_investigation_response(
                case=case,
                ai_available=ai_available,
                policy_reason=policy_result.reason,
                policy_applied=policy_result.policy_applied,
                recovery_channel=ai_response.recovery_channel,
                wait_time_minutes=ai_response.wait_time_minutes,
                ai_rationale=ai_response.recommended_action_rationale,
            )

    @classmethod
    def get_investigation(
        cls,
        payment_id: Union[int, str],
        db: Session,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves existing investigation report for a payment.
        """
        payment = None
        if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
            payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()

        if not payment:
            payment = db.query(Payment).filter(Payment.payment_id == str(payment_id)).first()

        if not payment:
            return None

        case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).first()
        if not case or not case.ai_diagnosis:
            return None

        # Look for the latest audit log to extract metadata
        latest_audit = (
            db.query(AuditLog)
            .filter(
                AuditLog.recovery_case_id == case.id,
                AuditLog.event_type == "AI_INVESTIGATION_COMPLETED",
            )
            .order_by(AuditLog.created_at.desc())
            .first()
        )

        metadata = latest_audit.metadata_ if latest_audit and latest_audit.metadata_ else {}

        return cls._format_investigation_response(
            case=case,
            ai_available=metadata.get("ai_available", True),
            policy_reason=metadata.get("policy_reason", ""),
            policy_applied=metadata.get("policy_applied", ""),
            recovery_channel=metadata.get("recovery_channel", "WHATSAPP"),
            wait_time_minutes=metadata.get("wait_time_minutes", 0),
            ai_rationale=case.diagnosis or "",
        )

    @classmethod
    def _format_investigation_response(
        cls,
        case: RecoveryCase,
        ai_available: bool = True,
        policy_reason: str = "",
        policy_applied: str = "",
        recovery_channel: Optional[str] = None,
        wait_time_minutes: int = 0,
        ai_rationale: str = "",
    ) -> Dict[str, Any]:
        return {
            "payment_id": case.payment.payment_id if case.payment else None,
            "payment_numeric_id": case.payment_id,
            "recovery_case_id": case.id,
            "ai_available": ai_available,
            "diagnosis": case.ai_diagnosis or case.diagnosis,
            "confidence": case.ai_confidence or 0.85,
            "summary": case.ai_summary or f"Case diagnosed as {case.diagnosis}.",
            "evidence": case.ai_evidence or [],
            "ai_recommended_action": case.ai_recommended_action or case.recommended_action,
            "ai_rationale": ai_rationale or case.diagnosis,
            "policy_result": case.policy_result or "ALLOWED",
            "final_action": case.final_action or case.recommended_action,
            "policy_applied": policy_applied or "AI_RECOMMENDATION_APPROVED",
            "policy_reason": policy_reason,
            "escalation_required": case.escalation_required,
            "recovery_channel": recovery_channel,
            "wait_time_minutes": wait_time_minutes,
            "recoverability_score": case.recoverability_score,
            "revenue_at_risk": float(case.revenue_at_risk),
            "status": case.status.value if hasattr(case.status, "value") else str(case.status),
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }

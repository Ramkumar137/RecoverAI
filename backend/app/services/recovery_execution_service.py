from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import (
    Payment,
    Customer,
    RecoveryCase,
    RecoveryAction,
    AuditLog,
    PaymentStatus,
    RecoveryCaseStatus,
    RecoveryActionType,
    ActionExecutionStatus,
)
from app.recovery.config import RecoveryConfig, StoppingRules
from app.recovery.state_machine import RecoveryCaseStateMachine
from app.recovery.simulator import PaymentSimulator
from app.services.investigation_service import InvestigationService
from app.services.recovery_case_service import RecoveryCaseService
from app.utils.logger import logger


class RecoveryExecutionService:
    """
    Core execution engine for simulated payment recovery workflows.
    Enforces deterministic policy validation, state machine transitions,
    stopping conditions, and zero-duplicate revenue accounting.
    """

    @classmethod
    def execute_recovery_action(
        cls,
        recovery_case_id: int,
        db: Session,
        bypass_window: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Executes policy-approved simulated recovery action for a single case.
        Idempotent: Re-executing an already recovered, stopped, or escalated case
        returns the existing state without duplicate financial crediting.
        """
        case = db.query(RecoveryCase).filter(RecoveryCase.id == recovery_case_id).first()
        if not case:
            logger.warning(f"RecoveryCase #{recovery_case_id} not found.")
            return None

        payment = case.payment
        if not payment:
            payment = db.query(Payment).filter(Payment.id == case.payment_id).first()

        amount_float = float(payment.amount)
        current_recovered = float(case.recovered_amount or 0.0)

        # 1. IDEMPOTENCY GUARD: Case already in terminal state
        if case.status in [RecoveryCaseStatus.RECOVERED, RecoveryCaseStatus.STOPPED, RecoveryCaseStatus.ESCALATED]:
            return {
                "case_id": case.id,
                "payment_id": payment.payment_id,
                "action": case.final_action or case.recommended_action or "UNKNOWN",
                "status": case.status.value,
                "previous_amount": amount_float,
                "recovered_amount": current_recovered,
                "retry_count": payment.retry_count,
                "idempotent": True,
                "message": f"Case #{case.id} is already in terminal state '{case.status.value}'. Action not re-executed.",
            }

        # 2. Ensure case has an approved policy action; if not, use recommended_action or investigate
        if not case.final_action:
            if case.recommended_action:
                case.final_action = case.recommended_action
                case.policy_result = "ALLOWED"
                db.commit()
            else:
                InvestigationService.investigate_payment(payment.id, db)
                db.refresh(case)

        final_action = case.final_action or case.recommended_action or RecoveryActionType.SEND_PAYMENT_LINK.value

        # 3. STOPPING RULES EVALUATION
        should_stop, stop_reason, target_status = StoppingRules.evaluate(
            payment_status=payment.status,
            case_status=case.status,
            retry_count=payment.retry_count,
            recoverability_score=case.recoverability_score,
            created_at=case.created_at,
            expires_at=case.expires_at,
            policy_result=case.policy_result,
            final_action=final_action,
            escalation_required=case.escalation_required,
        )

        if should_stop and target_status in [RecoveryCaseStatus.STOPPED, RecoveryCaseStatus.ESCALATED]:
            case.status = target_status
            case.updated_at = datetime.now(timezone.utc)
            action_type_enum = RecoveryActionType.STOP_RECOVERY if target_status == RecoveryCaseStatus.STOPPED else RecoveryActionType.ESCALATE_TO_HUMAN
            event_type = "RECOVERY_STOPPED" if target_status == RecoveryCaseStatus.STOPPED else "HUMAN_ESCALATION"

            action_record = RecoveryAction(
                recovery_case_id=case.id,
                action_type=action_type_enum,
                reason=stop_reason,
                status=ActionExecutionStatus.SKIPPED if target_status == RecoveryCaseStatus.STOPPED else ActionExecutionStatus.EXECUTED,
            )
            db.add(action_record)

            audit_entry = AuditLog(
                recovery_case_id=case.id,
                event_type=event_type,
                description=f"Recovery halted by policy rules: {stop_reason}",
                actor="POLICY_ENGINE",
                metadata_={
                    "payment_id": payment.payment_id,
                    "amount": amount_float,
                    "retry_count": payment.retry_count,
                    "stop_reason": stop_reason,
                    "target_status": target_status.value,
                },
            )
            db.add(audit_entry)
            db.commit()
            db.refresh(case)

            return {
                "case_id": case.id,
                "payment_id": payment.payment_id,
                "action": action_type_enum.value,
                "status": case.status.value,
                "previous_amount": amount_float,
                "recovered_amount": 0.0,
                "retry_count": payment.retry_count,
                "idempotent": False,
                "message": stop_reason,
            }

        # 4. POLICY ENGINE ENFORCEMENT: Never execute denied actions
        if case.policy_result == "DENIED" and final_action != case.final_action:
            final_action = case.final_action

        # 5. STATE MACHINE TRANSITIONS
        case.status = RecoveryCaseStatus.ACTION_APPROVED
        case.status = RecoveryCaseStatus.ACTION_EXECUTED
        case.recovery_attempts = (case.recovery_attempts or 0) + 1
        case.updated_at = datetime.now(timezone.utc)

        # Audit: Action Started
        db.add(
            AuditLog(
                recovery_case_id=case.id,
                event_type="RECOVERY_ACTION_STARTED",
                description=f"Initiating simulated recovery workflow: {final_action}",
                actor="RECOVERY_EXECUTION_ENGINE",
                metadata_={
                    "payment_id": payment.payment_id,
                    "action": final_action,
                    "retry_count": payment.retry_count,
                    "amount": amount_float,
                },
            )
        )

        # 6. ACTION EXECUTION BEHAVIOR
        is_success = False
        outcome_message = ""
        action_enum = RecoveryActionType(final_action) if final_action in [a.value for a in RecoveryActionType] else RecoveryActionType.SEND_PAYMENT_LINK

        if action_enum in [RecoveryActionType.RETRY_PAYMENT, RecoveryActionType.RETRY_LATER]:
            payment.retry_count = int(payment.retry_count or 0) + 1
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="PAYMENT_RETRY_ATTEMPTED",
                    description=f"Simulating payment retry attempt #{payment.retry_count} via gateway.",
                    actor="PAYMENT_SIMULATOR",
                    metadata_={"retry_count": payment.retry_count, "payment_id": payment.payment_id},
                )
            )
            is_success, outcome_message = PaymentSimulator.simulate_payment_attempt(
                payment=payment,
                action=action_enum.value,
                recoverability_score=case.recoverability_score,
                customer=payment.customer,
            )

        elif action_enum == RecoveryActionType.SEND_PAYMENT_LINK:
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="PAYMENT_LINK_SENT",
                    description=f"Simulated payment link dispatch to customer {payment.customer.email if payment.customer else 'customer'}.",
                    actor="PAYMENT_SIMULATOR",
                    metadata_={"action": "SEND_PAYMENT_LINK", "payment_id": payment.payment_id},
                )
            )
            is_success, outcome_message = PaymentSimulator.simulate_payment_attempt(
                payment=payment,
                action=action_enum.value,
                recoverability_score=case.recoverability_score,
                customer=payment.customer,
            )

        elif action_enum == RecoveryActionType.SEND_REMINDER:
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="REMINDER_SENT",
                    description="Simulated checkout reminder notification delivery.",
                    actor="PAYMENT_SIMULATOR",
                    metadata_={"action": "SEND_REMINDER", "payment_id": payment.payment_id},
                )
            )
            is_success, outcome_message = PaymentSimulator.simulate_payment_attempt(
                payment=payment,
                action=action_enum.value,
                recoverability_score=case.recoverability_score,
                customer=payment.customer,
            )

        elif action_enum == RecoveryActionType.CHANGE_PAYMENT_METHOD:
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="METHOD_CHANGE_SIMULATED",
                    description="Simulated customer selecting alternative payment instrument (UPI Autopay / Netbanking).",
                    actor="PAYMENT_SIMULATOR",
                    metadata_={"action": "CHANGE_PAYMENT_METHOD", "payment_id": payment.payment_id},
                )
            )
            is_success, outcome_message = PaymentSimulator.simulate_payment_attempt(
                payment=payment,
                action=action_enum.value,
                recoverability_score=case.recoverability_score,
                customer=payment.customer,
            )

        elif action_enum == RecoveryActionType.ESCALATE_TO_HUMAN:
            case.status = RecoveryCaseStatus.ESCALATED
            case.escalation_required = True
            db.add(
                RecoveryAction(
                    recovery_case_id=case.id,
                    action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
                    reason="Escalated to human operations team for manual high-touch handling.",
                    status=ActionExecutionStatus.EXECUTED,
                    executed_at=datetime.now(timezone.utc),
                )
            )
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="HUMAN_ESCALATION",
                    description="Case routed to merchant VIP support and account management.",
                    actor="POLICY_ENGINE",
                    metadata_={"action": "ESCALATE_TO_HUMAN", "amount": amount_float},
                )
            )
            db.commit()
            db.refresh(case)
            return {
                "case_id": case.id,
                "payment_id": payment.payment_id,
                "action": final_action,
                "status": case.status.value,
                "previous_amount": amount_float,
                "recovered_amount": 0.0,
                "retry_count": payment.retry_count,
                "idempotent": False,
                "message": "Case escalated to human specialist.",
            }

        elif action_enum == RecoveryActionType.STOP_RECOVERY:
            case.status = RecoveryCaseStatus.STOPPED
            db.add(
                RecoveryAction(
                    recovery_case_id=case.id,
                    action_type=RecoveryActionType.STOP_RECOVERY,
                    reason="Recovery halted by policy limit.",
                    status=ActionExecutionStatus.EXECUTED,
                    executed_at=datetime.now(timezone.utc),
                )
            )
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="RECOVERY_STOPPED",
                    description="Automated recovery terminated.",
                    actor="POLICY_ENGINE",
                    metadata_={"action": "STOP_RECOVERY"},
                )
            )
            db.commit()
            db.refresh(case)
            return {
                "case_id": case.id,
                "payment_id": payment.payment_id,
                "action": final_action,
                "status": case.status.value,
                "previous_amount": amount_float,
                "recovered_amount": 0.0,
                "retry_count": payment.retry_count,
                "idempotent": False,
                "message": "Recovery stopped by policy.",
            }

        # 7. PROCESS SIMULATION OUTCOME
        if is_success:
            payment.status = PaymentStatus.RECOVERED
            payment.updated_at = datetime.now(timezone.utc)
            case.status = RecoveryCaseStatus.RECOVERED
            case.recovered_amount = payment.amount
            case.updated_at = datetime.now(timezone.utc)

            db.add(
                RecoveryAction(
                    recovery_case_id=case.id,
                    action_type=action_enum,
                    reason=f"Executed {final_action}. Payment recovered successfully.",
                    status=ActionExecutionStatus.EXECUTED,
                    executed_at=datetime.now(timezone.utc),
                    recovered_amount=payment.amount,
                    result=outcome_message,
                )
            )
            db.add(
                AuditLog(
                    recovery_case_id=case.id,
                    event_type="PAYMENT_RECOVERED",
                    description=f"Payment recovered successfully (₹{amount_float:,.2f}) via {final_action}.",
                    actor="RECOVERY_EXECUTION_ENGINE",
                    metadata_={
                        "payment_id": payment.payment_id,
                        "amount": amount_float,
                        "recovered_amount": amount_float,
                        "action": final_action,
                        "retry_count": payment.retry_count,
                        "result": "SUCCESS",
                    },
                )
            )
        else:
            # Check if retry limit was reached on this failure
            if payment.retry_count >= RecoveryConfig.MAX_RETRIES:
                case.status = RecoveryCaseStatus.STOPPED
                stop_note = f"Max retries ({payment.retry_count}/{RecoveryConfig.MAX_RETRIES}) reached. Recovery halted."
                db.add(
                    RecoveryAction(
                        recovery_case_id=case.id,
                        action_type=action_enum,
                        reason=f"Executed {final_action}. Failed. {stop_note}",
                        status=ActionExecutionStatus.FAILED,
                        executed_at=datetime.now(timezone.utc),
                        result=outcome_message,
                    )
                )
                db.add(
                    AuditLog(
                        recovery_case_id=case.id,
                        event_type="PAYMENT_FAILED",
                        description=f"Simulated payment attempt failed: {outcome_message}",
                        actor="PAYMENT_SIMULATOR",
                        metadata_={"payment_id": payment.payment_id, "retry_count": payment.retry_count, "result": "FAILED"},
                    )
                )
                db.add(
                    AuditLog(
                        recovery_case_id=case.id,
                        event_type="RECOVERY_STOPPED",
                        description=stop_note,
                        actor="POLICY_ENGINE",
                        metadata_={"retry_count": payment.retry_count},
                    )
                )
            else:
                case.status = RecoveryCaseStatus.FAILED
                db.add(
                    RecoveryAction(
                        recovery_case_id=case.id,
                        action_type=action_enum,
                        reason=f"Executed {final_action}. Failed. Eligible for further action if retries remain.",
                        status=ActionExecutionStatus.FAILED,
                        executed_at=datetime.now(timezone.utc),
                        result=outcome_message,
                    )
                )
                db.add(
                    AuditLog(
                        recovery_case_id=case.id,
                        event_type="PAYMENT_FAILED",
                        description=f"Simulated payment attempt failed: {outcome_message}",
                        actor="PAYMENT_SIMULATOR",
                        metadata_={"payment_id": payment.payment_id, "retry_count": payment.retry_count, "result": "FAILED"},
                    )
                )

        db.commit()
        db.refresh(case)
        db.refresh(payment)

        return {
            "case_id": case.id,
            "payment_id": payment.payment_id,
            "action": final_action,
            "status": case.status.value,
            "previous_amount": amount_float,
            "recovered_amount": float(case.recovered_amount or 0.0),
            "retry_count": payment.retry_count,
            "idempotent": False,
            "message": outcome_message if outcome_message else (
                "Payment successfully recovered." if is_success else "Recovery action executed; payment attempt failed."
            ),
        }

    @classmethod
    def execute_batch_recovery(
        cls,
        db: Session,
        limit: int = 500,
    ) -> Dict[str, Any]:
        """
        Executes automated recovery across a large batch of unrecovered payments.
        Pipes each through: Eligible -> Stop Check -> Policy -> Execute -> Simulate -> Settle.
        """
        # Ensure all failed/abandoned/expired payments have cases
        unrecovered_payments = (
            db.query(Payment)
            .filter(Payment.status.in_([PaymentStatus.FAILED, PaymentStatus.ABANDONED, PaymentStatus.EXPIRED]))
            .all()
        )

        for p in unrecovered_payments:
            if not p.recovery_case:
                RecoveryCaseService.create_or_update_recovery_case(p.id, db)

        # Select eligible cases (not yet RECOVERED, STOPPED, or ESCALATED)
        eligible_cases = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.status.in_([
                    RecoveryCaseStatus.OPEN,
                    RecoveryCaseStatus.IN_PROGRESS,
                    RecoveryCaseStatus.FAILED,
                    RecoveryCaseStatus.ACTION_APPROVED,
                ])
            )
            .limit(limit)
            .all()
        )

        cases_processed = 0
        actions_executed = 0
        payments_recovered = 0
        payments_failed = 0
        escalated_count = 0
        stopped_count = 0

        for case in eligible_cases:
            cases_processed += 1
            res = cls.execute_recovery_action(case.id, db)
            if not res:
                continue

            actions_executed += 1
            st = res.get("status")
            if st == RecoveryCaseStatus.RECOVERED.value:
                payments_recovered += 1
            elif st == RecoveryCaseStatus.ESCALATED.value:
                escalated_count += 1
            elif st == RecoveryCaseStatus.STOPPED.value:
                stopped_count += 1
            elif st == RecoveryCaseStatus.FAILED.value:
                payments_failed += 1

        # Calculate accurate financial aggregates from database
        all_cases = db.query(RecoveryCase).all()
        total_risk = sum(Decimal(str(c.revenue_at_risk)) for c in all_cases)
        total_potential = sum(
            Decimal(str(c.revenue_at_risk)) * (Decimal(str(c.recoverability_score)) / Decimal("100.0"))
            for c in all_cases
        )
        total_recovered = sum(Decimal(str(c.recovered_amount or 0.0)) for c in all_cases)

        recovery_rate = (
            round(float((total_recovered / total_potential) * Decimal("100.0")), 1)
            if total_potential > Decimal("0.00")
            else 0.0
        )

        return {
            "cases_processed": cases_processed,
            "actions_executed": actions_executed,
            "payments_recovered": payments_recovered,
            "payments_failed": payments_failed,
            "escalated": escalated_count,
            "stopped": stopped_count,
            "revenue_at_risk": float(total_risk),
            "potentially_recoverable": round(float(total_potential), 2),
            "recovered_revenue": round(float(total_recovered), 2),
            "recovery_rate": recovery_rate,
        }

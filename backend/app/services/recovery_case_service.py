from decimal import Decimal
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from sqlalchemy.orm import Session
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
from app.services.revenue_risk_service import RevenueRiskService
from app.recovery.diagnosis_engine import DiagnosisEngine
from app.recovery.strategy_selector import StrategySelector
from app.ml.feature_extractor import FeatureExtractor
from app.ml.model import RecoverabilityPredictor
from app.utils.logger import logger


class RecoveryCaseService:
    """
    End-to-end orchestration service for payment risk detection,
    diagnosis, ML recoverability prediction, and bounded recovery case creation.
    """

    @classmethod
    def create_or_update_recovery_case(
        cls,
        payment_id: Union[int, str],
        db: Session,
    ) -> Optional[RecoveryCase]:
        """
        Executes the full pipeline for a single payment.
        Accepts either internal numeric ID (e.g. 1) or payment reference string (e.g. "pay_...").
        """
        payment = None
        if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
            payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()

        if not payment:
            payment = db.query(Payment).filter(Payment.payment_id == str(payment_id)).first()

        if not payment:
            logger.warning(f"Payment '{payment_id}' not found.")
            return None

        # 1. Calculate Revenue at Risk
        revenue_at_risk = RevenueRiskService.calculate_revenue_at_risk(payment)

        # 2. Diagnose Failure
        diagnosis_result = DiagnosisEngine.diagnose(
            failure_reason=payment.failure_reason,
            status=payment.status,
        )

        # 3. Extract Features for ML
        feature_dict = FeatureExtractor.extract_from_payment_entity(payment)

        # 4. Predict Recoverability Score & Tier
        score, tier = RecoverabilityPredictor.predict_score(feature_dict)

        # 5. Select Initial Recovery Strategy
        customer = payment.customer
        c_succ = customer.successful_payments if customer else 0
        c_fail = customer.failed_payments if customer else 0
        c_rate = float(c_succ / (c_succ + c_fail)) if (c_succ + c_fail) > 0 else 0.8

        strategy = StrategySelector.select_strategy(
            diagnosis=diagnosis_result.diagnosis,
            recoverability_score=score,
            retry_count=payment.retry_count or 0,
            amount=float(payment.amount),
            customer_success_rate=c_rate,
            customer_failed_payments=c_fail,
        )

        # 6. Create or Update RecoveryCase entity
        recovery_case = (
            db.query(RecoveryCase)
            .filter(RecoveryCase.payment_id == payment.id)
            .first()
        )

        is_new = False
        if not recovery_case:
            is_new = True
            recovery_case = RecoveryCase(
                payment_id=payment.id,
                revenue_at_risk=revenue_at_risk,
                recoverability_score=score,
                diagnosis=diagnosis_result.diagnosis,
                recommended_action=strategy.action_type.value,
                status=RecoveryCaseStatus.OPEN,
                recovered_amount=Decimal("0.00"),
            )
            db.add(recovery_case)
            db.flush()
        else:
            if revenue_at_risk > Decimal("0.00"):
                recovery_case.revenue_at_risk = revenue_at_risk
            elif not recovery_case.revenue_at_risk or recovery_case.revenue_at_risk == Decimal("0.00"):
                recovery_case.revenue_at_risk = Decimal(str(payment.amount))
            recovery_case.recoverability_score = score
            recovery_case.diagnosis = diagnosis_result.diagnosis
            recovery_case.recommended_action = strategy.action_type.value
            recovery_case.updated_at = datetime.now(timezone.utc)

        # 7. Record Recovery Action Record if recommended action not yet present
        existing_action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id == recovery_case.id,
                RecoveryAction.action_type == strategy.action_type,
            )
            .first()
        )
        if not existing_action:
            action_record = RecoveryAction(
                recovery_case_id=recovery_case.id,
                action_type=strategy.action_type,
                reason=strategy.reason,
                status=ActionExecutionStatus.PENDING,
            )
            db.add(action_record)

        # 8. Record Audit Log
        event_name = "CASE_CREATED" if is_new else "CASE_REANALYZED"
        audit_entry = AuditLog(
            recovery_case_id=recovery_case.id,
            event_type=event_name,
            description=(
                f"Analyzed payment {payment.payment_id} (₹{payment.amount}). "
                f"Diagnosis: {diagnosis_result.diagnosis} ({diagnosis_result.severity}). "
                f"Recoverability: {score}% ({tier}). "
                f"Recommended: {strategy.action_type.value}."
            ),
            actor="RECOVERY_PIPELINE",
            metadata_={
                "diagnosis": diagnosis_result.diagnosis,
                "score": score,
                "tier": tier,
                "action": strategy.action_type.value,
                "reason": strategy.reason,
            },
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(recovery_case)
        return recovery_case

    @classmethod
    def analyze_batch(
        cls,
        db: Session,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """
        Batch analyzes all eligible unrecovered payments (FAILED, ABANDONED, EXPIRED).
        """
        eligible_payments = (
            db.query(Payment)
            .filter(Payment.status.in_([PaymentStatus.FAILED, PaymentStatus.ABANDONED, PaymentStatus.EXPIRED]))
            .limit(limit)
            .all()
        )

        analyzed_count = 0
        total_risk = Decimal("0.00")
        total_potential = Decimal("0.00")
        high_count = 0
        medium_count = 0
        low_count = 0

        for payment in eligible_payments:
            case = cls.create_or_update_recovery_case(payment.id, db)
            if case:
                analyzed_count += 1
                total_risk += case.revenue_at_risk
                potential_share = case.revenue_at_risk * (Decimal(str(case.recoverability_score)) / Decimal("100.0"))
                total_potential += potential_share

                if case.recoverability_score >= 70.0:
                    high_count += 1
                elif case.recoverability_score >= 30.0:
                    medium_count += 1
                else:
                    low_count += 1

        return {
            "payments_analyzed": analyzed_count,
            "revenue_at_risk": float(total_risk),
            "potentially_recoverable": round(float(total_potential), 2),
            "high_recoverability": high_count,
            "medium_recoverability": medium_count,
            "low_recoverability": low_count,
        }

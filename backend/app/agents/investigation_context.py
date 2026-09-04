from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.agents.investigation_tools import (
    get_payment_details,
    get_customer_profile,
    get_payment_history,
    get_failure_history,
    get_recovery_history,
    get_subscription_status,
    get_customer_payment_patterns,
)
from app.ml.feature_extractor import FeatureExtractor
from app.ml.model import RecoverabilityPredictor
from app.recovery.diagnosis_engine import DiagnosisEngine
from app.recovery.strategy_selector import StrategySelector
from app.models.enums import FailureReason, PaymentStatus


@dataclass
class InvestigationContext:
    payment: Dict[str, Any]
    customer: Dict[str, Any]
    payment_history: List[Dict[str, Any]]
    failure_history: List[Dict[str, Any]]
    recovery_history: List[Dict[str, Any]]
    subscription_status: List[Dict[str, Any]]
    payment_patterns: Dict[str, Any]
    ml_prediction: Dict[str, Any]
    deterministic_diagnosis: Dict[str, Any]
    deterministic_strategy: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_prompt_text(self) -> str:
        """
        Formats the sanitized investigation context into structured markdown
        for the Gemini prompt.
        """
        p = self.payment
        c = self.customer
        ml = self.ml_prediction
        diag = self.deterministic_diagnosis
        strat = self.deterministic_strategy
        patterns = self.payment_patterns

        history_summary = "\n".join(
            [
                f"- Tx ID: {item.get('payment_id')}, Amount: ₹{item.get('amount')}, Status: {item.get('status')}, Reason: {item.get('failure_reason') or 'N/A'}, Retries: {item.get('retry_count')}"
                for item in self.payment_history[:5]
            ]
        ) or "No prior payment records found."

        subs_summary = "\n".join(
            [
                f"- Sub ID: {s.get('subscription_id')}, Plan: {s.get('billing_cycle')}, Status: {s.get('status')}, Next Date: {s.get('next_payment_date')}"
                for s in self.subscription_status
            ]
        ) or "No recurring subscriptions."

        recovery_actions_summary = "\n".join(
            [
                f"- Action: {r.get('action_type')}, Result: {r.get('result')}, Recovered: ₹{r.get('recovered_amount')}"
                for r in self.recovery_history[:5]
            ]
        ) or "No prior recovery actions recorded."

        return f"""### CURRENT TRANSACTION UNDER INVESTIGATION
- Payment ID: {p.get('payment_id')}
- Amount: ₹{p.get('amount'):,.2f} ({p.get('currency', 'INR')})
- Payment Method: {p.get('payment_method')}
- Payment Status: {p.get('status')}
- Gateway Failure Reason: {p.get('failure_reason') or 'NONE/ABANDONED'}
- Automated Retry Count to Date: {p.get('retry_count', 0)} / 3 (Max Limit)
- Merchant Name: {p.get('merchant_name')}
- Timestamp: {p.get('created_at')}

### CUSTOMER HISTORICAL PROFILE & TELEMETRY
- Name: {c.get('name', 'Unknown')} (ID: {c.get('customer_id')})
- Account Age: {c.get('account_age_days', 0)} days
- Total Lifetime Payments: {c.get('total_payments', 0)}
- Successful Payments: {c.get('successful_payments', 0)}
- Failed Payments: {c.get('failed_payments', 0)}
- Historical Success Rate: {c.get('success_rate', 0.0) * 100:.1f}%
- Average Payment Amount: ₹{c.get('average_payment_amount', 0.0):,.2f}
- Preferred Payment Instrument: {patterns.get('preferred_method') or 'N/A'}

### SUBSCRIPTION & RECURRING COMMERCE STATUS
{subs_summary}

### PRIOR ATTEMPTS & RECOVERY LOG
{recovery_actions_summary}

### RECENT PAYMENT TELEMETRY (LATEST 5)
{history_summary}

### BASELINE ML PREDICTOR SIGNALS
- ML Estimated Recoverability Score: {ml.get('score')} / 100.0 (Tier: {ml.get('tier')})
- Key Predictive Factors:
  * Customer Success Rate: {c.get('success_rate', 0.0) * 100:.1f}%
  * Accumulated Retries: {p.get('retry_count', 0)}
  * Ticket Size vs Avg: ₹{p.get('amount', 0.0):,.2f} vs ₹{c.get('average_payment_amount', 0.0):,.2f}

### DETERMINISTIC HEURISTIC BASELINE
- Rule-Engine Diagnosis: {diag.get('diagnosis')} ({diag.get('severity')} severity)
- Heuristic Strategy: {strat.get('action_type')}
- Heuristic Rationale: {strat.get('reason')}
"""


class InvestigationContextBuilder:
    """
    Orchestrates the 7 read-only database tools and feature extraction
    to assemble a sanitized, comprehensive context for the recovery agent.
    """

    @classmethod
    def build(cls, payment_id: Union[int, str], db: Session) -> Optional[InvestigationContext]:
        payment = get_payment_details(payment_id, db)
        if not payment:
            return None

        customer_id = payment["customer_id"]
        customer = get_customer_profile(customer_id, db)
        payment_history = get_payment_history(customer_id, db, limit=10)
        failure_history = get_failure_history(customer_id, db)
        recovery_history = get_recovery_history(customer_id, db)
        subscription_status = get_subscription_status(customer_id, db)
        payment_patterns = get_customer_payment_patterns(customer_id, db)

        # ML Feature Extraction & Prediction
        status_enum = None
        try:
            status_enum = PaymentStatus(payment["status"])
        except (ValueError, TypeError):
            pass

        failure_reason_enum = None
        if payment.get("failure_reason"):
            try:
                failure_reason_enum = FailureReason(payment["failure_reason"])
            except (ValueError, TypeError):
                pass

        features = FeatureExtractor.extract_features(
            amount=payment["amount"],
            customer_avg_amount=customer.get("average_payment_amount", payment["amount"]),
            customer_successful_payments=customer.get("successful_payments", 0),
            customer_failed_payments=customer.get("failed_payments", 0),
            customer_account_age_days=customer.get("account_age_days", 30),
            retry_count=payment["retry_count"],
            failure_reason=payment.get("failure_reason"),
            payment_method=payment.get("payment_method", "UPI"),
            is_subscription=len(subscription_status) > 0,
        )

        ml_score, ml_tier = RecoverabilityPredictor.predict_score(features)
        ml_prediction = {
            "score": ml_score,
            "tier": ml_tier,
            "features": features,
        }

        # Deterministic Diagnosis
        diag = DiagnosisEngine.diagnose(
            failure_reason=failure_reason_enum,
            status=status_enum,
        )
        deterministic_diagnosis = {
            "diagnosis": diag.diagnosis,
            "explanation": diag.explanation,
            "severity": diag.severity,
            "retry_appropriate": diag.retry_appropriate,
        }

        # Deterministic Strategy
        strat = StrategySelector.select_strategy(
            diagnosis=diag.diagnosis,
            recoverability_score=ml_score,
            retry_count=payment["retry_count"],
            amount=payment["amount"],
            customer_success_rate=customer.get("success_rate", 1.0),
            customer_failed_payments=customer.get("failed_payments", 0),
        )
        deterministic_strategy = {
            "action_type": strat.action_type.value if hasattr(strat.action_type, "value") else str(strat.action_type),
            "reason": strat.reason,
            "priority": strat.priority,
        }

        return InvestigationContext(
            payment=payment,
            customer=customer,
            payment_history=payment_history,
            failure_history=failure_history,
            recovery_history=recovery_history,
            subscription_status=subscription_status,
            payment_patterns=payment_patterns,
            ml_prediction=ml_prediction,
            deterministic_diagnosis=deterministic_diagnosis,
            deterministic_strategy=deterministic_strategy,
        )

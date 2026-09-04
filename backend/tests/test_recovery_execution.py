from decimal import Decimal
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import pytest

from app.models import (
    Payment,
    Customer,
    Merchant,
    RecoveryCase,
    RecoveryAction,
    AuditLog,
    PaymentStatus,
    FailureReason,
    RecoveryCaseStatus,
    RecoveryActionType,
    ActionExecutionStatus,
)
from app.recovery.config import RecoveryConfig, StoppingRules
from app.recovery.state_machine import RecoveryCaseStateMachine, InvalidStateTransitionError
from app.recovery.simulator import PaymentSimulator
from app.services.recovery_execution_service import RecoveryExecutionService
from app.services.recovery_analytics_service import RecoveryAnalyticsService
from app.agents.gemini_agent import GeminiAgent


@pytest.fixture(autouse=True)
def mock_gemini_for_execution_tests():
    with patch("app.agents.gemini_agent.GeminiAgent.investigate") as mock_investigate:
        def side_effect(ctx):
            fb = GeminiAgent.generate_fallback_investigation(ctx)
            return fb, False
        mock_investigate.side_effect = side_effect
        yield


# ============================================================
# 1. State Machine & Stopping Rules Tests
# ============================================================

def test_state_machine_valid_transitions():
    case = RecoveryCase(
        payment_id=1,
        revenue_at_risk=Decimal("5000.00"),
        recoverability_score=80.0,
        status=RecoveryCaseStatus.OPEN,
    )

    RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.INVESTIGATING)
    assert case.status == RecoveryCaseStatus.INVESTIGATING

    RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.ACTION_APPROVED)
    assert case.status == RecoveryCaseStatus.ACTION_APPROVED

    RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.ACTION_EXECUTED)
    assert case.status == RecoveryCaseStatus.ACTION_EXECUTED

    RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.RECOVERED)
    assert case.status == RecoveryCaseStatus.RECOVERED


def test_state_machine_invalid_transitions():
    case = RecoveryCase(
        payment_id=1,
        revenue_at_risk=Decimal("5000.00"),
        recoverability_score=80.0,
        status=RecoveryCaseStatus.RECOVERED,  # Terminal state
    )

    with pytest.raises(InvalidStateTransitionError):
        RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.OPEN)

    with pytest.raises(InvalidStateTransitionError):
        RecoveryCaseStateMachine.transition(case, RecoveryCaseStatus.ACTION_EXECUTED)


def test_stopping_rules_max_retries():
    should_stop, reason, target = StoppingRules.evaluate(
        payment_status=PaymentStatus.FAILED,
        case_status=RecoveryCaseStatus.OPEN,
        retry_count=3,
        recoverability_score=75.0,
    )
    assert should_stop is True
    assert target == RecoveryCaseStatus.STOPPED
    assert "Maximum retry" in reason


def test_stopping_rules_already_recovered():
    should_stop, reason, target = StoppingRules.evaluate(
        payment_status=PaymentStatus.RECOVERED,
        case_status=RecoveryCaseStatus.RECOVERED,
        retry_count=1,
        recoverability_score=90.0,
    )
    assert should_stop is True
    assert target == RecoveryCaseStatus.RECOVERED


def test_stopping_rules_window_expired():
    old_time = datetime.now(timezone.utc) - timedelta(hours=50)
    should_stop, reason, target = StoppingRules.evaluate(
        payment_status=PaymentStatus.FAILED,
        case_status=RecoveryCaseStatus.OPEN,
        retry_count=1,
        recoverability_score=80.0,
        created_at=old_time,
    )
    assert should_stop is True
    assert target == RecoveryCaseStatus.STOPPED
    assert "Recovery window" in reason


# ============================================================
# 2. Simulator & Execution Service Unit Tests
# ============================================================

def test_payment_simulator_deterministic():
    dummy_payment = Payment(
        payment_id="sim_test_01",
        amount=Decimal("5000.00"),
        currency="INR",
        payment_method="UPI",
        status=PaymentStatus.FAILED,
        failure_reason=FailureReason.BANK_TIMEOUT,
        retry_count=0,
    )

    succ1, msg1 = PaymentSimulator.simulate_payment_attempt(
        dummy_payment, "RETRY_LATER", recoverability_score=95.0
    )
    succ2, msg2 = PaymentSimulator.simulate_payment_attempt(
        dummy_payment, "RETRY_LATER", recoverability_score=95.0
    )

    assert succ1 == succ2
    assert msg1 == msg2


def test_execute_recovery_successful(db_session):
    # Find or use pay_demo_01_bank_timeout
    payment = db_session.query(Payment).filter(Payment.payment_id == "pay_demo_01_bank_timeout").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    # Reset state to open for isolated test
    case.status = RecoveryCaseStatus.OPEN
    case.recovered_amount = Decimal("0.00")
    payment.status = PaymentStatus.FAILED
    payment.retry_count = 0
    case.final_action = "RETRY_LATER"
    case.policy_result = "ALLOWED"
    db_session.commit()

    try:
        res = RecoveryExecutionService.execute_recovery_action(case.id, db_session)
        assert res is not None
        assert res["status"] in ["RECOVERED", "FAILED"]
        if res["status"] == "RECOVERED":
            assert res["recovered_amount"] == float(payment.amount)
            assert payment.status == PaymentStatus.RECOVERED
    finally:
        case.status = RecoveryCaseStatus.OPEN
        case.recovered_amount = Decimal("0.00")
        payment.status = PaymentStatus.FAILED
        payment.retry_count = 0
        db_session.commit()


def test_idempotent_execution_double_count_prevention(db_session):
    # Retrieve a recovered payment
    payment = db_session.query(Payment).filter(Payment.payment_id == "PAY_10482").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    # Ensure it is recovered
    case.status = RecoveryCaseStatus.RECOVERED
    case.recovered_amount = Decimal("8500.00")
    payment.status = PaymentStatus.RECOVERED
    db_session.commit()

    # Call execute_recovery_action twice
    res1 = RecoveryExecutionService.execute_recovery_action(case.id, db_session)
    res2 = RecoveryExecutionService.execute_recovery_action(case.id, db_session)

    assert res1["idempotent"] is True
    assert res2["idempotent"] is True
    assert res1["recovered_amount"] == 8500.0
    assert res2["recovered_amount"] == 8500.0
    # Ensure recovered amount didn't double to 17000
    db_session.refresh(case)
    assert float(case.recovered_amount) == 8500.0


def test_execute_recovery_max_retries_stops(db_session):
    payment = db_session.query(Payment).filter(Payment.payment_id == "pay_demo_05_max_retries_halted").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    case.status = RecoveryCaseStatus.OPEN
    payment.retry_count = 3
    db_session.commit()

    res = RecoveryExecutionService.execute_recovery_action(case.id, db_session)
    assert res is not None
    assert res["status"] == "STOPPED"
    assert res["recovered_amount"] == 0.0


def test_execute_recovery_escalate_to_human(db_session):
    payment = db_session.query(Payment).filter(Payment.payment_id == "pay_demo_03_card_declined").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    case.status = RecoveryCaseStatus.OPEN
    case.final_action = "ESCALATE_TO_HUMAN"
    case.policy_result = "ALLOWED"
    db_session.commit()

    res = RecoveryExecutionService.execute_recovery_action(case.id, db_session)
    assert res is not None
    assert res["status"] == "ESCALATED"
    assert case.escalation_required is True


# ============================================================
# 3. API Endpoints Tests
# ============================================================

def test_api_execute_recovery(client, db_session):
    payment = db_session.query(Payment).filter(Payment.payment_id == "pay_demo_02_insufficient_funds").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    case.status = RecoveryCaseStatus.OPEN
    db_session.commit()

    try:
        response = client.post(f"/api/recovery/execute/{case.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == case.id
        assert "status" in data
        assert "recovered_amount" in data
    finally:
        case.status = RecoveryCaseStatus.OPEN
        case.recovered_amount = Decimal("0.00")
        payment.status = PaymentStatus.FAILED
        payment.retry_count = 1
        db_session.commit()


def test_api_run_batch_recovery(client):
    response = client.post("/api/recovery/run-batch?limit=25")
    assert response.status_code == 200
    data = response.json()
    assert data["cases_processed"] > 0
    assert "recovered_revenue" in data
    assert "recovery_rate" in data
    assert data["recovery_rate"] >= 0.0


def test_api_case_timeline(client, db_session):
    payment = db_session.query(Payment).filter(Payment.payment_id == "PAY_10482").first()
    assert payment is not None
    case = payment.recovery_case
    assert case is not None

    response = client.get(f"/api/recovery/cases/{case.id}/timeline")
    assert response.status_code == 200
    timeline = response.json()
    assert isinstance(timeline, list)
    assert len(timeline) > 0
    assert "event" in timeline[0]
    assert "actor" in timeline[0]
    assert "description" in timeline[0]


def test_api_analytics_overview(client):
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "revenue_at_risk" in data
    assert "potentially_recoverable" in data
    assert "recovered_revenue" in data
    assert "recovery_rate" in data
    assert "active_cases" in data


def test_api_analytics_recovery_trend(client):
    response = client.get("/api/analytics/recovery-trend?days=7")
    assert response.status_code == 200
    trend = response.json()
    assert isinstance(trend, list)
    assert len(trend) > 0
    assert "date" in trend[0]
    assert "revenue_at_risk" in trend[0]
    assert "recovered" in trend[0]


def test_api_analytics_action_breakdown(client):
    response = client.get("/api/analytics/action-breakdown")
    assert response.status_code == 200
    breakdown = response.json()
    assert isinstance(breakdown, list)
    if len(breakdown) > 0:
        assert "action" in breakdown[0]
        assert "attempts" in breakdown[0]
        assert "recovered_amount" in breakdown[0]


def test_api_analytics_failure_breakdown(client):
    response = client.get("/api/analytics/failure-breakdown")
    assert response.status_code == 200
    breakdown = response.json()
    assert isinstance(breakdown, list)
    assert len(breakdown) > 0
    assert "failure_reason" in breakdown[0]
    assert "count" in breakdown[0]
    assert "amount_at_risk" in breakdown[0]


# ============================================================
# 4. PAY_10482 End-to-End Test
# ============================================================

def test_pay_10482_end_to_end_flow(client, db_session):
    payment = db_session.query(Payment).filter(Payment.payment_id == "PAY_10482").first()
    assert payment is not None
    assert float(payment.amount) == 8500.0
    assert payment.failure_reason == FailureReason.BANK_TIMEOUT

    # Execute recovery action
    case = payment.recovery_case
    response = client.post(f"/api/recovery/execute/{case.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["payment_id"] == "PAY_10482"
    assert data["status"] == "RECOVERED"
    assert data["recovered_amount"] == 8500.0

    # Verify audit timeline
    timeline_res = client.get(f"/api/recovery/cases/{case.id}/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    events = [item["event"] for item in timeline]
    assert "PAYMENT_RECOVERED" in events

    # Verify idempotent double-call
    repeat_res = client.post(f"/api/recovery/execute/{case.id}")
    assert repeat_res.status_code == 200
    repeat_data = repeat_res.json()
    assert repeat_data["idempotent"] is True
    assert repeat_data["recovered_amount"] == 8500.0

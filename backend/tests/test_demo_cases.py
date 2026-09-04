from decimal import Decimal
from app.models.enums import RecoveryActionType


def test_demo_case_1_bank_timeout(client):
    res = client.post("/api/recovery/analyze/pay_demo_01_bank_timeout")
    assert res.status_code == 200
    data = res.json()
    assert data["revenue_at_risk"] == 8500.0 or data["revenue_at_risk"] == "8500.00"
    assert data["diagnosis"] == "TEMPORARY_BANK_FAILURE"
    assert data["recoverability_score"] >= 70.0  # HIGH
    assert data["recommended_action"] == RecoveryActionType.RETRY_LATER.value


def test_demo_case_2_insufficient_funds(client):
    res = client.post("/api/recovery/analyze/pay_demo_02_insufficient_funds")
    assert res.status_code == 200
    data = res.json()
    assert data["revenue_at_risk"] == 4500.0 or data["revenue_at_risk"] == "4500.00"
    assert data["diagnosis"] == "INSUFFICIENT_FUNDS"
    assert data["recoverability_score"] >= 30.0  # MEDIUM or HIGH
    assert data["recommended_action"] == RecoveryActionType.SEND_PAYMENT_LINK.value


def test_demo_case_3_card_declined(client):
    res = client.post("/api/recovery/analyze/pay_demo_03_card_declined")
    assert res.status_code == 200
    data = res.json()
    assert data["revenue_at_risk"] == 12000.0 or data["revenue_at_risk"] == "12000.00"
    assert data["diagnosis"] == "PAYMENT_METHOD_DECLINED"
    assert data["recoverability_score"] < 70.0  # LOW / MEDIUM
    assert data["recommended_action"] in [
        RecoveryActionType.CHANGE_PAYMENT_METHOD.value,
        RecoveryActionType.ESCALATE_TO_HUMAN.value,
    ]


def test_demo_case_4_checkout_abandoned(client):
    res = client.post("/api/recovery/analyze/pay_demo_04_checkout_abandoned")
    assert res.status_code == 200
    data = res.json()
    assert data["revenue_at_risk"] == 2500.0 or data["revenue_at_risk"] == "2500.00"
    assert data["diagnosis"] == "CHECKOUT_ABANDONMENT"
    assert data["recoverability_score"] >= 70.0  # HIGH
    assert data["recommended_action"] == RecoveryActionType.SEND_REMINDER.value


def test_demo_case_5_max_retries_halted(client):
    res = client.post("/api/recovery/analyze/pay_demo_05_max_retries_halted")
    assert res.status_code == 200
    data = res.json()
    assert data["revenue_at_risk"] == 15000.0 or data["revenue_at_risk"] == "15000.00"
    assert data["recommended_action"] == RecoveryActionType.STOP_RECOVERY.value

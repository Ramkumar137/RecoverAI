from app.models.enums import RecoveryActionType
from app.recovery.strategy_selector import StrategySelector


def test_strategy_stop_recovery_on_max_retries():
    rec = StrategySelector.select_strategy(
        diagnosis="TEMPORARY_BANK_FAILURE",
        recoverability_score=95.0,
        retry_count=3,
    )
    assert rec.action_type == RecoveryActionType.STOP_RECOVERY


def test_strategy_retry_later_for_high_bank_timeout():
    rec = StrategySelector.select_strategy(
        diagnosis="TEMPORARY_BANK_FAILURE",
        recoverability_score=85.0,
        retry_count=1,
    )
    assert rec.action_type == RecoveryActionType.RETRY_LATER


def test_strategy_send_payment_link_for_insufficient_funds():
    rec = StrategySelector.select_strategy(
        diagnosis="INSUFFICIENT_FUNDS",
        recoverability_score=65.0,
        retry_count=0,
    )
    assert rec.action_type == RecoveryActionType.SEND_PAYMENT_LINK


def test_strategy_escalate_for_high_declines():
    rec = StrategySelector.select_strategy(
        diagnosis="PAYMENT_METHOD_DECLINED",
        recoverability_score=20.0,
        retry_count=2,
        amount=15000.0,
        customer_failed_payments=4,
    )
    assert rec.action_type == RecoveryActionType.ESCALATE_TO_HUMAN


def test_strategy_send_reminder_for_abandonment():
    rec = StrategySelector.select_strategy(
        diagnosis="CHECKOUT_ABANDONMENT",
        recoverability_score=75.0,
        retry_count=0,
    )
    assert rec.action_type == RecoveryActionType.SEND_REMINDER

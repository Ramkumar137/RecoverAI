from decimal import Decimal
from app.models import Payment, PaymentStatus, FailureReason
from app.services.revenue_risk_service import RevenueRiskService


def test_calculate_revenue_at_risk_failed_payment():
    p = Payment(
        payment_id="pay_test_01",
        customer_id=1,
        merchant_id=1,
        amount=Decimal("5000.00"),
        currency="INR",
        payment_method="UPI",
        status=PaymentStatus.FAILED,
        failure_reason=FailureReason.BANK_TIMEOUT,
    )
    risk = RevenueRiskService.calculate_revenue_at_risk(p)
    assert risk == Decimal("5000.00")
    assert RevenueRiskService.is_revenue_at_risk(p) is True


def test_calculate_revenue_at_risk_success_payment():
    p = Payment(
        payment_id="pay_test_02",
        customer_id=1,
        merchant_id=1,
        amount=Decimal("3500.00"),
        currency="INR",
        payment_method="CARD",
        status=PaymentStatus.SUCCESS,
    )
    risk = RevenueRiskService.calculate_revenue_at_risk(p)
    assert risk == Decimal("0.00")
    assert RevenueRiskService.is_revenue_at_risk(p) is False


def test_calculate_revenue_at_risk_abandoned_payment():
    p = Payment(
        payment_id="pay_test_03",
        customer_id=1,
        merchant_id=1,
        amount=Decimal("2500.00"),
        currency="INR",
        payment_method="UPI",
        status=PaymentStatus.ABANDONED,
    )
    risk = RevenueRiskService.calculate_revenue_at_risk(p)
    assert risk == Decimal("2500.00")

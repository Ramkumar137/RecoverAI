from decimal import Decimal
from app.models import Customer, Merchant, Payment, Subscription, RecoveryCase, RecoveryAction, AuditLog
from app.models.enums import PaymentStatus, FailureReason, RecoveryActionType, RecoveryCaseStatus


def test_models_instantiation(db_session):
    # Verify Customer
    customer = Customer(
        customer_id="cust_unit_test_01",
        name="Unit Test Customer",
        email="unittest@example.com",
        account_age_days=120,
        total_payments=10,
        successful_payments=9,
        failed_payments=1,
        average_payment_amount=Decimal("3000.00"),
    )
    assert customer.name == "Unit Test Customer"
    assert repr(customer).startswith("<Customer")

    # Verify Merchant
    merchant = Merchant(
        merchant_id="merch_unit_test_01",
        name="Unit Test Merchant",
        category="SaaS",
        average_payment_amount=Decimal("3000.00"),
    )
    assert repr(merchant).startswith("<Merchant")

    # Verify Payment
    payment = Payment(
        payment_id="pay_unit_test_01",
        customer_id=1,
        merchant_id=1,
        amount=Decimal("2999.00"),
        currency="INR",
        payment_method="UPI",
        status=PaymentStatus.FAILED,
        failure_reason=FailureReason.BANK_TIMEOUT,
    )
    assert payment.amount == Decimal("2999.00")
    assert repr(payment).startswith("<Payment")

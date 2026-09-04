from app.models.enums import FailureReason, PaymentStatus
from app.recovery.diagnosis_engine import DiagnosisEngine


def test_diagnosis_mappings():
    # Bank Timeout
    d1 = DiagnosisEngine.diagnose(FailureReason.BANK_TIMEOUT, PaymentStatus.FAILED)
    assert d1.diagnosis == "TEMPORARY_BANK_FAILURE"
    assert d1.retry_appropriate is True

    # Network Error
    d2 = DiagnosisEngine.diagnose(FailureReason.NETWORK_ERROR, PaymentStatus.FAILED)
    assert d2.diagnosis == "TEMPORARY_PAYMENT_FAILURE"
    assert d2.retry_appropriate is True

    # Card Declined
    d3 = DiagnosisEngine.diagnose(FailureReason.CARD_DECLINED, PaymentStatus.FAILED)
    assert d3.diagnosis == "PAYMENT_METHOD_DECLINED"
    assert d3.retry_appropriate is False

    # Authentication Failed
    d4 = DiagnosisEngine.diagnose(FailureReason.AUTHENTICATION_FAILED, PaymentStatus.FAILED)
    assert d4.diagnosis == "CUSTOMER_AUTHENTICATION_REQUIRED"

    # Limit Exceeded
    d5 = DiagnosisEngine.diagnose(FailureReason.LIMIT_EXCEEDED, PaymentStatus.FAILED)
    assert d5.diagnosis == "PAYMENT_LIMIT_EXCEEDED"

    # Abandoned Checkout
    d6 = DiagnosisEngine.diagnose(None, PaymentStatus.ABANDONED)
    assert d6.diagnosis == "CHECKOUT_ABANDONMENT"

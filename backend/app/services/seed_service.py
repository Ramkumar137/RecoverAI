from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Customer,
    Merchant,
    Payment,
    Subscription,
    RecoveryCase,
    RecoveryAction,
    AuditLog,
    PaymentStatus,
    FailureReason,
    RecoveryActionType,
    RecoveryCaseStatus,
    ActionExecutionStatus,
)
from app.utils.logger import logger


def seed_prototype_data_if_empty(db: Session) -> None:
    """
    Seeds initial realistic prototype records if the database is currently empty.
    """
    customer_count = db.query(Customer).count()
    if customer_count > 0:
        logger.info("Database already contains data; skipping seed.")
        return

    logger.info("Seeding initial prototype records into PostgreSQL...")

    # Merchants
    merchants = [
        Merchant(
            merchant_id="merch_subhub_01",
            name="SaaS Stream Pro",
            category="Software Subscription",
            average_payment_amount=Decimal("2499.00"),
        ),
        Merchant(
            merchant_id="merch_cloudpay_02",
            name="QuickCloud Hosting",
            category="Infrastructure",
            average_payment_amount=Decimal("4999.00"),
        ),
        Merchant(
            merchant_id="merch_edutech_03",
            name="SkillForge Academy",
            category="Education",
            average_payment_amount=Decimal("1299.00"),
        ),
    ]
    db.add_all(merchants)
    db.flush()

    # Customers
    customers = [
        Customer(
            customer_id="cust_rahul_101",
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            account_age_days=180,
            total_payments=12,
            successful_payments=11,
            failed_payments=1,
            average_payment_amount=Decimal("2499.00"),
        ),
        Customer(
            customer_id="cust_priya_102",
            name="Priya Patel",
            email="priya.patel@example.com",
            account_age_days=95,
            total_payments=6,
            successful_payments=4,
            failed_payments=2,
            average_payment_amount=Decimal("4999.00"),
        ),
        Customer(
            customer_id="cust_vikram_103",
            name="Vikram Verma",
            email="vikram.verma@example.com",
            account_age_days=310,
            total_payments=24,
            successful_payments=22,
            failed_payments=2,
            average_payment_amount=Decimal("1299.00"),
        ),
        Customer(
            customer_id="cust_ananya_104",
            name="Ananya Iyer",
            email="ananya.iyer@example.com",
            account_age_days=45,
            total_payments=2,
            successful_payments=1,
            failed_payments=1,
            average_payment_amount=Decimal("2499.00"),
        ),
    ]
    db.add_all(customers)
    db.flush()

    # Subscriptions
    now = datetime.now(timezone.utc)
    subscriptions = [
        Subscription(
            subscription_id="sub_rahul_01",
            customer_id=customers[0].id,
            merchant_id=merchants[0].id,
            amount=Decimal("2499.00"),
            billing_cycle="MONTHLY",
            status="ACTIVE",
            next_payment_date=now + timedelta(days=25),
            retry_count=1,
        ),
        Subscription(
            subscription_id="sub_priya_02",
            customer_id=customers[1].id,
            merchant_id=merchants[1].id,
            amount=Decimal("4999.00"),
            billing_cycle="MONTHLY",
            status="PAST_DUE",
            next_payment_date=now - timedelta(days=2),
            retry_count=2,
        ),
    ]
    db.add_all(subscriptions)
    db.flush()

    # Payments
    payments = [
        Payment(
            payment_id="pay_insuf_9001",
            customer_id=customers[0].id,
            merchant_id=merchants[0].id,
            amount=Decimal("2499.00"),
            currency="INR",
            payment_method="UPI",
            status=PaymentStatus.FAILED,
            failure_reason=FailureReason.INSUFFICIENT_FUNDS,
            retry_count=1,
        ),
        Payment(
            payment_id="pay_timeout_9002",
            customer_id=customers[1].id,
            merchant_id=merchants[1].id,
            amount=Decimal("4999.00"),
            currency="INR",
            payment_method="CARD",
            status=PaymentStatus.FAILED,
            failure_reason=FailureReason.BANK_TIMEOUT,
            retry_count=1,
        ),
        Payment(
            payment_id="pay_neterr_9003",
            customer_id=customers[2].id,
            merchant_id=merchants[2].id,
            amount=Decimal("1299.00"),
            currency="INR",
            payment_method="NETBANKING",
            status=PaymentStatus.RECOVERED,
            failure_reason=FailureReason.NETWORK_ERROR,
            retry_count=2,
        ),
        Payment(
            payment_id="pay_auth_9004",
            customer_id=customers[3].id,
            merchant_id=merchants[0].id,
            amount=Decimal("2499.00"),
            currency="INR",
            payment_method="CARD",
            status=PaymentStatus.FAILED,
            failure_reason=FailureReason.AUTHENTICATION_FAILED,
            retry_count=1,
        ),
    ]
    db.add_all(payments)
    db.flush()

    # Recovery Cases
    case1 = RecoveryCase(
        payment_id=payments[0].id,
        revenue_at_risk=Decimal("2499.00"),
        recoverability_score=0.88,
        diagnosis="Customer has high payment history; failure likely due to temporary end-of-month liquidity constraint.",
        recommended_action=RecoveryActionType.RETRY_LATER.value,
        status=RecoveryCaseStatus.OPEN,
        recovered_amount=Decimal("0.00"),
    )
    case2 = RecoveryCase(
        payment_id=payments[1].id,
        revenue_at_risk=Decimal("4999.00"),
        recoverability_score=0.74,
        diagnosis="Issuing bank gateway suffered transient timeout during OTP verification step.",
        recommended_action=RecoveryActionType.RETRY_PAYMENT.value,
        status=RecoveryCaseStatus.IN_PROGRESS,
        recovered_amount=Decimal("0.00"),
    )
    case3 = RecoveryCase(
        payment_id=payments[2].id,
        revenue_at_risk=Decimal("1299.00"),
        recoverability_score=0.95,
        diagnosis="Intermittent network drop during handoff; recovered via payment link SMS prompt.",
        recommended_action=RecoveryActionType.SEND_PAYMENT_LINK.value,
        status=RecoveryCaseStatus.RECOVERED,
        recovered_amount=Decimal("1299.00"),
    )
    case4 = RecoveryCase(
        payment_id=payments[3].id,
        revenue_at_risk=Decimal("2499.00"),
        recoverability_score=0.62,
        diagnosis="3D Secure challenge failed; recommended switching to UPI or sending instant checkout link.",
        recommended_action=RecoveryActionType.CHANGE_PAYMENT_METHOD.value,
        status=RecoveryCaseStatus.OPEN,
        recovered_amount=Decimal("0.00"),
    )
    db.add_all([case1, case2, case3, case4])
    db.flush()

    # Recovery Actions
    actions = [
        RecoveryAction(
            recovery_case_id=case1.id,
            action_type=RecoveryActionType.RETRY_LATER,
            reason="Scheduled retry after payroll date (1st of month).",
            status=ActionExecutionStatus.PENDING,
        ),
        RecoveryAction(
            recovery_case_id=case2.id,
            action_type=RecoveryActionType.RETRY_PAYMENT,
            reason="Triggered automated gateway secondary attempt after 15 minutes.",
            status=ActionExecutionStatus.EXECUTED,
            executed_at=now - timedelta(hours=1),
            result="Gateway retry returned pending status.",
        ),
        RecoveryAction(
            recovery_case_id=case3.id,
            action_type=RecoveryActionType.SEND_PAYMENT_LINK,
            reason="Sent smart Razorpay recovery link via WhatsApp and Email.",
            status=ActionExecutionStatus.EXECUTED,
            executed_at=now - timedelta(hours=3),
            result="Customer clicked link and completed transaction successfully.",
            recovered_amount=Decimal("1299.00"),
        ),
        RecoveryAction(
            recovery_case_id=case4.id,
            action_type=RecoveryActionType.CHANGE_PAYMENT_METHOD,
            reason="Requested customer switch to UPI Autopay.",
            status=ActionExecutionStatus.PENDING,
        ),
    ]
    db.add_all(actions)
    db.flush()

    # Audit Logs
    audit_logs = [
        AuditLog(
            recovery_case_id=case1.id,
            event_type="CASE_CREATED",
            description="Revenue at risk detected for payment pay_insuf_9001 (₹2,499.00).",
            actor="SYSTEM",
        ),
        AuditLog(
            recovery_case_id=case2.id,
            event_type="DIAGNOSIS_COMPLETED",
            description="Bank timeout diagnosed. Transience score: 0.74.",
            actor="AI_DIAGNOSTIC_AGENT",
        ),
        AuditLog(
            recovery_case_id=case3.id,
            event_type="REVENUE_RECOVERED",
            description="Successfully recovered ₹1,299.00 via payment link execution.",
            actor="RECOVERY_ENGINE",
            metadata_={"link_channel": "WhatsApp", "gateway_ref": "rzp_link_88712"},
        ),
    ]
    db.add_all(audit_logs)
    db.commit()
    logger.info("Successfully seeded prototype data.")

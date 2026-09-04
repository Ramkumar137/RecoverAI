import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    Customer,
    Merchant,
    Payment,
    Subscription,
    PaymentStatus,
    FailureReason,
    RecoveryCaseStatus,
)
from app.utils.logger import logger


MERCHANT_CATEGORIES = [
    ("Software Subscription", ["CloudStack SaaS", "DevMetrics Pro", "HostPulse Cloud", "CyberVault AI"]),
    ("E-Commerce", ["TrendBoutique", "OmniMart Retail", "Zenith Electronics", "UrbanFurnish"]),
    ("Education", ["SkillForge Academy", "CodeSprint Bootcamp", "LearnEdge Global", "TutorNet"]),
    ("Financial Services", ["WealthGrow Mutual", "FinServe Capital", "LedgerPay Tech", "MicroLoan Direct"]),
    ("Healthcare & Fitness", ["FitPulse Club", "MediCare Express", "NutriLife Health", "ZenYoga Digital"]),
]

CUSTOMER_PATTERNS = [
    "NORMAL_CUSTOMER",
    "FREQUENT_FAILURE_CUSTOMER",
    "HIGH_VALUE_CUSTOMER",
    "SUBSCRIPTION_CUSTOMER",
    "ABANDONED_CHECKOUT_CUSTOMER",
]


def seed_merchants(db: Session) -> List[Merchant]:
    """Ensures at least 20 merchants exist."""
    existing_merchants = {m.merchant_id: m for m in db.query(Merchant).all()}
    created_merchants = list(existing_merchants.values())

    counter = 1
    for category, names in MERCHANT_CATEGORIES:
        for name in names:
            m_id = f"merch_{category[:4].lower()}_{counter:03d}"
            if m_id not in existing_merchants:
                merchant = Merchant(
                    merchant_id=m_id,
                    name=name,
                    category=category,
                    average_payment_amount=Decimal(str(random.randint(1500, 15000))),
                )
                db.add(merchant)
                created_merchants.append(merchant)
            counter += 1

    db.flush()
    logger.info(f"Total merchants in database: {len(created_merchants)}")
    return created_merchants


def seed_customers(db: Session) -> List[Customer]:
    """Ensures at least 100 customers exist spanning the 5 personas."""
    existing_customers = {c.customer_id: c for c in db.query(Customer).all()}
    created_customers = list(existing_customers.values())

    first_names = ["Aarav", "Aditi", "Rohan", "Ananya", "Vikram", "Sneha", "Kabir", "Neha", "Arjun", "Pooja", "Rahul", "Priya", "Karan", "Divya", "Suresh", "Meera", "Varun", "Riya", "Nikhil", "Isha"]
    last_names = ["Sharma", "Verma", "Patel", "Iyer", "Reddy", "Gupta", "Nair", "Mehta", "Singh", "Joshi", "Bose", "Chopra", "Rao", "Mishra", "Deshmukh"]

    target_count = 110
    current_count = len(created_customers)

    for i in range(current_count + 1, target_count + 1):
        c_id = f"cust_synth_{i:04d}"
        if c_id in existing_customers:
            continue

        fn = random.choice(first_names)
        ln = random.choice(last_names)
        pattern = CUSTOMER_PATTERNS[(i - 1) % len(CUSTOMER_PATTERNS)]

        if pattern == "NORMAL_CUSTOMER":
            succ = random.randint(8, 20)
            fail = random.randint(0, 2)
            avg_amt = random.randint(1200, 4500)
            age_days = random.randint(60, 365)
        elif pattern == "FREQUENT_FAILURE_CUSTOMER":
            succ = random.randint(3, 8)
            fail = random.randint(5, 12)
            avg_amt = random.randint(800, 3000)
            age_days = random.randint(20, 150)
        elif pattern == "HIGH_VALUE_CUSTOMER":
            succ = random.randint(12, 35)
            fail = random.randint(1, 4)
            avg_amt = random.randint(15000, 75000)
            age_days = random.randint(180, 720)
        elif pattern == "SUBSCRIPTION_CUSTOMER":
            succ = random.randint(6, 24)
            fail = random.randint(0, 3)
            avg_amt = random.randint(2000, 8000)
            age_days = random.randint(90, 500)
        else:  # ABANDONED_CHECKOUT_CUSTOMER
            succ = random.randint(5, 15)
            fail = random.randint(1, 3)
            avg_amt = random.randint(1500, 6000)
            age_days = random.randint(30, 200)

        cust = Customer(
            customer_id=c_id,
            name=f"{fn} {ln}",
            email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
            account_age_days=age_days,
            total_payments=succ + fail,
            successful_payments=succ,
            failed_payments=fail,
            average_payment_amount=Decimal(str(avg_amt)),
        )
        db.add(cust)
        created_customers.append(cust)

    db.flush()
    logger.info(f"Total customers in database: {len(created_customers)}")
    return created_customers


def seed_demo_cases(db: Session, merchants: Optional[List[Merchant]] = None, reset: bool = False) -> None:
    """Creates or resets the 5 intentionally strong demo scenarios required by Phase 2 & Phase 4."""
    now = datetime.now(timezone.utc)
    if not merchants:
        merchants = db.query(Merchant).all()
    if not merchants:
        return
    m = merchants[0]

    demo_specs = [
        {
            "cid": "cust_demo_01_timeout",
            "name": "Amitabh Sen (Demo High Recoverability)",
            "email": "amitabh.demo@example.com",
            "succ": 15,
            "fail": 2,
            "pid": "pay_demo_01_bank_timeout",
            "amount": Decimal("8500.00"),
            "status": PaymentStatus.FAILED,
            "reason": FailureReason.BANK_TIMEOUT,
            "retries": 0,
            "method": "UPI",
        },
        {
            "cid": "cust_demo_02_insufficient",
            "name": "Sunita Rao (Demo Medium/High Link)",
            "email": "sunita.demo@example.com",
            "succ": 12,
            "fail": 1,
            "pid": "pay_demo_02_insufficient_funds",
            "amount": Decimal("4500.00"),
            "status": PaymentStatus.FAILED,
            "reason": FailureReason.INSUFFICIENT_FUNDS,
            "retries": 1,
            "method": "CARD",
        },
        {
            "cid": "cust_demo_03_carddeclined",
            "name": "Rajesh Khanna (Demo Low/Escalate)",
            "email": "rajesh.demo@example.com",
            "succ": 3,
            "fail": 6,
            "pid": "pay_demo_03_card_declined",
            "amount": Decimal("12000.00"),
            "status": PaymentStatus.FAILED,
            "reason": FailureReason.CARD_DECLINED,
            "retries": 2,
            "method": "CARD",
        },
        {
            "cid": "cust_demo_04_abandoned",
            "name": "Kavita Nair (Demo Abandoned Reminder)",
            "email": "kavita.demo@example.com",
            "succ": 9,
            "fail": 0,
            "pid": "pay_demo_04_checkout_abandoned",
            "amount": Decimal("2500.00"),
            "status": PaymentStatus.ABANDONED,
            "reason": None,
            "retries": 0,
            "method": "UPI",
        },
        {
            "cid": "cust_demo_05_maxretries",
            "name": "Dinesh Bhat (Demo Stop Recovery)",
            "email": "dinesh.demo@example.com",
            "succ": 2,
            "fail": 8,
            "pid": "pay_demo_05_max_retries_halted",
            "amount": Decimal("15000.00"),
            "status": PaymentStatus.FAILED,
            "reason": FailureReason.INSUFFICIENT_FUNDS,
            "retries": 3,
            "method": "NETBANKING",
        },
        {
            "cid": "cust_demo_pay_10482",
            "name": "Pooja Sharma (VIP Demo Case PAY_10482)",
            "email": "pooja.sharma@example.com",
            "succ": 18,
            "fail": 1,
            "pid": "PAY_10482",
            "amount": Decimal("8500.00"),
            "status": PaymentStatus.FAILED,
            "reason": FailureReason.BANK_TIMEOUT,
            "retries": 0,
            "method": "UPI",
        },
    ]

    for spec in demo_specs:
        cust = db.query(Customer).filter(Customer.customer_id == spec["cid"]).first()
        if not cust:
            cust = Customer(
                customer_id=spec["cid"],
                name=spec["name"],
                email=spec["email"],
                account_age_days=150,
                total_payments=spec["succ"] + spec["fail"],
                successful_payments=spec["succ"],
                failed_payments=spec["fail"],
                average_payment_amount=spec["amount"],
            )
            db.add(cust)
            db.flush()

        payment = db.query(Payment).filter(Payment.payment_id == spec["pid"]).first()
        if not payment:
            payment = Payment(
                payment_id=spec["pid"],
                customer_id=cust.id,
                merchant_id=m.id,
                amount=spec["amount"],
                currency="INR",
                payment_method=spec["method"],
                status=spec["status"],
                failure_reason=spec["reason"],
                retry_count=spec["retries"],
                created_at=now - timedelta(hours=random.randint(1, 24)),
            )
            db.add(payment)
        elif reset:
            payment.status = spec["status"]
            payment.failure_reason = spec["reason"]
            payment.retry_count = spec["retries"]
            payment.amount = spec["amount"]
            payment.payment_method = spec["method"]
            if payment.recovery_case:
                payment.recovery_case.status = RecoveryCaseStatus.OPEN
                payment.recovery_case.recovered_amount = Decimal("0.00")
                payment.recovery_case.final_action = None
                payment.recovery_case.policy_result = None
                payment.recovery_case.recovery_attempts = 0

    db.flush()
    logger.info("Successfully verified/seeded standard demo cases.")


def seed_payments_and_subscriptions(
    db: Session,
    merchants: List[Merchant],
    customers: List[Customer],
    target_payments: int = 550,
) -> None:
    """Generates 500+ realistic payment records across statuses, failure reasons, and timestamps."""
    existing_count = db.query(Payment).count()
    if existing_count >= target_payments:
        logger.info(f"Payment table already contains {existing_count} records. Safe to skip bulk payment generation.")
        return

    logger.info(f"Generating realistic payment records (target: {target_payments})...")
    now = datetime.now(timezone.utc)
    methods = ["UPI", "CARD", "NETBANKING", "WALLET"]

    # Generate subscriptions for ~30% of customers
    sub_count = 0
    for c in customers[:35]:
        s_id = f"sub_{c.customer_id}"
        if not db.query(Subscription).filter(Subscription.subscription_id == s_id).first():
            m = random.choice(merchants)
            sub = Subscription(
                subscription_id=s_id,
                customer_id=c.id,
                merchant_id=m.id,
                amount=Decimal(str(random.randint(999, 4999))),
                billing_cycle=random.choice(["MONTHLY", "ANNUALLY"]),
                status=random.choice(["ACTIVE", "ACTIVE", "PAST_DUE"]),
                next_payment_date=now + timedelta(days=random.randint(-5, 25)),
                retry_count=random.randint(0, 2),
            )
            db.add(sub)
            sub_count += 1
    db.flush()
    logger.info(f"Created {sub_count} subscriptions.")

    to_generate = target_payments - existing_count
    for i in range(1, to_generate + 1):
        p_id = f"pay_synth_{existing_count + i:05d}"
        c = random.choice(customers)
        m = random.choice(merchants)
        created_time = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))

        # Status distribution: 60% SUCCESS, 25% FAILED, 8% ABANDONED, 4% EXPIRED, 3% RECOVERED
        p_rand = random.random()
        if p_rand < 0.60:
            status = PaymentStatus.SUCCESS
            failure_reason = None
            retries = 0
        elif p_rand < 0.85:
            status = PaymentStatus.FAILED
            failure_reason = random.choice([
                FailureReason.BANK_TIMEOUT,
                FailureReason.NETWORK_ERROR,
                FailureReason.INSUFFICIENT_FUNDS,
                FailureReason.CARD_DECLINED,
                FailureReason.AUTHENTICATION_FAILED,
                FailureReason.LIMIT_EXCEEDED,
                FailureReason.UNKNOWN,
            ])
            retries = random.choice([0, 0, 1, 1, 2, 3])
        elif p_rand < 0.93:
            status = PaymentStatus.ABANDONED
            failure_reason = None
            retries = 0
        elif p_rand < 0.97:
            status = PaymentStatus.EXPIRED
            failure_reason = None
            retries = 0
        else:
            status = PaymentStatus.RECOVERED
            failure_reason = random.choice([FailureReason.BANK_TIMEOUT, FailureReason.INSUFFICIENT_FUNDS])
            retries = random.randint(1, 2)

        # Realistic payment amount
        if float(c.average_payment_amount) > 10000:
            amount = Decimal(str(random.randint(8000, 45000)))
        else:
            amount = Decimal(str(random.randint(499, 5999)))

        payment = Payment(
            payment_id=p_id,
            customer_id=c.id,
            merchant_id=m.id,
            amount=amount,
            currency="INR",
            payment_method=random.choice(methods),
            status=status,
            failure_reason=failure_reason,
            retry_count=retries,
            created_at=created_time,
        )
        db.add(payment)

    db.commit()
    logger.info(f"Bulk payment generation completed. Total payments: {db.query(Payment).count()}")


def run_seed():
    db = SessionLocal()
    try:
        logger.info("--- Starting RecoverAI Synthetic Data Generator ---")
        merchants = seed_merchants(db)
        customers = seed_customers(db)
        seed_demo_cases(db, merchants)
        seed_payments_and_subscriptions(db, merchants, customers, target_payments=550)
        db.commit()
        logger.info("--- Data Generator Completed Successfully ---")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during synthetic data generation: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()

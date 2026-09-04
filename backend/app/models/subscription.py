from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subscription_id = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    billing_cycle = Column(String(50), default="MONTHLY", nullable=False)  # MONTHLY, QUARTERLY, ANNUALLY
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)  # ACTIVE, PAST_DUE, CANCELLED, PAUSED
    next_payment_date = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    merchant = relationship("Merchant", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, subscription_id='{self.subscription_id}', status='{self.status}')>"

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import PaymentStatus, FailureReason
from app.schemas.customer import CustomerRead
from app.schemas.merchant import MerchantRead


class PaymentBase(BaseModel):
    payment_id: str
    customer_id: int
    merchant_id: int
    amount: Decimal
    currency: str = "INR"
    payment_method: str
    status: PaymentStatus = PaymentStatus.PENDING
    failure_reason: Optional[FailureReason] = None
    retry_count: int = 0


class PaymentCreate(PaymentBase):
    pass


class PaymentRead(PaymentBase):
    id: int
    customer: Optional[CustomerRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentDetail(PaymentRead):
    customer: Optional[CustomerRead] = None
    merchant: Optional[MerchantRead] = None

    model_config = ConfigDict(from_attributes=True)

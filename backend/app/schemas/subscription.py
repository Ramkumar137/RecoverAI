from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SubscriptionBase(BaseModel):
    subscription_id: str
    customer_id: int
    merchant_id: int
    amount: Decimal
    billing_cycle: str = "MONTHLY"
    status: str = "ACTIVE"
    next_payment_date: Optional[datetime] = None
    retry_count: int = 0


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionRead(SubscriptionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

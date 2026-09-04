from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    customer_id: str
    name: str
    email: str
    account_age_days: int = 0
    total_payments: int = 0
    successful_payments: int = 0
    failed_payments: int = 0
    average_payment_amount: Decimal = Decimal("0.00")


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class MerchantBase(BaseModel):
    merchant_id: str
    name: str
    category: str
    average_payment_amount: Decimal = Decimal("0.00")


class MerchantCreate(MerchantBase):
    pass


class MerchantRead(MerchantBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

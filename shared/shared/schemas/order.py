import uuid
from datetime import datetime
from decimal import Decimal
from shared.compat import StrEnum
from typing import Any

from pydantic import BaseModel


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    user_id: uuid.UUID
    plan_id: uuid.UUID


class OrderRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    status: OrderStatus
    amount: Decimal
    currency: str
    payment_url: str | None = None
    external_payment_id: str | None = None
    provider_payload: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

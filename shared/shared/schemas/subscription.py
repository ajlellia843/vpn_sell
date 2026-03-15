import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class SubscriptionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    order_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    status: SubscriptionStatus
    auto_provisioned: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionExtend(BaseModel):
    subscription_id: uuid.UUID
    days: int

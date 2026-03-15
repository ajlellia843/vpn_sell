import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    duration_days: int
    price: Decimal
    currency: str = "RUB"
    description: str | None = None
    traffic_limit_gb: int | None = None
    device_limit: int = 1
    is_active: bool = True


class PlanRead(BaseModel):
    id: uuid.UUID
    name: str
    duration_days: int
    price: Decimal
    currency: str
    description: str | None = None
    traffic_limit_gb: int | None = None
    device_limit: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PlanUpdate(BaseModel):
    name: str | None = None
    duration_days: int | None = None
    price: Decimal | None = None
    currency: str | None = None
    description: str | None = None
    traffic_limit_gb: int | None = None
    device_limit: int | None = None
    is_active: bool | None = None

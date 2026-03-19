import uuid
from datetime import datetime
from shared.compat import StrEnum

from pydantic import BaseModel


class ProvisionStatus(StrEnum):
    PENDING = "pending"
    PROVISIONED = "provisioned"
    FAILED = "failed"
    DISABLED = "disabled"


class VPNAccessRead(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID
    xui_client_id: str | None = None
    inbound_id: int | None = None
    connection_uri: str | None = None
    provision_status: ProvisionStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProvisionRequest(BaseModel):
    subscription_id: uuid.UUID
    user_id: uuid.UUID
    plan_duration_days: int
    traffic_limit_gb: int | None = None
    device_limit: int = 1


class ProvisionResponse(BaseModel):
    subscription_id: uuid.UUID
    provision_status: ProvisionStatus
    connection_uri: str | None = None

import uuid
from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    is_active: bool | None = None
    username: str | None = None
    first_name: str | None = None

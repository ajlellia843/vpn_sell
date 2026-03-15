import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class VPNAccessBinding(Base):
    __tablename__ = "vpn_access_bindings"
    __table_args__ = {"schema": "vpn"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True,
    )
    xui_client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inbound_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    connection_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    provision_status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True,
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

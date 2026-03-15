"""create vpn schema and vpn_access_bindings table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS vpn")
    op.create_table(
        "vpn_access_bindings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            unique=True,
        ),
        sa.Column("xui_client_id", sa.String(255), nullable=True),
        sa.Column("inbound_id", sa.Integer(), nullable=True),
        sa.Column("connection_uri", sa.Text(), nullable=True),
        sa.Column(
            "provision_status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="vpn",
    )
    op.create_index(
        "ix_vpn_access_bindings_subscription_id",
        "vpn_access_bindings",
        ["subscription_id"],
        schema="vpn",
    )
    op.create_index(
        "ix_vpn_access_bindings_provision_status",
        "vpn_access_bindings",
        ["provision_status"],
        schema="vpn",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vpn_access_bindings_provision_status",
        table_name="vpn_access_bindings",
        schema="vpn",
    )
    op.drop_index(
        "ix_vpn_access_bindings_subscription_id",
        table_name="vpn_access_bindings",
        schema="vpn",
    )
    op.drop_table("vpn_access_bindings", schema="vpn")
    op.execute("DROP SCHEMA IF EXISTS vpn CASCADE")

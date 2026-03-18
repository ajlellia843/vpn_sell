# Centralized provider: build X-UI adapter (real or stub) from settings.
# ProvisioningService receives adapter via app.state; it does not know if real or stub.

from app.adapters.base import AbstractVPNPanelAdapter
from app.adapters.stub_xui import StubXUIAdapter
from app.adapters.xui import XUIAdapter
from app.config import VPNServiceSettings


def provide_vpn_panel_adapter(settings: VPNServiceSettings) -> AbstractVPNPanelAdapter:
    if settings.use_stub_xui:
        return StubXUIAdapter(inbound_id=settings.xui_inbound_id)
    return XUIAdapter(
        base_url=settings.xui_base_url,
        username=settings.xui_username,
        password=settings.xui_password,
        inbound_id=settings.xui_inbound_id,
    )

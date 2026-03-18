from shared.config import BaseServiceSettings


class VPNServiceSettings(BaseServiceSettings):
    service_name: str = "vpn-service"
    xui_base_url: str
    xui_username: str
    xui_password: str
    xui_inbound_id: int = 1

    # Stub: use stub instead of real 3x-ui adapter (env: USE_STUB_XUI)
    use_stub_xui: bool = False

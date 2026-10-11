import pytest
from app.subsystems.auth.auth_service import AuthService
from app.subsystems.auth.jwt_manager import JwtManager
from app.subsystems.auth.session_store import SessionStore
from app.core.device_fingerprint import DeviceMetadata

@pytest.mark.asyncio
async def test_auth_register_and_login():
    device = DeviceMetadata(ip="192.168.1.100", user_agent="Mozilla/5.0 Test")
    
    # Register
    reg = await AuthService.register(
        email="testfan@syncroprime.io",
        username="TestFan99",
        password_plain="SecurePass123!",
        preferred_persona="GEN_Z",
        device_meta=device
    )
    assert reg.user["email"] == "testfan@syncroprime.io"
    assert reg.user["persona"] == "GEN_Z"
    assert reg.user["tokens"] == 250
    assert reg.access_token is not None

    # Verify Access Token
    decoded = JwtManager.verify_access_token(reg.access_token)
    assert decoded is not None
    assert decoded["userId"] == reg.user["id"]
    assert decoded["persona"] == "GEN_Z"

    # Login
    login_res = await AuthService.login(
        email="testfan@syncroprime.io",
        password_plain="SecurePass123!",
        device_meta=device
    )
    assert login_res.user["id"] == reg.user["id"]
    assert login_res.session_id is not None

    # Verify Redis Session Cache
    session = await SessionStore.get_session(login_res.session_id)
    assert session is not None
    assert session.user_id == reg.user["id"]
    assert session.subnet == "192.168.1.0/24"

@pytest.mark.asyncio
async def test_guest_mode():
    device = DeviceMetadata(ip="10.0.0.50", user_agent="MobileSafari Test")
    guest_res = await AuthService.guest_login(device_meta=device)
    assert guest_res.user["accountVerification"] == "GUEST"
    assert guest_res.user["tokens"] == 0
    assert guest_res.access_token is not None

    # Verify guest token decoding
    decoded = JwtManager.verify_access_token(guest_res.access_token)
    assert decoded is not None
    assert decoded["isGuest"] is True

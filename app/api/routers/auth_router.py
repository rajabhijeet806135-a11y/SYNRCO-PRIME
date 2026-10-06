from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from app.config import PersonaType
from app.core.device_fingerprint import DeviceMetadata
from app.subsystems.auth.auth_service import AuthService, AuthResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Security"])

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    preferred_persona: PersonaType = "CASUAL"
    device_metadata: Optional[DeviceMetadata] = None
    clan_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str
    device_metadata: Optional[DeviceMetadata] = None

class OAuthLoginRequest(BaseModel):
    provider: str  # 'google' | 'apple' | 'facebook'
    oauth_id: str
    email: str
    name: str
    device_metadata: Optional[DeviceMetadata] = None

class GuestLoginRequest(BaseModel):
    device_metadata: Optional[DeviceMetadata] = None

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    try:
        return await AuthService.register(
            email=req.email,
            username=req.username,
            password_plain=req.password,
            preferred_persona=req.preferred_persona,
            device_meta=req.device_metadata,
            clan_id=req.clan_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    try:
        return await AuthService.login(
            email=req.email,
            password_plain=req.password,
            device_meta=req.device_metadata
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/oauth", response_model=AuthResponse)
async def oauth_login(req: OAuthLoginRequest):
    try:
        return await AuthService.oauth_login(
            provider=req.provider,
            oauth_id=req.oauth_id,
            email=req.email,
            name=req.name,
            device_meta=req.device_metadata
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/guest", response_model=AuthResponse)
async def guest_login(req: GuestLoginRequest):
    return await AuthService.guest_login(device_meta=req.device_metadata)

@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "status": "authenticated",
        "user": current_user
    }

import jwt
import time
from typing import Optional, Dict, Any
from app.config import settings, PersonaType

class TokenPayload:
    def __init__(
        self,
        user_id: str,
        username: str,
        persona: PersonaType,
        account_verification: str,
        is_guest: bool,
        fingerprint_hash: str,
        clan_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.username = username
        self.persona = persona
        self.account_verification = account_verification
        self.is_guest = is_guest
        self.fingerprint_hash = fingerprint_hash
        self.clan_id = clan_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "username": self.username,
            "persona": self.persona,
            "accountVerification": self.account_verification,
            "isGuest": self.is_guest,
            "fingerprintHash": self.fingerprint_hash,
            "clanId": self.clan_id
        }

class JwtManager:
    @staticmethod
    def generate_access_token(payload: TokenPayload) -> str:
        data = payload.to_dict()
        data["exp"] = int(time.time()) + (settings.JWT_ACCESS_EXPIRY_MINUTES * 60)
        data["iat"] = int(time.time())
        return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def generate_refresh_token(user_id: str, fingerprint_hash: str) -> str:
        data = {
            "userId": user_id,
            "fingerprintHash": fingerprint_hash,
            "type": "refresh",
            "exp": int(time.time()) + (settings.JWT_REFRESH_EXPIRY_DAYS * 86400),
            "iat": int(time.time())
        }
        return jwt.encode(data, settings.JWT_REFRESH_SECRET, algorithm="HS256")

    @staticmethod
    def generate_guest_token(fingerprint_hash: str) -> Dict[str, str]:
        guest_id = f"guest_{hex(int(time.time()*1000) % 0xFFFFFFF)[2:]}"
        payload = TokenPayload(
            user_id=guest_id,
            username=f"Guest_{guest_id[6:]}",
            persona="CASUAL",
            account_verification="GUEST",
            is_guest=True,
            fingerprint_hash=fingerprint_hash
        )
        token = JwtManager.generate_access_token(payload)
        return {"token": token, "guest_id": guest_id}

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            decoded = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
            if decoded.get("type") != "refresh":
                return None
            return decoded
        except Exception:
            return None

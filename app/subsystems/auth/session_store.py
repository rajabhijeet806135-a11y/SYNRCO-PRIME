import aiosqlite
import json
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.config import settings, PersonaType
from app.core.redis_state import redis_client
from app.core.device_fingerprint import DeviceFingerprinter, DeviceMetadata

class CachedSession(BaseModel):
    session_id: str
    user_id: str
    username: str
    persona: PersonaType
    account_verification: str
    sybil_score: float
    fingerprint_hash: str
    subnet: str
    clan_id: Optional[str] = None
    created_at: int
    expires_at: int

class SessionStore:
    @staticmethod
    async def create_session(
        user_id: str,
        username: str,
        persona: PersonaType,
        verification: str,
        sybil_score: float,
        device_meta: DeviceMetadata,
        clan_id: Optional[str] = None
    ) -> CachedSession:
        session_id = f"sess_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
        fingerprint_hash = DeviceFingerprinter.generate_fingerprint(device_meta)
        subnet = DeviceFingerprinter.extract_subnet(device_meta.ip)
        now = int(time.time() * 1000)
        expires_at = now + (30 * 86400 * 1000)

        session_data = CachedSession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            persona=persona,
            account_verification=verification,
            sybil_score=sybil_score,
            fingerprint_hash=fingerprint_hash,
            subnet=subnet,
            clan_id=clan_id,
            created_at=now,
            expires_at=expires_at
        )

        dumped = session_data.model_dump() if hasattr(session_data, 'model_dump') else session_data.dict()

        # 1. Primary fast Redis session cache (0 DB hits per message)
        await redis_client.set(
            f"session:{session_id}",
            json.dumps(dumped),
            ex=30 * 86400
        )
        await redis_client.set(f"user:{user_id}:active_session", session_id, ex=30 * 86400)
        await redis_client.sadd(f"subnet:{subnet}:users", user_id)

        # 2. Async DB durability
        try:
            async with aiosqlite.connect(settings.DB_FILE) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO sessions (
                        id, user_id, device_fingerprint, ip_address, subnet, user_agent, created_at, expires_at, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    session_id,
                    user_id,
                    fingerprint_hash,
                    device_meta.ip or "127.0.0.1",
                    subnet,
                    device_meta.user_agent or "unknown",
                    now,
                    expires_at
                ))
                await db.commit()
        except Exception as e:
            print(f"[SessionStore] Error writing session to DB: {e}")

        return session_data

    @staticmethod
    async def get_session(session_id: str) -> Optional[CachedSession]:
        raw = await redis_client.get(f"session:{session_id}")
        if not raw:
            return None
        try:
            data = json.loads(raw)
            return CachedSession(**data)
        except Exception:
            return None

    @staticmethod
    async def update_session_persona(session_id: str, new_persona: PersonaType) -> bool:
        session = await SessionStore.get_session(session_id)
        if not session:
            return False
        session.persona = new_persona
        dumped = session.model_dump() if hasattr(session, 'model_dump') else session.dict()
        await redis_client.set(f"session:{session_id}", json.dumps(dumped), ex=30 * 86400)
        return True

    @staticmethod
    async def revoke_session(session_id: str) -> None:
        session = await SessionStore.get_session(session_id)
        if session:
            await redis_client.delete_async(f"session:{session_id}", f"user:{session.user_id}:active_session")

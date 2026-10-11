import aiosqlite
import bcrypt
import json
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings, PersonaType
from app.core.device_fingerprint import DeviceFingerprinter, DeviceMetadata
from app.subsystems.auth.jwt_manager import JwtManager, TokenPayload
from app.subsystems.auth.session_store import SessionStore

class AuthResponse(BaseModel):
    user: Dict[str, Any]
    access_token: str
    refresh_token: str
    session_id: str

class AuthService:
    @staticmethod
    async def register(
        email: str,
        username: str,
        password_plain: str,
        preferred_persona: PersonaType = "CASUAL",
        device_meta: Optional[DeviceMetadata] = None,
        clan_id: Optional[str] = None
    ) -> AuthResponse:
        meta = device_meta or DeviceMetadata()
        user_id = f"usr_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), salt).decode("utf-8")
        now = int(time.time() * 1000)

        initial_scores = {
            "casual": 1.0 if preferred_persona == "CASUAL" else 0.2,
            "genz": 1.0 if preferred_persona == "GEN_Z" else 0.2,
            "hardcore": 1.0 if preferred_persona == "HARDCORE" else 0.2,
            "club_member": 1.0 if preferred_persona == "CLUB_MEMBER" else 0.2,
            "stadium": 1.0 if preferred_persona == "STADIUM" else 0.0,
            "broadcaster": 1.0 if preferred_persona == "BROADCASTER" else 0.0,
        }

        async with aiosqlite.connect(settings.DB_FILE) as db:
            await db.execute("""
                INSERT INTO users (
                    id, email, username, password_hash, preferred_persona, persona_scores_json,
                    account_verification, sybil_trust_score, clan_id, xp_total, sync_tokens,
                    prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                email.lower(),
                username,
                password_hash,
                preferred_persona,
                json.dumps(initial_scores),
                "EMAIL_VERIFIED",
                0.95,
                clan_id,
                0,
                250,  # 250 starter $SYNC tokens
                0,
                1.0,
                "BRONZE_FAN",
                now,
                now
            ))
            await db.commit()

        session = await SessionStore.create_session(
            user_id=user_id,
            username=username,
            persona=preferred_persona,
            verification="EMAIL_VERIFIED",
            sybil_score=0.95,
            device_meta=meta,
            clan_id=clan_id
        )

        fingerprint_hash = DeviceFingerprinter.generate_fingerprint(meta)
        access_token = JwtManager.generate_access_token(
            TokenPayload(
                user_id=user_id,
                username=username,
                persona=preferred_persona,
                account_verification="EMAIL_VERIFIED",
                is_guest=False,
                fingerprint_hash=fingerprint_hash,
                clan_id=clan_id
            )
        )
        refresh_token = JwtManager.generate_refresh_token(user_id, fingerprint_hash)

        return AuthResponse(
            user={
                "id": user_id,
                "email": email.lower(),
                "username": username,
                "persona": preferred_persona,
                "accountVerification": "EMAIL_VERIFIED",
                "sybilScore": 0.95,
                "clanId": clan_id,
                "tokens": 250,
                "xp": 0,
                "streak": 0,
                "multiplier": 1.0,
                "tierBadge": "BRONZE_FAN"
            },
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.session_id
        )

    @staticmethod
    async def login(
        email: str,
        password_plain: str,
        device_meta: Optional[DeviceMetadata] = None
    ) -> AuthResponse:
        meta = device_meta or DeviceMetadata()
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
            row = await cursor.fetchone()

        if not row:
            raise ValueError("Invalid email or password")

        if row["password_hash"]:
            is_valid = bcrypt.checkpw(password_plain.encode("utf-8"), row["password_hash"].encode("utf-8"))
            if not is_valid:
                raise ValueError("Invalid email or password")

        session = await SessionStore.create_session(
            user_id=row["id"],
            username=row["username"],
            persona=row["preferred_persona"],
            verification=row["account_verification"],
            sybil_score=row["sybil_trust_score"],
            device_meta=meta,
            clan_id=row["clan_id"]
        )

        fingerprint_hash = DeviceFingerprinter.generate_fingerprint(meta)
        access_token = JwtManager.generate_access_token(
            TokenPayload(
                user_id=row["id"],
                username=row["username"],
                persona=row["preferred_persona"],
                account_verification=row["account_verification"],
                is_guest=row["account_verification"] == "GUEST",
                fingerprint_hash=fingerprint_hash,
                clan_id=row["clan_id"]
            )
        )
        refresh_token = JwtManager.generate_refresh_token(row["id"], fingerprint_hash)

        return AuthResponse(
            user={
                "id": row["id"],
                "email": row["email"],
                "username": row["username"],
                "persona": row["preferred_persona"],
                "accountVerification": row["account_verification"],
                "sybilScore": row["sybil_trust_score"],
                "clanId": row["clan_id"],
                "tokens": row["sync_tokens"],
                "xp": row["xp_total"],
                "streak": row["prediction_streak"],
                "multiplier": row["streak_multiplier"],
                "tierBadge": row["tier_badge"]
            },
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.session_id
        )

    @staticmethod
    async def oauth_login(
        provider: str,
        oauth_id: str,
        email: str,
        name: str,
        device_meta: Optional[DeviceMetadata] = None
    ) -> AuthResponse:
        meta = device_meta or DeviceMetadata()
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
            row = await cursor.fetchone()

            now = int(time.time() * 1000)
            if not row:
                user_id = f"usr_oauth_{provider}_{now}"
                await db.execute("""
                    INSERT INTO users (
                        id, email, username, preferred_persona, persona_scores_json,
                        account_verification, sybil_trust_score, xp_total, sync_tokens,
                        prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    email.lower(),
                    name,
                    "GEN_Z",
                    json.dumps({"casual": 0.3, "genz": 0.9, "hardcore": 0.3, "club_member": 0.4}),
                    "EMAIL_VERIFIED",
                    0.98,
                    0,
                    300,
                    0,
                    1.0,
                    "BRONZE_FAN",
                    now,
                    now
                ))
                await db.commit()
                cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = await cursor.fetchone()

        session = await SessionStore.create_session(
            user_id=row["id"],
            username=row["username"],
            persona=row["preferred_persona"],
            verification=row["account_verification"],
            sybil_score=row["sybil_trust_score"],
            device_meta=meta,
            clan_id=row["clan_id"]
        )

        fingerprint_hash = DeviceFingerprinter.generate_fingerprint(meta)
        access_token = JwtManager.generate_access_token(
            TokenPayload(
                user_id=row["id"],
                username=row["username"],
                persona=row["preferred_persona"],
                account_verification=row["account_verification"],
                is_guest=False,
                fingerprint_hash=fingerprint_hash,
                clan_id=row["clan_id"]
            )
        )
        refresh_token = JwtManager.generate_refresh_token(row["id"], fingerprint_hash)

        return AuthResponse(
            user={
                "id": row["id"],
                "email": row["email"],
                "username": row["username"],
                "persona": row["preferred_persona"],
                "accountVerification": row["account_verification"],
                "sybilScore": row["sybil_trust_score"],
                "clanId": row["clan_id"],
                "tokens": row["sync_tokens"],
                "xp": row["xp_total"],
                "streak": row["prediction_streak"],
                "multiplier": row["streak_multiplier"],
                "tierBadge": row["tier_badge"]
            },
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.session_id
        )

    @staticmethod
    async def guest_login(device_meta: Optional[DeviceMetadata] = None) -> AuthResponse:
        meta = device_meta or DeviceMetadata()
        fingerprint_hash = DeviceFingerprinter.generate_fingerprint(meta)
        guest_info = JwtManager.generate_guest_token(fingerprint_hash)
        guest_id = guest_info["guest_id"]
        username = f"Guest_{guest_id[6:]}"

        session = await SessionStore.create_session(
            user_id=guest_id,
            username=username,
            persona="CASUAL",
            verification="GUEST",
            sybil_score=0.65,
            device_meta=meta
        )

        refresh_token = JwtManager.generate_refresh_token(guest_id, fingerprint_hash)

        return AuthResponse(
            user={
                "id": guest_id,
                "email": f"{guest_id}@guest.syncroprime.io",
                "username": username,
                "persona": "CASUAL",
                "accountVerification": "GUEST",
                "sybilScore": 0.65,
                "tokens": 0,
                "xp": 0,
                "streak": 0,
                "multiplier": 1.0,
                "tierBadge": "BRONZE_FAN"
            },
            access_token=guest_info["token"],
            refresh_token=refresh_token,
            session_id=session.session_id
        )

import aiosqlite
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.config import settings
from app.core.events import event_bus, Topics

class ClanInfo(BaseModel):
    id: str
    name: str
    tag: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    member_count: int

class ClanChatMessage(BaseModel):
    id: str
    clan_id: str
    user_id: str
    username: str
    message: str
    timestamp_ms: int

class ClanService:
    @staticmethod
    async def list_clans() -> List[ClanInfo]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM clans ORDER BY total_points DESC")
            rows = await cursor.fetchall()
            return [
                ClanInfo(
                    id=r["id"],
                    name=r["name"],
                    tag=r["tag"],
                    description=r["description"],
                    avatar_url=r["avatar_url"],
                    total_points=r["total_points"],
                    member_count=r["member_count"]
                )
                for r in rows
            ]

    @staticmethod
    async def get_clan(clan_id: str) -> Optional[ClanInfo]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM clans WHERE id = ?", (clan_id,))
            r = await cursor.fetchone()
            if not r:
                return None
            return ClanInfo(
                id=r["id"],
                name=r["name"],
                tag=r["tag"],
                description=r["description"],
                avatar_url=r["avatar_url"],
                total_points=r["total_points"],
                member_count=r["member_count"]
            )

    @staticmethod
    async def send_clan_message(clan_id: str, user_id: str, username: str, message: str) -> ClanChatMessage:
        msg = ClanChatMessage(
            id=f"msg_{int(time.time()*1000)}",
            clan_id=clan_id,
            user_id=user_id,
            username=username,
            message=message,
            timestamp_ms=int(time.time() * 1000)
        )
        dumped = msg.model_dump() if hasattr(msg, 'model_dump') else msg.dict()
        await event_bus.publish(Topics.CLAN_MESSAGE, dumped, source="clan_service")
        return msg

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.core.redis_state import redis_client
from app.subsystems.cqrs.cqrs_engine import cqrs_state_engine

class BroadcasterConfig(BaseModel):
    match_id: str
    broadcaster_name: str
    overlay_theme: str = "DARK_MODERN"
    sponsored_moments_enabled: bool = True
    active_sponsors: List[str] = ["Nike", "HawkEye", "StateFarm"]
    sync_latency_offset_ms: int = 150

class SdkService:
    @staticmethod
    async def get_overlay_metadata(match_id: str) -> Dict[str, Any]:
        leaderboard = await cqrs_state_engine.get_match_leaderboard(match_id, limit=5)
        top_clans = await cqrs_state_engine.get_clan_leaderboard(match_id, limit=3)
        crowd_db_raw = await redis_client.get(f"crowd:{match_id}:decibels")
        crowd_db = float(crowd_db_raw) if crowd_db_raw else 92.5

        return {
            "matchId": match_id,
            "sdkVersion": "2.4.0-syncro-prime",
            "streamSyncTimestamp": int(redis_client._expirations.get(f"match:{match_id}:sync", 0)),
            "liveCrowdDecibels": crowd_db,
            "topViewers": leaderboard,
            "topClans": top_clans,
            "embedSnippet": f'<SyncroOverlay matchId="{match_id}" theme="dark" haptics="true" />'
        }

import time
import math
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.core.redis_state import redis_client
from app.core.events import event_bus, Topics

class CrowdDecibelSnapshot(BaseModel):
    match_id: str
    current_decibels: float  # 60.0 to 120.0 dB
    cheer_taps_last_10s: int
    is_hype_spike: bool
    haptic_intensity: float  # 0.0 to 1.0

class CrowdDecibelEngine:
    _instance: Optional['CrowdDecibelEngine'] = None

    def __init__(self):
        self._cheer_counts: Dict[str, int] = {}
        self._last_reset: float = time.time()

    @classmethod
    def get_instance(cls) -> 'CrowdDecibelEngine':
        if cls._instance is None:
            cls._instance = CrowdDecibelEngine()
        return cls._instance

    async def record_cheer(self, match_id: str, user_id: str, intensity: float = 1.0) -> CrowdDecibelSnapshot:
        self._cheer_counts[match_id] = self._cheer_counts.get(match_id, 0) + int(intensity)
        taps = self._cheer_counts[match_id]

        # Calculate decibels: baseline 75 dB, scales with log(taps) up to 118 dB
        calculated_db = round(min(120.0, 75.0 + (math.log(max(1, taps)) * 6.5)), 1)
        is_hype = calculated_db > 102.0
        haptic_intensity = round(min(1.0, (calculated_db - 70.0) / 50.0), 2)

        snapshot = CrowdDecibelSnapshot(
            match_id=match_id,
            current_decibels=calculated_db,
            cheer_taps_last_10s=taps,
            is_hype_spike=is_hype,
            haptic_intensity=haptic_intensity
        )

        await redis_client.set(f"crowd:{match_id}:decibels", str(calculated_db))

        dumped = snapshot.model_dump() if hasattr(snapshot, 'model_dump') else snapshot.dict()
        await event_bus.publish(Topics.CROWD_DECIBEL_UPDATE, dumped, source="crowd_decibel_engine")

        if is_hype:
            await event_bus.publish(
                Topics.HAPTIC_TRIGGER,
                {"matchId": match_id, "intensity": haptic_intensity, "decibels": calculated_db},
                source="crowd_decibel_engine"
            )

        return snapshot

    async def get_decibels(self, match_id: str) -> float:
        val = await redis_client.get(f"crowd:{match_id}:decibels")
        return float(val) if val else 84.5

crowd_decibel_engine = CrowdDecibelEngine.get_instance()

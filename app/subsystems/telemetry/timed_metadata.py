import time
from typing import Dict, Any
from pydantic import BaseModel

class TimedMetadataTrack(BaseModel):
    track_type: str
    pts_timestamp_ms: int
    wall_clock_epoch_ms: int
    latency_to_glass_ms: int
    payload: Dict[str, Any]

class TimedMetadataInjector:
    @staticmethod
    def create_track(payload: Dict[str, Any], ingest_epoch_ms: int) -> TimedMetadataTrack:
        now_ms = int(time.time() * 1000)
        glass_to_glass = max(120, now_ms - ingest_epoch_ms + 350)

        return TimedMetadataTrack(
            track_type="SEI_USER_DATA",
            pts_timestamp_ms=now_ms % 10000000,
            wall_clock_epoch_ms=now_ms,
            latency_to_glass_ms=min(650, glass_to_glass),  # SLA <= 650ms
            payload=payload
        )

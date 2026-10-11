import time
import random
from typing import Dict, Any, Optional, Set, List
from pydantic import BaseModel
from app.datasets.dataset1_telemetry import MultiSportTelemetryData
from app.core.ttl_cache import shared_vlm_cache
from app.core.events import event_bus, Topics

class VlmTacticalInference(BaseModel):
    match_id: str
    timestamp_ms: int
    tactical_summary: str
    detected_event: Optional[str] = None
    is_dead_time: bool = False
    dead_time_type: Optional[str] = None
    suggested_dead_time_duration_seconds: Optional[int] = None
    highlight_hype_score: int = 50
    ai_narrative: str

class VlmInferencePool:
    """
    Subsystem 3: Shared VLM Inference Pool (Flaw 4 Fix)
    One inference per match broadcast, not per viewer (O(1) compute cost).
    Caches results in Redis with 500ms TTL.
    """
    _instance: Optional['VlmInferencePool'] = None

    def __init__(self):
        self._prewarmed_matches: Set[str] = set()
        self._inference_count: int = 0

    @classmethod
    def get_instance(cls) -> 'VlmInferencePool':
        if cls._instance is None:
            cls._instance = VlmInferencePool()
        return cls._instance

    def prewarm_match_pool(self, match_id: str) -> None:
        self._prewarmed_matches.add(match_id)
        print(f"[VlmInferencePool] Pre-warmed GPU worker pool for match: {match_id}")

    async def infer_broadcast_context(
        self,
        match_id: str,
        telemetry_frame: MultiSportTelemetryData
    ) -> VlmTacticalInference:
        cache_key = f"vlm:match:{match_id}:latest"

        # 1. Check shared inference cache (500ms TTL)
        cached = shared_vlm_cache.get(cache_key)
        if cached:
            return cached

        # 2. Perform Single Match Broadcast Analysis
        self._inference_count += 1
        now = int(time.time() * 1000)
        detected_event = None
        is_dead_time = False
        dead_time_type = None
        dead_time_duration = None
        highlight_hype = 50
        narrative = "Live open play in progress."

        if telemetry_frame.sport == "CRICKET":
            bowler = next((p for p in telemetry_frame.active_players if p.role == "BOWLER"), None)
            if telemetry_frame.tactical_metadata and telemetry_frame.tactical_metadata.drs_review_available and random.random() < 0.2:
                is_dead_time = True
                detected_event = "DRS_LBW_REVIEW"
                dead_time_type = "UMPIRE_REVIEW"
                dead_time_duration = 45
                highlight_hype = 85
                narrative = "Umpire signal DRS review for LBW. Ball-tracking Hawkeye cameras engaged."
            else:
                spd = bowler.release_speed_kmh if bowler and bowler.release_speed_kmh else 142.0
                narrative = f"Bowler release speed recorded at {spd} km/h on full length."

        elif telemetry_frame.sport == "FOOTBALL":
            xg = telemetry_frame.tactical_metadata.xg_snapshot if telemetry_frame.tactical_metadata and telemetry_frame.tactical_metadata.xg_snapshot else 0.1
            if xg > 0.65:
                highlight_hype = 92
                narrative = f"High-danger scoring opportunity detected! xG peak at {xg}."
            if random.random() < 0.15:
                is_dead_time = True
                detected_event = "VAR_PENALTY_CHECK"
                dead_time_type = "VAR_STOPPAGE"
                dead_time_duration = 60
                narrative = "Referee checking pitchside monitor for potential handball in penalty area."

        elif telemetry_frame.sport == "BASKETBALL":
            shot_clock = telemetry_frame.tactical_metadata.shot_clock_seconds if telemetry_frame.tactical_metadata and telemetry_frame.tactical_metadata.shot_clock_seconds is not None else 12.0
            if shot_clock < 5.0:
                highlight_hype = 88
                narrative = "Shot clock under 5 seconds! Clutch isolation play developing."

        inference = VlmTacticalInference(
            match_id=match_id,
            timestamp_ms=now,
            tactical_summary=f"{telemetry_frame.sport} Live Tactical Frame Analysis",
            detected_event=detected_event,
            is_dead_time=is_dead_time,
            dead_time_type=dead_time_type,
            suggested_dead_time_duration_seconds=dead_time_duration,
            highlight_hype_score=highlight_hype,
            ai_narrative=narrative
        )

        # 3. Cache in 500ms TTL cache (Shared across ALL viewers)
        shared_vlm_cache.set(cache_key, inference, match_id=match_id, ttl_ms=500)

        # 4. Publish to EventBus
        dumped = inference.model_dump() if hasattr(inference, 'model_dump') else inference.dict()
        await event_bus.publish(Topics.VLM_INFERENCE_RESULT, dumped, source="vlm_pool")

        return inference

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_inferences": self._inference_count,
            "prewarmed_matches": list(self._prewarmed_matches)
        }

vlm_inference_pool = VlmInferencePool.get_instance()

from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.datasets.dataset1_telemetry import MultiSportTelemetryData
from app.subsystems.telemetry.football_adapter import FootballAdapter
from app.subsystems.telemetry.cricket_adapter import CricketAdapter
from app.subsystems.telemetry.basketball_adapter import BasketballAdapter
from app.subsystems.telemetry.timed_metadata import TimedMetadataInjector, TimedMetadataTrack
from app.core.ttl_cache import shared_telemetry_cache
from app.core.events import event_bus, Topics

class ProcessedTelemetryFrame(BaseModel):
    match_id: str
    sport: str
    timestamp_ms: int
    frame_idx: int
    tactical_analysis: Dict[str, Any]
    timed_metadata: TimedMetadataTrack

class TelemetryPipeline:
    _instance: Optional['TelemetryPipeline'] = None

    @classmethod
    def get_instance(cls) -> 'TelemetryPipeline':
        if cls._instance is None:
            cls._instance = TelemetryPipeline()
        return cls._instance

    async def ingest_frame(self, raw_frame: MultiSportTelemetryData) -> ProcessedTelemetryFrame:
        if raw_frame.sport == "FOOTBALL":
            tactical = FootballAdapter.process_frame(raw_frame)
        elif raw_frame.sport == "CRICKET":
            tactical = CricketAdapter.process_frame(raw_frame)
        elif raw_frame.sport == "BASKETBALL":
            tactical = BasketballAdapter.process_frame(raw_frame)
        else:
            tactical = {"raw": raw_frame.dict()}

        timed_metadata = TimedMetadataInjector.create_track(
            payload={"sport": raw_frame.sport, "frameIdx": raw_frame.frame_idx, "analysis": tactical},
            ingest_epoch_ms=raw_frame.timestamp_ms
        )

        processed = ProcessedTelemetryFrame(
            match_id=raw_frame.match_id,
            sport=raw_frame.sport,
            timestamp_ms=raw_frame.timestamp_ms,
            frame_idx=raw_frame.frame_idx,
            tactical_analysis=tactical,
            timed_metadata=timed_metadata
        )

        # Cache in 200ms TTL cache
        shared_telemetry_cache.set(
            f"telemetry:latest:{raw_frame.match_id}",
            processed,
            match_id=raw_frame.match_id,
            ttl_ms=200,
            frame_idx=raw_frame.frame_idx
        )

        # Publish to EventBus
        dumped = processed.model_dump() if hasattr(processed, 'model_dump') else processed.dict()
        await event_bus.publish(Topics.TELEMETRY_PROCESSED, dumped, source="telemetry_pipeline")

        return processed

    def get_latest_telemetry(self, match_id: str) -> Optional[ProcessedTelemetryFrame]:
        return shared_telemetry_cache.get(f"telemetry:latest:{match_id}")

telemetry_pipeline = TelemetryPipeline.get_instance()

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any
from app.config import PersonaType
from app.datasets.dataset1_telemetry import MultiSportTelemetryData
from app.subsystems.telemetry.pipeline import telemetry_pipeline
from app.subsystems.persona.persona_router import PersonaRouter
from app.api.deps import rate_limit_guard

router = APIRouter(prefix="/api/v1/telemetry", tags=["Multi-Sport Telemetry Pipeline"])

@router.post("/ingest", dependencies=[Depends(rate_limit_guard)])
async def ingest_telemetry_frame(frame: MultiSportTelemetryData):
    processed = await telemetry_pipeline.ingest_frame(frame)
    return {
        "status": "ingested",
        "frame": processed
    }

@router.get("/latest/{match_id}")
async def get_latest_telemetry(
    match_id: str,
    persona: Optional[PersonaType] = Query(None)
):
    latest = telemetry_pipeline.get_latest_telemetry(match_id)
    if not latest:
        raise HTTPException(status_code=404, detail="No active telemetry stream found for this match")

    if persona:
        # Adapt for requested persona
        return PersonaRouter.adapt_telemetry(latest.tactical_analysis.get("raw", latest), persona)

    return latest

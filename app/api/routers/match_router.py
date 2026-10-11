import aiosqlite
import json
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.config import settings
from app.subsystems.crowd.decibel_engine import crowd_decibel_engine, CrowdDecibelSnapshot
from app.subsystems.vlm.highlight_generator import highlight_generator, AiHighlightClip
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/matches", tags=["Matches, Highlights & Crowd Resonator"])

class CheerRequest(BaseModel):
    intensity: float = 1.0

@router.get("")
async def list_matches():
    async with aiosqlite.connect(settings.DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM matches ORDER BY start_time DESC")
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"],
                "sport": r["sport"],
                "title": r["title"],
                "homeTeam": r["home_team"],
                "awayTeam": r["away_team"],
                "status": r["status"],
                "startTime": r["start_time"],
                "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            }
            for r in rows
        ]

@router.get("/{match_id}/highlights", response_model=List[AiHighlightClip])
async def get_match_highlights(match_id: str):
    return highlight_generator.get_highlights(match_id)

@router.post("/{match_id}/cheer", response_model=CrowdDecibelSnapshot)
async def cheer_match(
    match_id: str,
    req: CheerRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await crowd_decibel_engine.record_cheer(
        match_id=match_id,
        user_id=current_user["userId"],
        intensity=req.intensity
    )

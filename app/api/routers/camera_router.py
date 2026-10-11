from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.config import PersonaType
from app.core.telemetry_db import telemetry_db

router = APIRouter(prefix="/api/v1/matches", tags=["Match Angles, Cameras & 3D Spatial Positions"])

class RecordFrameRequest(BaseModel):
    match_id: str
    frame_idx: int
    timestamp_ms: int
    ball: Dict[str, Any]
    players: List[Dict[str, Any]]

@router.get("/{match_id}/cameras")
async def get_match_cameras(
    match_id: str,
    angle_type: Optional[str] = Query(None, description="Filter by camera type (e.g. MAIN_BROADCAST, SKY_TACTICAL, PLAYER_POV, HAWKEYE_3D)"),
    persona: Optional[str] = Query(None, description="Filter by recommended persona")
):
    """
    Returns all camera perspectives and viewing angles for a match,
    including 3D positions (X, Y, Z), optical rotation angles (Pitch, Yaw, Roll),
    Field of View (FOV), and live stream URLs.
    """
    cameras = await telemetry_db.get_camera_angles(match_id, angle_type=angle_type, persona=persona)
    if not cameras:
        # Check if match exists
        matches = await telemetry_db.get_all_matches()
        if not any(m["id"] == match_id for m in matches):
            raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found")
    return {
        "matchId": match_id,
        "count": len(cameras),
        "cameras": cameras
    }

@router.get("/{match_id}/cameras/{camera_id}")
async def get_camera_details(match_id: str, camera_id: str):
    """Returns detailed calibration, angles, and stream configuration for a specific camera."""
    cam = await telemetry_db.get_camera_by_id(camera_id)
    if not cam or cam["matchId"] != match_id:
        raise HTTPException(status_code=404, detail=f"Camera '{camera_id}' not found for match '{match_id}'")
    return cam

@router.get("/{match_id}/positions")
async def get_match_positions(
    match_id: str,
    frame_idx: Optional[int] = Query(None, description="Optional frame index filter"),
    player_id: Optional[str] = Query(None, description="Optional player filter")
):
    """
    Returns frame-by-frame spatial positions of both ball and players,
    including heading angles, trajectory launch/impact angles, speed, and postures.
    """
    ball_frames = await telemetry_db.get_ball_telemetry_frames(match_id, frame_idx=frame_idx)
    players = await telemetry_db.get_player_positions(match_id, frame_idx=frame_idx, player_id=player_id)
    
    return {
        "matchId": match_id,
        "frameIdx": frame_idx,
        "ballTelemetry": ball_frames,
        "playerPositions": players
    }

@router.get("/{match_id}/hawkeye")
async def get_hawkeye_trajectory_angles(match_id: str):
    """
    Returns Hawkeye ball-tracking 3D trajectory frames, pitch impact angles
    (e.g. 3.2° pitch bounce), exit launch angles, and DRS projection.
    """
    ball_frames = await telemetry_db.get_ball_telemetry_frames(match_id)
    hawkeye_frames = [f for f in ball_frames if f.get("hawkeyePitchPoint") or f["angles"]["impactAngleDeg"] > 0]
    
    return {
        "matchId": match_id,
        "hawkeyeActive": True,
        "framesCount": len(hawkeye_frames),
        "trajectoryFrames": hawkeye_frames
    }

@router.get("/{match_id}/tactical-moments")
async def get_match_tactical_moments(match_id: str):
    """
    Returns high-impact match moments (DRS reviews, VAR penalty checks, buzzer beaters)
    linked directly to their primary camera angles and decisive angle metrics.
    """
    moments = await telemetry_db.get_tactical_moments(match_id)
    return {
        "matchId": match_id,
        "momentsCount": len(moments),
        "moments": moments
    }

@router.get("/{match_id}/presets")
async def get_match_camera_presets(
    match_id: str,
    persona: Optional[PersonaType] = Query(None, description="Persona preset profile")
):
    """Returns quick-switch camera perspective presets tailored for each persona."""
    presets = await telemetry_db.get_camera_presets(match_id, persona=persona)
    return {
        "matchId": match_id,
        "presets": presets
    }

@router.post("/telemetry/record-frame", tags=["Multi-Sport Telemetry Pipeline"])
async def record_telemetry_frame(req: RecordFrameRequest):
    """Ingests and records a new frame of 3D spatial positions and angles into the database."""
    res = await telemetry_db.record_telemetry_frame(
        match_id=req.match_id,
        frame_idx=req.frame_idx,
        timestamp_ms=req.timestamp_ms,
        ball=req.ball,
        players=req.players
    )
    return res

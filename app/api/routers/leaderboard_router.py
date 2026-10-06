from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any, Optional
from app.subsystems.cqrs.cqrs_engine import cqrs_state_engine
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/leaderboards", tags=["CQRS Leaderboards (Sub-5ms)"])

@router.get("/global/{match_id}")
async def get_global_leaderboard(
    match_id: str,
    limit: int = Query(50, ge=1, le=100)
):
    return await cqrs_state_engine.get_match_leaderboard(match_id, limit=limit)

@router.get("/clans/{match_id}")
async def get_clan_leaderboard(
    match_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    return await cqrs_state_engine.get_clan_leaderboard(match_id, limit=limit)

@router.get("/rank/{match_id}")
async def get_my_rank(
    match_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    rank_info = await cqrs_state_engine.get_user_rank(match_id, current_user["userId"])
    return rank_info or {"rank": None, "score": 0.0}

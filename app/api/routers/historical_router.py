from fastapi import APIRouter
from typing import Dict, Any
from app.datasets.dataset4_historical import (
    HISTORICAL_CRICKET_H2H,
    HISTORICAL_FOOTBALL_PENALTIES,
    HISTORICAL_BASKETBALL_CLUTCH
)

router = APIRouter(prefix="/api/v1/historical", tags=["Dataset 4: Historical Multi-Sport Analytics"])

@router.get("/cricket-h2h")
async def get_cricket_head_to_head():
    return HISTORICAL_CRICKET_H2H

@router.get("/football-penalties")
async def get_football_penalties():
    return HISTORICAL_FOOTBALL_PENALTIES

@router.get("/basketball-clutch")
async def get_basketball_clutch():
    return HISTORICAL_BASKETBALL_CLUTCH

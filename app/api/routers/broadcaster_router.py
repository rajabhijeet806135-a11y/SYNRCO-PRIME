from fastapi import APIRouter
from typing import Dict, Any, List
from app.subsystems.broadcaster.sdk_service import SdkService
from app.subsystems.broadcaster.sponsor_engine import SponsorEngine, SponsoredMoment

router = APIRouter(prefix="/api/v1/broadcaster", tags=["Broadcaster B2B SDK & Gamification"])

@router.get("/overlay/{match_id}")
async def get_overlay_metadata(match_id: str):
    return await SdkService.get_overlay_metadata(match_id)

@router.get("/sponsors", response_model=List[SponsoredMoment])
async def list_sponsored_campaigns():
    return SponsorEngine.list_campaigns()

@router.get("/sponsors/{campaign_key}", response_model=SponsoredMoment)
async def get_sponsor_campaign(campaign_key: str):
    return SponsorEngine.get_campaign(campaign_key)

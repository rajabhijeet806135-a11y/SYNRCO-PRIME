from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.subsystems.clans.clan_service import ClanService, ClanInfo, ClanChatMessage
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/clans", tags=["Fan Communities & Clan Lounges"])

class SendChatMessageRequest(BaseModel):
    message: str

@router.get("", response_model=List[ClanInfo])
async def list_clans():
    return await ClanService.list_clans()

@router.get("/{clan_id}", response_model=ClanInfo)
async def get_clan(clan_id: str):
    clan = await ClanService.get_clan(clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    return clan

@router.post("/{clan_id}/chat", response_model=ClanChatMessage)
async def send_clan_chat(
    clan_id: str,
    req: SendChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await ClanService.send_clan_message(
        clan_id=clan_id,
        user_id=current_user["userId"],
        username=current_user.get("username", "Fan"),
        message=req.message
    )

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.config import SportType
from app.api.deps import get_current_user, rate_limit_guard
from app.subsystems.settlement.prediction_manager import prediction_manager, PredictionModel
from app.subsystems.settlement.settlement_worker import settlement_worker, VoteSubmission
from app.subsystems.settlement.reward_ledger import RewardLedger

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions & Real-Time Settlement"])

class CreatePredictionRequest(BaseModel):
    match_id: str
    sport: SportType
    title: str
    question: str
    options: List[str]
    window_seconds: int = 30
    odds: Optional[Dict[str, float]] = None
    correct_option: Optional[str] = None

class SubmitVoteRequest(BaseModel):
    prediction_id: str
    selected_option: str
    stake_tokens: int = 50
    client_event_id: str
    reaction_speed_ms: Optional[int] = 2500

class SettlePredictionRequest(BaseModel):
    correct_option: str

@router.get("/active/{match_id}", response_model=List[PredictionModel])
async def get_active_predictions(match_id: str):
    return await prediction_manager.get_active_predictions(match_id)

@router.post("/create", response_model=PredictionModel)
async def create_prediction(
    req: CreatePredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await prediction_manager.create_prediction(
        match_id=req.match_id,
        sport=req.sport,
        title=req.title,
        question=req.question,
        options=req.options,
        window_seconds=req.window_seconds,
        odds=req.odds,
        correct_option=req.correct_option
    )

@router.post("/vote", dependencies=[Depends(rate_limit_guard)])
async def submit_vote(
    req: SubmitVoteRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    submission = VoteSubmission(
        user_id=current_user["userId"],
        prediction_id=req.prediction_id,
        selected_option=req.selected_option,
        stake_tokens=req.stake_tokens,
        client_event_id=req.client_event_id,
        sybil_score=1.0,
        clan_id=current_user.get("clanId"),
        reaction_speed_ms=req.reaction_speed_ms or 2500
    )
    result = await settlement_worker.submit_vote(submission)
    if not result.get("accepted"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Vote submission failed"))
    return result

@router.post("/settle/{prediction_id}")
async def settle_prediction(
    prediction_id: str,
    req: SettlePredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        result = await settlement_worker.settle_prediction(
            prediction_id=prediction_id,
            correct_option=req.correct_option
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/balance")
async def get_my_balance(current_user: Dict[str, Any] = Depends(get_current_user)):
    return await RewardLedger.get_user_balance(current_user["userId"])

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.config import PersonaType
from app.api.deps import get_current_user
from app.subsystems.persona.persona_engine import PersonaEngine, QuizAnswers
from app.subsystems.persona.behavioral_classifier import UserSessionTelemetry

router = APIRouter(prefix="/api/v1/persona", tags=["Persona Adaptation Engine"])

class OverridePersonaRequest(BaseModel):
    new_persona: PersonaType

@router.post("/quiz")
async def evaluate_quiz(answers: QuizAnswers):
    return PersonaEngine.process_onboarding_quiz(answers)

@router.post("/override")
async def override_persona(
    req: OverridePersonaRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    res = await PersonaEngine.manual_override_persona(
        user_id=current_user["userId"],
        new_persona=req.new_persona
    )
    return res

@router.post("/telemetry-update")
async def update_behavioral_telemetry(
    telemetry: UserSessionTelemetry,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    updated = await PersonaEngine.update_behavioral_persona(
        user_id=current_user["userId"],
        telemetry=telemetry
    )
    return {
        "status": "updated",
        "scores": updated
    }

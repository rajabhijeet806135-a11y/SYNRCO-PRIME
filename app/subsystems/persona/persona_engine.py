import aiosqlite
import json
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings, PersonaType
from app.datasets.dataset3_gamification import PersonaConfidenceScores
from app.subsystems.persona.behavioral_classifier import BehavioralClassifier, UserSessionTelemetry
from app.core.redis_state import redis_client
from app.subsystems.auth.session_store import SessionStore

class QuizAnswers(BaseModel):
    q1_viewing_style: str  # 'quick_highlights' | 'deep_stats' | 'social_clan' | 'relaxed_fun'
    q2_sports_knowledge: str  # 'beginner' | 'intermediate' | 'expert'
    q3_primary_device: str  # 'mobile' | 'smart_tv' | 'in_stadium'

class PersonaEngine:
    @staticmethod
    def process_onboarding_quiz(answers: QuizAnswers) -> Dict[str, Any]:
        casual = 0.2
        genz = 0.2
        hardcore = 0.2
        club = 0.2
        stadium = 0.0

        if answers.q1_viewing_style == "relaxed_fun":
            casual += 0.5
        elif answers.q1_viewing_style == "quick_highlights":
            genz += 0.5
        elif answers.q1_viewing_style == "deep_stats":
            hardcore += 0.5
        elif answers.q1_viewing_style == "social_clan":
            club += 0.5

        if answers.q2_sports_knowledge == "beginner":
            casual += 0.4
        elif answers.q2_sports_knowledge == "expert":
            hardcore += 0.4

        if answers.q3_primary_device == "mobile":
            genz += 0.2
        elif answers.q3_primary_device == "in_stadium":
            stadium = 0.9

        scores = PersonaConfidenceScores(
            casual=round(casual, 2),
            genz=round(genz, 2),
            hardcore=round(hardcore, 2),
            club_member=round(club, 2),
            stadium=round(stadium, 2)
        )

        best_persona: PersonaType = "CASUAL"
        if stadium > 0.8:
            best_persona = "STADIUM"
        else:
            options = [
                (scores.casual, "CASUAL"),
                (scores.genz, "GEN_Z"),
                (scores.hardcore, "HARDCORE"),
                (scores.club_member, "CLUB_MEMBER")
            ]
            options.sort(key=lambda x: x[0], reverse=True)
            best_persona = options[0][1]  # type: ignore

        return {
            "recommended_persona": best_persona,
            "confidence_scores": scores
        }

    @staticmethod
    async def update_behavioral_persona(user_id: str, telemetry: UserSessionTelemetry) -> PersonaConfidenceScores:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT persona_scores_json FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()

            current = (
                json.loads(row["persona_scores_json"])
                if row and row["persona_scores_json"]
                else {"casual": 0.5, "genz": 0.5, "hardcore": 0.2, "club_member": 0.2}
            )

            current_scores = PersonaConfidenceScores(**current)
            updated = BehavioralClassifier.classify(telemetry, current_scores)

            dumped = updated.model_dump() if hasattr(updated, 'model_dump') else updated.dict()
            await db.execute(
                "UPDATE users SET persona_scores_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(dumped), int(time.time() * 1000), user_id)
            )
            await db.commit()

        await redis_client.set(f"user:{user_id}:persona_scores", json.dumps(dumped), ex=3600)
        return updated

    @staticmethod
    async def manual_override_persona(
        user_id: str,
        new_persona: PersonaType,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            await db.execute(
                "UPDATE users SET preferred_persona = ?, updated_at = ? WHERE id = ?",
                (new_persona, int(time.time() * 1000), user_id)
            )
            await db.commit()

        if session_id:
            await SessionStore.update_session_persona(session_id, new_persona)

        active_sess = await redis_client.get(f"user:{user_id}:active_session")
        if active_sess:
            await SessionStore.update_session_persona(active_sess, new_persona)

        return {
            "success": True,
            "active_persona": new_persona
        }

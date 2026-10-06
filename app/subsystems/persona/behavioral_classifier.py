from typing import List
from pydantic import BaseModel
from app.datasets.dataset3_gamification import PersonaConfidenceScores

class UserSessionTelemetry(BaseModel):
    stat_overlay_opens: int = 0
    tactical_view_duration_seconds: int = 0
    prediction_reaction_speed_ms: List[int] = []
    chat_messages_sent: int = 0
    emotes_sent: int = 0
    clan_lounges_visited: int = 0
    plain_english_help_requested: int = 0
    in_stadium_5g_connected: bool = False
    total_interactions: int = 0

class BehavioralClassifier:
    """
    Subsystem 1 Layer 2: Behavioral Inference Engine
    Classifies user engagement patterns into persona confidence dimensions (0.0 to 1.0)
    """
    @staticmethod
    def classify(telemetry: UserSessionTelemetry, current_scores: PersonaConfidenceScores) -> PersonaConfidenceScores:
        casual = current_scores.casual
        genz = current_scores.genz
        hardcore = current_scores.hardcore
        club = current_scores.club_member
        stadium = current_scores.stadium or 0.0

        # 1. Hardcore signals: Deep stats view, long tactical camera dwell
        if telemetry.stat_overlay_opens > 5 or telemetry.tactical_view_duration_seconds > 60:
            hardcore = min(1.0, hardcore + 0.70)
            casual = max(0.0, casual - 0.30)
            genz = max(0.0, genz - 0.20)

        # 2. Gen-Z signals: Rapid reactions (<4s), high emote volume
        avg_speed = (
            sum(telemetry.prediction_reaction_speed_ms) / len(telemetry.prediction_reaction_speed_ms)
            if telemetry.prediction_reaction_speed_ms else 8000
        )
        if telemetry.emotes_sent > 3 or (200 < avg_speed < 4000):
            genz = min(1.0, genz + 0.30)

        # 3. Casual signals: Plain English requests, low stat overlay usage
        if telemetry.plain_english_help_requested > 2 or (telemetry.total_interactions < 5 and telemetry.stat_overlay_opens == 0):
            casual = min(1.0, casual + 0.25)
            hardcore = max(0.0, hardcore - 0.20)

        # 4. Clan member signals: Clan chat & lounge visits
        if telemetry.clan_lounges_visited > 0 or telemetry.chat_messages_sent > 4:
            club = min(1.0, club + 0.35)

        # 5. Stadium 5G signal
        if telemetry.in_stadium_5g_connected:
            stadium = 0.95

        # Normalization
        total = casual + genz + hardcore + club + (stadium if stadium > 0.5 else 0)
        if total > 0:
            casual = round(casual / total, 2)
            genz = round(genz / total, 2)
            hardcore = round(hardcore / total, 2)
            club = round(club / total, 2)
            if stadium > 0.5:
                stadium = round(stadium / total, 2)

        return PersonaConfidenceScores(
            casual=max(0.05, min(1.0, casual)),
            genz=max(0.05, min(1.0, genz)),
            hardcore=max(0.05, min(1.0, hardcore)),
            club_member=max(0.05, min(1.0, club)),
            stadium=stadium
        )

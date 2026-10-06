from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import PersonaType
from app.datasets.dataset2_events import ContextualEventData
from app.datasets.dataset1_telemetry import MultiSportTelemetryData

class PersonaAdaptedPayload(BaseModel):
    persona: PersonaType
    match_id: str
    ui_mode: str
    title: str
    content: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None

class PersonaRouter:
    @staticmethod
    def adapt_contextual_event(event: ContextualEventData, persona: PersonaType) -> PersonaAdaptedPayload:
        if persona == "CASUAL":
            return PersonaAdaptedPayload(
                persona="CASUAL",
                match_id=event.match_id,
                ui_mode="SIMPLIFIED_EXPLANATION",
                title="Easy AI Match Explainer",
                content={
                    "headline": event.prompts_generated.casual,
                    "subtext": event.contextual_narrative,
                    "actionType": "POLL",
                    "actionPayload": {
                        "question": event.prompts_generated.casual,
                        "options": ["Yes", "No"],
                    },
                    "gamificationHint": "Earn +25 Fan XP for voting!",
                }
            )

        elif persona == "GEN_Z":
            return PersonaAdaptedPayload(
                persona="GEN_Z",
                match_id=event.match_id,
                ui_mode="RAPID_MICRO_PREDICTION",
                title="15s Rapid Micro-Challenge 🔥",
                content={
                    "headline": event.prompts_generated.genz,
                    "subtext": f"Window closes in {event.estimated_dead_time_seconds}s!",
                    "actionType": "PREDICTION",
                    "actionPayload": {
                        "predictionId": f"pred_{event.event_id}",
                        "question": event.prompts_generated.genz,
                        "options": event.prediction_options or ["Option A", "Option B"],
                        "odds": event.odds or {"Option A": 2.0, "Option B": 2.0},
                        "windowSeconds": event.estimated_dead_time_seconds,
                    },
                    "gamificationHint": "Active 2.5x Streak Multiplier Enabled ⚡",
                }
            )

        elif persona == "HARDCORE":
            return PersonaAdaptedPayload(
                persona="HARDCORE",
                match_id=event.match_id,
                ui_mode="TACTICAL_DEEP_DIVE",
                title="Advanced Telemetry & Predictive Analytics",
                content={
                    "headline": event.prompts_generated.hardcore,
                    "subtext": f"Event Type: {event.event_type} | AI Confidence: 94.2%",
                    "actionType": "TELEMETRY_CARD",
                    "actionPayload": {
                        "predictionId": f"pred_{event.event_id}",
                        "question": event.prompts_generated.hardcore,
                        "options": event.prediction_options,
                        "odds": event.odds,
                    },
                }
            )

        elif persona == "CLUB_MEMBER":
            return PersonaAdaptedPayload(
                persona="CLUB_MEMBER",
                match_id=event.match_id,
                ui_mode="CLAN_WAR_CLASH",
                title="Clan Battle Arena ⚔️",
                content={
                    "headline": event.prompts_generated.club_member or "Clan Battle Alert!",
                    "subtext": "Every member vote contributes to your Clan Leaderboard rank!",
                    "actionType": "CLAN_BATTLE",
                    "actionPayload": {
                        "predictionId": f"pred_{event.event_id}",
                        "options": event.prediction_options,
                    },
                    "gamificationHint": "+100 Clan War Glory Points on win",
                }
            )

        elif persona == "STADIUM":
            return PersonaAdaptedPayload(
                persona="STADIUM",
                match_id=event.match_id,
                ui_mode="IN_STADIUM_5G_EXPERIENCE",
                title="In-Stadium 5G Live View",
                content={
                    "headline": event.prompts_generated.stadium or "Live Stadium Replay Available",
                    "subtext": "Synchronized with stadium audio system",
                    "actionType": "STADIUM_AR",
                    "actionPayload": {
                        "seatViewAngle": "CAMERA_POV_ENDZONE",
                        "stadiumDeliveryAvailable": True,
                    },
                }
            )

        else:  # BROADCASTER
            return PersonaAdaptedPayload(
                persona="BROADCASTER",
                match_id=event.match_id,
                ui_mode="BROADCAST_SDK_OVERLAY",
                title="Broadcaster Interactive Real Estate",
                content={
                    "headline": event.prompts_generated.broadcaster or "Official Matchday Poll",
                    "subtext": "Embeddable SDK layer for OTT stream",
                    "actionType": "BROADCAST_OVERLAY",
                    "actionPayload": {
                        "sponsorBrand": "HawkEye & Nike",
                        "interactiveCta": "Vote Now on Stream",
                    },
                }
            )

    @staticmethod
    def adapt_telemetry(telemetry: MultiSportTelemetryData, persona: PersonaType) -> Dict[str, Any]:
        dumped = telemetry.model_dump() if hasattr(telemetry, 'model_dump') else telemetry.dict()
        if persona == "HARDCORE":
            return dumped

        if persona == "GEN_Z":
            return {
                "matchId": telemetry.match_id,
                "sport": telemetry.sport,
                "ballSpeedKmh": telemetry.ball.speed_kmh,
                "hypeFactor": "HIGH_SPEED_ROCKET 🚀" if telemetry.ball.speed_kmh > 120 else "NORMAL",
                "activeTopPlayer": telemetry.active_players[0].name if telemetry.active_players else "Unknown",
            }

        return {
            "matchId": telemetry.match_id,
            "sport": telemetry.sport,
            "ballSpeedKmh": round(telemetry.ball.speed_kmh),
            "activePlayersSummary": [p.name or p.player_id for p in telemetry.active_players],
        }

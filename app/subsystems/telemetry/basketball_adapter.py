from typing import Dict, Any
from app.datasets.dataset1_telemetry import MultiSportTelemetryData

class BasketballAdapter:
    @staticmethod
    def process_frame(data: MultiSportTelemetryData) -> Dict[str, Any]:
        shot_clock = (
            data.tactical_metadata.shot_clock_seconds
            if data.tactical_metadata and data.tactical_metadata.shot_clock_seconds is not None
            else 14.0
        )
        shooter = next((p for p in data.active_players if p.role in ("GUARD", "FORWARD")), None)
        separation = shooter.defensive_separation_m if shooter and shooter.defensive_separation_m is not None else 2.5
        arc_prob = data.ball.shot_arc_probability or 0.55

        is_clutch = shot_clock < 5.0
        expected_points = round(arc_prob * (3.0 if separation > 2.0 else 2.0), 2)

        return {
            "matchId": data.match_id,
            "timestampMs": data.timestamp_ms,
            "shotClockSeconds": shot_clock,
            "shotArcProbability": arc_prob,
            "defensiveSeparationMeters": separation,
            "isClutchMoment": is_clutch,
            "expectedPointValue": expected_points
        }

from typing import Dict, Any
from app.datasets.dataset1_telemetry import MultiSportTelemetryData

class CricketAdapter:
    @staticmethod
    def process_frame(data: MultiSportTelemetryData) -> Dict[str, Any]:
        bowler = next((p for p in data.active_players if p.role == "BOWLER"), None)
        batsman = next((p for p in data.active_players if p.role == "BATSMAN"), None)

        release_speed = bowler.release_speed_kmh if bowler and bowler.release_speed_kmh else data.ball.speed_kmh or 140.0
        run_up = bowler.run_up_velocity_ms if bowler and bowler.run_up_velocity_ms else 7.2
        bat_speed = batsman.bat_speed_kmh if batsman and batsman.bat_speed_kmh else 115.0

        pitch_point = (
            {"x": data.ball.trajectory_pitch_point.x, "y": data.ball.trajectory_pitch_point.y}
            if data.ball.trajectory_pitch_point else {"x": 16.5, "y": 0.1}
        )

        is_hitting = abs(pitch_point["y"]) < 0.25
        x_wicket = 0.72 if is_hitting else 0.18

        return {
            "matchId": data.match_id,
            "timestampMs": data.timestamp_ms,
            "bowlerReleaseSpeedKmh": release_speed,
            "bowlerRunUpVelocityMs": run_up,
            "batsmanBatSpeedKmh": bat_speed,
            "pitchBouncePoint": pitch_point,
            "drsLbwAnalysis": {
                "pitching": "IN_LINE" if abs(pitch_point["y"]) < 0.2 else "OUTSIDE_OFF",
                "impact": "IN_LINE",
                "wickets": "HITTING" if is_hitting else "MISSING",
                "xWicketProbability": x_wicket
            },
            "projectedOverRuns": 6 if release_speed > 145.0 else 9
        }

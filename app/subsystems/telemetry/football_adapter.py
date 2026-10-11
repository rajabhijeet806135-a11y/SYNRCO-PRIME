import math
from typing import Dict, Any
from app.datasets.dataset1_telemetry import MultiSportTelemetryData

class FootballAdapter:
    @staticmethod
    def calculate_xg(ball_x: float, ball_y: float, defensive_separation: float) -> float:
        # Standard pitch 105m x 68m, goal center at (105, 34)
        dx = 105.0 - ball_x
        dy = abs(34.0 - ball_y)
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 35.0:
            return 0.02

        try:
            angle_rad = math.atan2(7.32 * dx, dx * dx + dy * dy - (7.32 / 2) ** 2)
        except Exception:
            angle_rad = 0.2

        base_prob = max(0.01, min(0.95, (abs(angle_rad) / math.pi) * (15.0 / max(1.0, distance))))
        defender_factor = min(1.2, max(0.5, defensive_separation / 2.0))
        return round(base_prob * defender_factor, 3)

    @staticmethod
    def process_frame(data: MultiSportTelemetryData) -> Dict[str, Any]:
        home_players = [
            (p.model_dump() if hasattr(p, 'model_dump') else p.dict())
            for p in data.active_players if p.team in ("MCI", "HOME")
        ]
        away_players = [
            (p.model_dump() if hasattr(p, 'model_dump') else p.dict())
            for p in data.active_players if p.team in ("RMA", "AWAY")
        ]

        defenders = [p for p in data.active_players if p.role == "DEFENDER"]
        avg_def_x = sum(p.x for p in defenders) / len(defenders) if defenders else 45.0

        max_speed = 0.0
        fastest_player = "none"
        for p in data.active_players:
            if p.speed_kmh > max_speed:
                max_speed = p.speed_kmh
                fastest_player = p.name or p.player_id

        striker = next((p for p in data.active_players if p.role == "STRIKER"), None)
        def_sep = striker.defensive_separation_m if striker and striker.defensive_separation_m is not None else 2.0
        calculated_xg = FootballAdapter.calculate_xg(data.ball.x, data.ball.y, def_sep)

        ball_dump = data.ball.model_dump() if hasattr(data.ball, 'model_dump') else data.ball.dict()

        return {
            "matchId": data.match_id,
            "timestampMs": data.timestamp_ms,
            "ball": ball_dump,
            "homeTeamPlayers": home_players,
            "awayTeamPlayers": away_players,
            "defensiveLineHeightMeters": round(avg_def_x, 1),
            "pressingIntensityIndex": round(max_speed / 30.0, 2),
            "calculatedExpectedGoalXG": calculated_xg,
            "fastestSprintPlayer": {
                "playerId": fastest_player,
                "speedKmh": max_speed
            }
        }

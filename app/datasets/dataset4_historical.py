from typing import Dict
from pydantic import BaseModel

class CricketHeadToHead(BaseModel):
    batsman_id: str
    bowler_id: str
    balls_faced: int
    runs_scored: int
    dismissals: int
    strike_rate: float
    dot_ball_percentage: float
    boundary_percentage: float
    average_exit_velocity_kmh: float

class FootballPenaltyAnalysis(BaseModel):
    striker_id: str
    goalkeeper_id: str
    total_penalties: int
    goals_scored: int
    conversion_rate: float
    preferred_target: str
    gk_dive_bias: str

class BasketballClutchStats(BaseModel):
    player_id: str
    clutch_possessions_last_2min: int
    field_goal_percentage: float
    three_point_percentage: float
    win_probability_added: float
    double_team_frequency: float

HISTORICAL_CRICKET_H2H: Dict[str, CricketHeadToHead] = {
    "ind_18_kohli_vs_aus_56_starc": CricketHeadToHead(
        batsman_id="ind_18_kohli",
        bowler_id="aus_56_starc",
        balls_faced=184,
        runs_scored=236,
        dismissals=4,
        strike_rate=128.26,
        dot_ball_percentage=42.4,
        boundary_percentage=16.3,
        average_exit_velocity_kmh=124.8
    )
}

HISTORICAL_FOOTBALL_PENALTIES: Dict[str, FootballPenaltyAnalysis] = {
    "mci_09_haaland_vs_rma_01_courtois": FootballPenaltyAnalysis(
        striker_id="mci_09_haaland",
        goalkeeper_id="rma_01_courtois",
        total_penalties=7,
        goals_scored=6,
        conversion_rate=0.857,
        preferred_target="BOTTOM_RIGHT",
        gk_dive_bias="RIGHT"
    )
}

HISTORICAL_BASKETBALL_CLUTCH: Dict[str, BasketballClutchStats] = {
    "lal_23_james": BasketballClutchStats(
        player_id="lal_23_james",
        clutch_possessions_last_2min=342,
        field_goal_percentage=48.6,
        three_point_percentage=36.4,
        win_probability_added=4.82,
        double_team_frequency=0.78
    )
}

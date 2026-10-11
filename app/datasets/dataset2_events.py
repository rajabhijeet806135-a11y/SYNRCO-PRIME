from typing import List, Optional, Dict
from pydantic import BaseModel
from app.config import SportType

class PersonaPrompts(BaseModel):
    casual: str
    genz: str
    hardcore: str
    club_member: Optional[str] = None
    stadium: Optional[str] = None
    broadcaster: Optional[str] = None

class ContextualEventData(BaseModel):
    event_id: str
    match_id: str
    sport: SportType
    event_type: str
    is_dead_time: bool
    estimated_dead_time_seconds: int
    contextual_narrative: str
    prompts_generated: PersonaPrompts
    prediction_options: Optional[List[str]] = None
    correct_option: Optional[str] = None
    odds: Optional[Dict[str, float]] = None
    timestamp_ms: int

SAMPLE_CONTEXTUAL_EVENTS: List[ContextualEventData] = [
    ContextualEventData(
        event_id="EVT_DRS_REVIEW_1830",
        match_id="IND_AUS_T20_2026",
        sport="CRICKET",
        event_type="DRS_LBW_REVIEW",
        is_dead_time=True,
        estimated_dead_time_seconds=45,
        contextual_narrative="Third umpire reviewing ball tracking for LBW appeal against Virat Kohli.",
        prompts_generated=PersonaPrompts(
            casual="Will the ball hit the stumps? (Yes / No)",
            genz="DRS Verdict: OUT or NOT OUT? 🔥 (100 $SYNC at stake)",
            hardcore="Predicted Impact: Line / Outside Off / Umpire's Call (xWicket: 0.72 | Hawkeye Pitch Angle: 3.2°)",
            club_member="Clan Battle: Back Kohli with 100 Clan War Points!",
            stadium="Stadium Big Screen: Look up for live Hawkeye replay!",
            broadcaster="Sponsored by HawkEye Tech: Vote on the official broadcast overlay!"
        ),
        prediction_options=["OUT", "NOT OUT", "UMPIRE'S CALL"],
        correct_option="NOT OUT",
        odds={"OUT": 2.1, "NOT OUT": 1.65, "UMPIRE'S CALL": 3.8},
        timestamp_ms=1775304001500
    ),
    ContextualEventData(
        event_id="EVT_VAR_PENALTY_4412",
        match_id="MCI_RMA_UCL_2026",
        sport="FOOTBALL",
        event_type="VAR_PENALTY_CHECK",
        is_dead_time=True,
        estimated_dead_time_seconds=60,
        contextual_narrative="Referee at the pitchside monitor reviewing possible handball in the penalty box.",
        prompts_generated=PersonaPrompts(
            casual="Did the ball illegally touch the arm? (Penalty / No Penalty)",
            genz="Haaland Penalty: SCORES or SAVED? ⚽⚡ (2.5x Odds)",
            hardcore="Penalty Conversion Probability: 0.79 xG | GK Dive Probability: Right (54%)",
            club_member="Cityzens Clan vs Madridistas NY Clan War Clash!",
            stadium="Seat Delivery: Claim 20% off matchday snacks during VAR break!",
            broadcaster="Nike Clutch Moment: Predict Haaland spot-kick velocity!"
        ),
        prediction_options=["PENALTY_GIVEN", "NO_PENALTY"],
        correct_option="PENALTY_GIVEN",
        odds={"PENALTY_GIVEN": 1.45, "NO_PENALTY": 2.8},
        timestamp_ms=1775304002800
    ),
    ContextualEventData(
        event_id="EVT_NBA_CLUTCH_TIMEOUT_991",
        match_id="LAL_GSW_NBA_2026",
        sport="BASKETBALL",
        event_type="BASKETBALL_TIMEOUT",
        is_dead_time=True,
        estimated_dead_time_seconds=75,
        contextual_narrative="Lakers call full timeout with 4.8 seconds on the game clock.",
        prompts_generated=PersonaPrompts(
            casual="Who takes the final shot for the win?",
            genz="Buzzer Beater: CLUTCH BUCKET or MISS? 🏀🔥 (3x Streak Multiplier)",
            hardcore="LeBron Clutch Shot Probability: 46.2% eFG | GSW Double Team Prob: 82%",
            club_member="Lakers Nation Clan: Mobilize cheer resonance now!",
            stadium="Haptic Phone Pulse: Feel the arena decibel crescendo!",
            broadcaster="State Farm Assist of the Game: Vote for Play of the Match"
        ),
        prediction_options=["LEBRON_3PT", "DAVIS_DUNK", "DEFENSIVE_STOP"],
        correct_option="LEBRON_3PT",
        odds={"LEBRON_3PT": 2.4, "DAVIS_DUNK": 3.1, "DEFENSIVE_STOP": 2.0},
        timestamp_ms=1775304004100
    )
]

from typing import Optional, Dict
from pydantic import BaseModel
from app.config import PersonaType

class PersonaConfidenceScores(BaseModel):
    casual: float
    genz: float
    hardcore: float
    club_member: float
    stadium: Optional[float] = 0.0
    broadcaster: Optional[float] = 0.0

class GamificationState(BaseModel):
    xp_total: int
    sync_tokens: int
    prediction_streak: int
    streak_multiplier: float
    tier_badge: str

class ActiveSessionMetadata(BaseModel):
    match_id: str
    client_platform: str
    stadium_location: Optional[str] = None
    offline_queue_depth: int = 0
    last_active_timestamp: int

class UserPersonaProfile(BaseModel):
    user_id: str
    username: str
    preferred_persona: PersonaType
    persona_confidence_scores: PersonaConfidenceScores
    account_verification: str
    sybil_trust_score: float
    clan_id: Optional[str] = None
    gamification_state: GamificationState
    active_session: Optional[ActiveSessionMetadata] = None

SAMPLE_USERS = [
    UserPersonaProfile(
        user_id="usr_genz_7721",
        username="NeonStriker99",
        preferred_persona="GEN_Z",
        persona_confidence_scores=PersonaConfidenceScores(
            casual=0.12,
            genz=0.81,
            hardcore=0.44,
            club_member=0.62
        ),
        account_verification="EMAIL_VERIFIED",
        sybil_trust_score=0.94,
        clan_id="clan_mumbai_indians_elite",
        gamification_state=GamificationState(
            xp_total=4850,
            sync_tokens=1280,
            prediction_streak=5,
            streak_multiplier=3.0,
            tier_badge="DIAMOND_ANALYST"
        ),
        active_session=ActiveSessionMetadata(
            match_id="IND_AUS_T20_2026",
            client_platform="MOBILE_PWA",
            stadium_location="SEC_114_ROW_G",
            offline_queue_depth=0,
            last_active_timestamp=1775304000000
        )
    ),
    UserPersonaProfile(
        user_id="usr_hardcore_104",
        username="TacticalMastermind",
        preferred_persona="HARDCORE",
        persona_confidence_scores=PersonaConfidenceScores(
            casual=0.05,
            genz=0.32,
            hardcore=0.96,
            club_member=0.55
        ),
        account_verification="PHONE_VERIFIED",
        sybil_trust_score=0.99,
        clan_id="clan_cityzens_global",
        gamification_state=GamificationState(
            xp_total=12400,
            sync_tokens=4350,
            prediction_streak=8,
            streak_multiplier=3.0,
            tier_badge="DIAMOND_ANALYST"
        )
    ),
    UserPersonaProfile(
        user_id="usr_casual_332",
        username="WeekendViewer",
        preferred_persona="CASUAL",
        persona_confidence_scores=PersonaConfidenceScores(
            casual=0.88,
            genz=0.2,
            hardcore=0.1,
            club_member=0.15
        ),
        account_verification="REGISTERED",
        sybil_trust_score=0.85,
        gamification_state=GamificationState(
            xp_total=620,
            sync_tokens=250,
            prediction_streak=2,
            streak_multiplier=1.0,
            tier_badge="BRONZE_FAN"
        )
    )
]

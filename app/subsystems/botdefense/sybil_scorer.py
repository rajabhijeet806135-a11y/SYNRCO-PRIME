import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.config import settings
from app.core.redis_state import redis_client
from app.core.events import event_bus, Topics

class SybilAssessment(BaseModel):
    user_id: str
    composite_trust_score: float  # 0.0 to 1.0
    action_allowed: bool
    reward_multiplier_allowed: float  # 1.0, 0.5, or 0.0
    requires_captcha: bool
    flags: List[str]

class SybilTrustScorer:
    """
    Subsystem 7: Sybil Trust Scoring & Anti-Bot Defense (Flaw 5 Fix)
    Evaluates S1, S2, S3, S4 heuristics on every submission
    """
    @staticmethod
    async def evaluate_submission(
        user_id: str,
        subnet: str,
        reaction_speed_ms: int,
        account_created_at_ms: int,
        is_verified: bool,
        device_fingerprint_known: bool = True
    ) -> SybilAssessment:
        flags: List[str] = []
        score = 1.0

        # S1: Device Fingerprint History
        if not device_fingerprint_known:
            score -= 0.15
            flags.append("UNKNOWN_DEVICE_FINGERPRINT")

        # S2: Interaction Velocity (<150ms reaction from prompt appearance)
        if reaction_speed_ms < settings.SYBIL_MIN_HUMAN_REACTION_MS:
            score -= 0.55
            flags.append("BOT_INTERACTION_VELOCITY_SUB_150MS")

        # S3: Account Age Gating (<24h accounts)
        account_age_hours = (time.time() * 1000 - account_created_at_ms) / 3600000.0
        if account_age_hours < settings.SYBIL_NEW_ACCOUNT_HOURS_GATE and not is_verified:
            score -= 0.30
            flags.append("NEW_UNVERIFIED_ACCOUNT_UNDER_24H")

        # S4: IP Subnet Clustering (>5 accounts on same /24 subnet)
        subnet_users = await redis_client.smembers(f"subnet:{subnet}:users")
        if len(subnet_users) > settings.SYBIL_MAX_ACCOUNTS_PER_SUBNET:
            score -= 0.35
            flags.append(f"SUBNET_CLUSTERING_EXCEEDED_{len(subnet_users)}_ACCOUNTS")

        composite_score = round(max(0.0, min(1.0, score)), 2)

        # Determine Enforcement Policy
        if composite_score >= settings.SYBIL_FULL_REWARD_THRESHOLD:
            assessment = SybilAssessment(
                user_id=user_id,
                composite_trust_score=composite_score,
                action_allowed=True,
                reward_multiplier_allowed=1.0,
                requires_captcha=False,
                flags=flags
            )
        elif composite_score >= settings.SYBIL_SHADOW_LIMIT_THRESHOLD:
            assessment = SybilAssessment(
                user_id=user_id,
                composite_trust_score=composite_score,
                action_allowed=True,
                reward_multiplier_allowed=0.5,
                requires_captcha=True,
                flags=flags
            )
        else:
            assessment = SybilAssessment(
                user_id=user_id,
                composite_trust_score=composite_score,
                action_allowed=False,
                reward_multiplier_allowed=0.0,
                requires_captcha=True,
                flags=flags
            )
            # Publish security alert
            await event_bus.publish(
                Topics.SYBIL_FLAGGED,
                {"userId": user_id, "score": composite_score, "flags": flags},
                source="sybil_scorer"
            )

        return assessment

sybil_scorer = SybilTrustScorer()

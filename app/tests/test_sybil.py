import pytest
import time
from app.subsystems.botdefense.sybil_scorer import sybil_scorer
from app.subsystems.botdefense.proof_of_watch import ProofOfWatch
from app.core.redis_state import redis_client

@pytest.mark.asyncio
async def test_sybil_scorer_heuristics():
    now_ms = int(time.time() * 1000)

    # 1. Normal human submission
    assessment_human = await sybil_scorer.evaluate_submission(
        user_id="human_user_1",
        subnet="192.168.1.0/24",
        reaction_speed_ms=2200,  # 2.2s human reaction
        account_created_at_ms=now_ms - (48 * 3600 * 1000),  # 48h old
        is_verified=True,
        device_fingerprint_known=True
    )
    assert assessment_human.composite_trust_score >= 0.75
    assert assessment_human.action_allowed is True
    assert assessment_human.reward_multiplier_allowed == 1.0
    assert assessment_human.requires_captcha is False

    # 2. Bot submission (<150ms reaction speed)
    assessment_bot = await sybil_scorer.evaluate_submission(
        user_id="bot_user_1",
        subnet="10.0.0.0/24",
        reaction_speed_ms=80,  # 80ms - Bot reaction!
        account_created_at_ms=now_ms - 1000,
        is_verified=False,
        device_fingerprint_known=False
    )
    assert assessment_bot.composite_trust_score < 0.40
    assert assessment_bot.action_allowed is False
    assert "BOT_INTERACTION_VELOCITY_SUB_150MS" in assessment_bot.flags

@pytest.mark.asyncio
async def test_proof_of_watch_challenge():
    challenge = await ProofOfWatch.generate_challenge("user_target_1")
    assert challenge.challenge_id is not None
    assert challenge.expected_response_token is not None

    # Correct response
    is_valid = await ProofOfWatch.verify_challenge(
        challenge.challenge_id,
        challenge.expected_response_token
    )
    assert is_valid is True

    # Replay must fail
    is_valid_replay = await ProofOfWatch.verify_challenge(
        challenge.challenge_id,
        challenge.expected_response_token
    )
    assert is_valid_replay is False

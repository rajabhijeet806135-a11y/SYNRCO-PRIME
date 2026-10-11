import pytest
import time
from app.subsystems.settlement.prediction_manager import prediction_manager
from app.subsystems.settlement.settlement_worker import settlement_worker, VoteSubmission
from app.subsystems.settlement.reward_ledger import RewardLedger
from app.core.redis_state import redis_client

@pytest.mark.asyncio
async def test_prediction_creation_vote_and_instant_settlement():
    # 1. Create Prediction Pool
    pred = await prediction_manager.create_prediction(
        match_id="IND_AUS_T20_2026",
        sport="CRICKET",
        title="Next Ball Outcome",
        question="Next ball: 4, 6, Wicket, or Dot?",
        options=["DOT", "FOUR", "SIX", "WICKET"],
        window_seconds=20,
        odds={"DOT": 1.5, "FOUR": 3.0, "SIX": 4.5, "WICKET": 5.0}
    )
    assert pred.id is not None
    assert pred.status == "OPEN"

    # 2. Submit User Vote
    vote_res = await settlement_worker.submit_vote(
        VoteSubmission(
            user_id="usr_genz_7721",
            prediction_id=pred.id,
            selected_option="SIX",
            stake_tokens=100,
            client_event_id=f"vote_evt_{int(time.time()*1000)}",
            sybil_score=0.95
        )
    )
    assert vote_res["accepted"] is True

    # 3. Settle Prediction with SIX as outcome
    start_t = time.time()
    settle_res = await settlement_worker.settle_prediction(
        prediction_id=pred.id,
        correct_option="SIX"
    )
    duration_ms = (time.time() - start_t) * 1000

    assert settle_res.winners_count == 1
    assert settle_res.total_tokens_distributed > 0
    assert duration_ms < 100.0  # Sub-100ms UX settlement SLA

    # 4. Idempotency test: duplicate settlement must throw error
    with pytest.raises(ValueError):
        await settlement_worker.settle_prediction(
            prediction_id=pred.id,
            correct_option="SIX"
        )

import pytest
import time
from app.subsystems.cqrs.ring_buffer import edge_ingest_ring_buffer
from app.subsystems.cqrs.cqrs_engine import cqrs_state_engine
from app.core.sentinel_pool import sentinel_pool

@pytest.mark.asyncio
async def test_cqrs_zset_leaderboard():
    match_id = "TEST_MATCH_001"
    
    # Record scores
    await cqrs_state_engine.record_points(match_id, "user_alpha", 500.0, clan_id="clan_mumbai_indians_elite")
    await cqrs_state_engine.record_points(match_id, "user_beta", 850.0, clan_id="clan_cityzens_global")
    await cqrs_state_engine.record_points(match_id, "user_gamma", 320.0)

    # Read leaderboard (Sub-5ms response)
    start_t = time.time()
    top_users = await cqrs_state_engine.get_match_leaderboard(match_id, limit=10)
    duration_ms = (time.time() - start_t) * 1000

    assert duration_ms < 50.0  # Well within SLA
    assert len(top_users) == 3
    assert top_users[0]["user_id"] == "user_beta"
    assert top_users[0]["score"] == 850.0

    # User Rank check
    rank_beta = await cqrs_state_engine.get_user_rank(match_id, "user_beta")
    assert rank_beta["rank"] == 1

    rank_alpha = await cqrs_state_engine.get_user_rank(match_id, "user_alpha")
    assert rank_alpha["rank"] == 2

def test_ring_buffer_token_bucket_ingest():
    res = edge_ingest_ring_buffer.push("test_user_ip", {"action": "vote", "option": "YES"})
    assert res["accepted"] is True
    assert res["queued"] is True

    items = edge_ingest_ring_buffer.drain(max_items=10)
    assert len(items) >= 1

@pytest.mark.asyncio
async def test_sentinel_ha_failover():
    primary_before = sentinel_pool.get_primary()
    assert primary_before.role == "PRIMARY"

    # Trigger failover
    failover_res = await sentinel_pool.trigger_failover(reason="Node simulated crash")
    assert failover_res["failover_duration_ms"] < 5000  # < 5s SLA target!
    assert failover_res["new_primary"] != failover_res["old_primary"]

    # Verify new primary promoted
    new_primary = sentinel_pool.get_primary()
    assert new_primary.role == "PRIMARY"
    assert new_primary.id == failover_res["new_primary"]

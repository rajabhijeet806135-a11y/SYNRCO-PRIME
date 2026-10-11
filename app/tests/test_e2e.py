import pytest
import time
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_end_to_end_user_journey(async_client: AsyncClient):
    # 1. Health Check
    res_health = await async_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    # 2. Register Fan
    email = f"fan_{int(time.time()*1000)}@syncroprime.io"
    res_reg = await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "username": "E2EFan2026",
        "password": "Password123!",
        "preferred_persona": "GEN_Z",
        "clan_id": "clan_cityzens_global"
    })
    assert res_reg.status_code == 200
    auth_data = res_reg.json()
    token = auth_data["access_token"]
    user_id = auth_data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Onboarding Quiz
    res_quiz = await async_client.post("/api/v1/persona/quiz", json={
        "q1_viewing_style": "deep_stats",
        "q2_sports_knowledge": "expert",
        "q3_primary_device": "mobile"
    })
    assert res_quiz.status_code == 200
    assert res_quiz.json()["recommended_persona"] == "HARDCORE"

    # 4. Manual Persona Switch
    res_switch = await async_client.post(
        "/api/v1/persona/override",
        json={"new_persona": "HARDCORE"},
        headers=headers
    )
    assert res_switch.status_code == 200
    assert res_switch.json()["active_persona"] == "HARDCORE"

    # 5. Check Live Matches
    res_matches = await async_client.get("/api/v1/matches")
    assert res_matches.status_code == 200
    matches = res_matches.json()
    assert len(matches) >= 1
    match_id = matches[0]["id"]

    # 6. Create & Vote on Micro-Prediction
    res_pred = await async_client.post(
        "/api/v1/predictions/create",
        json={
            "match_id": match_id,
            "sport": "FOOTBALL",
            "title": "VAR Penalty Outcome",
            "question": "Haaland spot-kick: SCORES or SAVED?",
            "options": ["SCORES", "SAVED"],
            "odds": {"SCORES": 1.45, "SAVED": 3.2}
        },
        headers=headers
    )
    assert res_pred.status_code == 200
    pred_id = res_pred.json()["id"]

    # Vote
    res_vote = await async_client.post(
        "/api/v1/predictions/vote",
        json={
            "prediction_id": pred_id,
            "selected_option": "SCORES",
            "stake_tokens": 100,
            "client_event_id": f"client_evt_{int(time.time()*1000)}"
        },
        headers=headers
    )
    assert res_vote.status_code == 200

    # 7. Settle Prediction
    res_settle = await async_client.post(
        f"/api/v1/predictions/settle/{pred_id}",
        json={"correct_option": "SCORES"},
        headers=headers
    )
    assert res_settle.status_code == 200
    assert res_settle.json()["winners_count"] == 1

    # 8. Check Match Leaderboard
    res_leaderboard = await async_client.get(f"/api/v1/leaderboards/global/{match_id}")
    assert res_leaderboard.status_code == 200
    leaderboard = res_leaderboard.json()
    assert len(leaderboard) >= 1
    assert any(entry["user_id"] == user_id for entry in leaderboard)

    # 9. Check Broadcaster Overlay Metadata
    res_overlay = await async_client.get(f"/api/v1/broadcaster/overlay/{match_id}")
    assert res_overlay.status_code == 200
    assert "embedSnippet" in res_overlay.json()

    # 10. Check Historical Head-to-Head
    res_h2h = await async_client.get("/api/v1/historical/cricket-h2h")
    assert res_h2h.status_code == 200

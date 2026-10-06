import pytest
from app.subsystems.crowd.decibel_engine import crowd_decibel_engine
from app.subsystems.clans.clan_service import ClanService

@pytest.mark.asyncio
async def test_crowd_decibel_engine():
    snapshot1 = await crowd_decibel_engine.record_cheer("MCI_RMA_UCL_2026", "user_1", intensity=2.0)
    assert snapshot1.current_decibels >= 75.0

    # Simulate intense crowd spike
    for _ in range(15):
        snapshot_hype = await crowd_decibel_engine.record_cheer("MCI_RMA_UCL_2026", "user_group", intensity=5.0)

    assert snapshot_hype.current_decibels > 90.0
    assert snapshot_hype.haptic_intensity > 0.3

@pytest.mark.asyncio
async def test_clan_lounges():
    clans = await ClanService.list_clans()
    assert len(clans) >= 4

    # Send clan message
    msg = await ClanService.send_clan_message(
        clan_id="clan_mumbai_indians_elite",
        user_id="usr_genz_7721",
        username="NeonStriker99",
        message="Let's go Mumbai Paltan! Boost the decibel meter!"
    )
    assert msg.clan_id == "clan_mumbai_indians_elite"
    assert msg.message == "Let's go Mumbai Paltan! Boost the decibel meter!"

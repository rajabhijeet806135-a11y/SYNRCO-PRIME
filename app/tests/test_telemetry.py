import pytest
from app.datasets.dataset1_telemetry import (
    SAMPLE_FOOTBALL_TELEMETRY,
    SAMPLE_CRICKET_TELEMETRY,
    SAMPLE_BASKETBALL_TELEMETRY
)
from app.subsystems.telemetry.football_adapter import FootballAdapter
from app.subsystems.telemetry.cricket_adapter import CricketAdapter
from app.subsystems.telemetry.basketball_adapter import BasketballAdapter
from app.subsystems.telemetry.pipeline import telemetry_pipeline

def test_football_adapter_xg():
    analysis = FootballAdapter.process_frame(SAMPLE_FOOTBALL_TELEMETRY)
    assert analysis["matchId"] == "MCI_RMA_UCL_2026"
    assert "calculatedExpectedGoalXG" in analysis
    assert analysis["calculatedExpectedGoalXG"] > 0.0
    assert analysis["defensiveLineHeightMeters"] > 0.0

def test_cricket_adapter_hawkeye_and_drs():
    analysis = CricketAdapter.process_frame(SAMPLE_CRICKET_TELEMETRY)
    assert analysis["matchId"] == "IND_AUS_T20_2026"
    assert analysis["bowlerReleaseSpeedKmh"] == 144.2
    assert "drsLbwAnalysis" in analysis
    assert analysis["drsLbwAnalysis"]["wickets"] in ("HITTING", "MISSING")

def test_basketball_adapter_shot_clock():
    analysis = BasketballAdapter.process_frame(SAMPLE_BASKETBALL_TELEMETRY)
    assert analysis["matchId"] == "LAL_GSW_NBA_2026"
    assert analysis["shotClockSeconds"] == 4.8
    assert analysis["isClutchMoment"] is True  # Under 5 seconds

@pytest.mark.asyncio
async def test_telemetry_pipeline_ingest():
    processed = await telemetry_pipeline.ingest_frame(SAMPLE_FOOTBALL_TELEMETRY)
    assert processed.match_id == "MCI_RMA_UCL_2026"
    assert processed.timed_metadata.latency_to_glass_ms <= 650  # Strict SLA Check <= 650ms

    latest = telemetry_pipeline.get_latest_telemetry("MCI_RMA_UCL_2026")
    assert latest is not None
    assert latest.match_id == "MCI_RMA_UCL_2026"

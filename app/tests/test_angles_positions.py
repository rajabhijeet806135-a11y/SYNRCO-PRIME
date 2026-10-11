import os
from app.core.telemetry_db import telemetry_db

# Graceful pytest mark decorator fallback
try:
    import pytest
    async_test = pytest.mark.asyncio
except ImportError:
    def async_test(fn):
        return fn

@async_test
async def test_get_all_matches():
    matches = await telemetry_db.get_all_matches()
    assert len(matches) >= 3
    sports = {m["sport"] for m in matches}
    assert "CRICKET" in sports
    assert "FOOTBALL" in sports
    assert "BASKETBALL" in sports

@async_test
async def test_get_camera_angles_multi_sport():
    cricket_cameras = await telemetry_db.get_camera_angles("IND_AUS_T20_2026")
    assert len(cricket_cameras) == 8
    
    # Check camera types
    types = {c["angleType"] for c in cricket_cameras}
    assert "MAIN_BROADCAST" in types
    assert "SKY_TACTICAL" in types
    assert "PLAYER_POV" in types
    assert "HAWKEYE_3D" in types
    assert "FAN_ENDZONE" in types

    # Check 3D coordinates and angle boundaries
    for cam in cricket_cameras:
        assert -90.0 <= cam["rotation"]["pitchDeg"] <= 90.0
        assert 0.0 <= cam["rotation"]["yawDeg"] <= 360.0
        assert cam["optics"]["fieldOfViewDeg"] > 0.0
        assert cam["stream"]["streamUrl"].startswith("http")

@async_test
async def test_hawkeye_drs_angles():
    frames = await telemetry_db.get_ball_telemetry_frames("IND_AUS_T20_2026", frame_idx=84210)
    assert len(frames) == 1
    drs_frame = frames[0]
    # Hawkeye 3.2° pitch angle specification
    assert abs(drs_frame["angles"]["impactAngleDeg"] - 3.2) < 0.01
    assert drs_frame["hawkeyePitchPoint"]["x"] == 6.8
    assert drs_frame["hawkeyePitchPoint"]["y"] == 0.2

@async_test
async def test_player_positions_and_orientations():
    players = await telemetry_db.get_player_positions("IND_AUS_T20_2026", frame_idx=84210)
    assert len(players) >= 2
    
    kohli = next((p for p in players if p["playerId"] == "ind_18_kohli"), None)
    assert kohli is not None
    assert kohli["role"] == "BATSMAN"
    assert kohli["angles"]["facingAngleDeg"] == 180.0
    assert kohli["postureState"] == "ON_STRIKE"

@async_test
async def test_tactical_moments_camera_linkage():
    moments = await telemetry_db.get_tactical_moments("IND_AUS_T20_2026")
    assert len(moments) >= 1
    lbw_moment = moments[0]
    assert lbw_moment["eventName"] == "DRS_LBW_REVIEW_HAWKEYE"
    assert lbw_moment["primaryCameraId"] == "CAM_IND_AUS_HAWKEYE_DRS"
    assert lbw_moment["decisionOutcome"] == "OUT"

@async_test
async def test_record_telemetry_frame_write():
    res = await telemetry_db.record_telemetry_frame(
        match_id="IND_AUS_T20_2026",
        frame_idx=99999,
        timestamp_ms=1775304999999,
        ball={
            "x": 12.0, "y": 0.5, "z": 1.2,
            "speed_kmh": 142.5,
            "launch_angle_deg": 12.5,
            "impact_angle_deg": 2.8,
            "flight_phase": "IN_FLIGHT"
        },
        players=[
            {
                "player_id": "test_player_01",
                "player_name": "Test Athlete",
                "team": "IND",
                "role": "BATSMAN",
                "x": 10.0, "y": 0.0, "z": 0.0,
                "facing_angle_deg": 180.0,
                "movement_angle_deg": 180.0,
                "speed_kmh": 15.0,
                "posture_state": "ON_STRIKE"
            }
        ]
    )
    assert res["status"] == "persisted"
    assert res["frameIdx"] == 99999

    # Verify retrieval
    saved_ball = await telemetry_db.get_ball_telemetry_frames("IND_AUS_T20_2026", frame_idx=99999)
    assert len(saved_ball) == 1
    assert saved_ball[0]["angles"]["launchAngleDeg"] == 12.5

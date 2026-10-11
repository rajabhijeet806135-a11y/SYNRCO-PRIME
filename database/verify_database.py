#!/usr/bin/env python3
"""
SYNCRO PRIME: Match Angles, Camera Perspectives & Positions Verification Suite
Runs automated integrity tests against matches_telemetry.db
"""

import os
import sys
import sqlite3
import json

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "matches_telemetry.db")

def test_database_integrity():
    print("[TEST 1/7] Testing SQLite File Existence & Connection...")
    assert os.path.exists(DB_PATH), f"Database file missing: {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    print("  -> PASSED: Database connected successfully.")

    print("\n[TEST 2/7] Testing Foreign Key Integrity & WAL Mode...")
    cur = conn.cursor()
    fk_errors = cur.execute("PRAGMA foreign_key_check;").fetchall()
    assert len(fk_errors) == 0, f"Foreign key constraint violations: {fk_errors}"
    journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
    print(f"  -> PASSED: 0 FK violations. Journal mode: {journal_mode}")

    print("\n[TEST 3/7] Testing Table Counts & Minimum Data Requirements...")
    expected_tables = {
        "matches": 3,
        "camera_angles": 24,
        "ball_telemetry_frames": 12,
        "player_positions": 11,
        "tactical_moments": 3,
        "camera_presets": 10
    }
    for table, min_count in expected_tables.items():
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count >= min_count, f"Table '{table}' has {count} records, expected at least {min_count}"
        print(f"  -> PASSED: '{table}' has {count} records (>= {min_count})")

    print("\n[TEST 4/7] Testing Camera Angles & Perspective Geometry...")
    cameras = cur.execute("SELECT id, camera_angle_type, pitch_deg, yaw_deg, roll_deg, field_of_view_deg FROM camera_angles").fetchall()
    for c in cameras:
        # Pitch: -90° (straight down) to +90° (straight up)
        assert -90.0 <= c["pitch_deg"] <= 90.0, f"Camera {c['id']} invalid pitch: {c['pitch_deg']}"
        # Yaw: 0° to 360°
        assert 0.0 <= c["yaw_deg"] <= 360.0, f"Camera {c['id']} invalid yaw: {c['yaw_deg']}"
        # Roll: -180° to 180°
        assert -180.0 <= c["roll_deg"] <= 180.0, f"Camera {c['id']} invalid roll: {c['roll_deg']}"
        # FOV: 10° to 180°
        assert 10.0 <= c["field_of_view_deg"] <= 180.0, f"Camera {c['id']} invalid FOV: {c['field_of_view_deg']}"
    print(f"  -> PASSED: All {len(cameras)} camera angles comply with 3D optical rotational boundaries.")

    print("\n[TEST 5/7] Testing Ball Trajectory Angles & Hawkeye Precision...")
    # Verify Hawkeye 3.2° pitch bounce frame
    drs_frame = cur.execute("""
        SELECT * FROM ball_telemetry_frames
        WHERE match_id = 'IND_AUS_T20_2026' AND frame_idx = 84210
    """).fetchone()
    assert drs_frame is not None, "DRS Hawkeye pitch frame missing"
    assert abs(drs_frame["impact_angle_deg"] - 3.2) < 0.01, f"Expected 3.2° impact angle, got {drs_frame['impact_angle_deg']}°"
    assert drs_frame["hawkeye_pitch_x"] == 6.8, "Hawkeye pitch point X mismatch"
    assert drs_frame["hawkeye_pitch_y"] == 0.2, "Hawkeye pitch point Y mismatch"

    # Verify Kohli 32.0° launch angle frame
    six_frame = cur.execute("""
        SELECT * FROM ball_telemetry_frames
        WHERE match_id = 'IND_AUS_T20_2026' AND frame_idx = 84225
    """).fetchone()
    assert six_frame is not None, "Kohli 98m six trajectory frame missing"
    assert abs(six_frame["launch_angle_deg"] - 32.0) < 0.01, f"Expected 32.0° launch angle, got {six_frame['launch_angle_deg']}°"
    assert six_frame["speed_kmh"] == 148.0, "Speed mismatch on six"

    # Verify Football 28.4° goalmouth angle & xG
    football_frame = cur.execute("""
        SELECT * FROM ball_telemetry_frames
        WHERE match_id = 'MCI_RMA_UCL_2026' AND frame_idx = 120440
    """).fetchone()
    assert football_frame is not None, "Haaland goal trajectory frame missing"
    assert abs(football_frame["impact_angle_deg"] - 28.4) < 0.01, "Goalmouth subtended angle mismatch"
    assert football_frame["xg_snapshot"] == 0.74, "xG mismatch"

    # Verify Basketball 48.5° arc launch angle & 44.8° entry
    nba_frame = cur.execute("""
        SELECT * FROM ball_telemetry_frames
        WHERE match_id = 'LAL_GSW_NBA_2026' AND frame_idx = 99395
    """).fetchone()
    assert nba_frame is not None, "NBA release frame missing"
    assert abs(nba_frame["launch_angle_deg"] - 48.5) < 0.01, "3PT launch angle mismatch"
    print("  -> PASSED: All sports trajectory angles (Hawkeye 3.2°, Launch 32.0°, Goal 28.4°, Arc 48.5°) verified.")

    print("\n[TEST 6/7] Testing Player Spatial Positions & Heading Angles...")
    players = cur.execute("SELECT id, player_name, facing_angle_deg, movement_angle_deg, speed_kmh, posture_state FROM player_positions").fetchall()
    for p in players:
        assert 0.0 <= p["facing_angle_deg"] <= 360.0, f"Player {p['player_name']} invalid heading: {p['facing_angle_deg']}"
        assert 0.0 <= p["movement_angle_deg"] <= 360.0, f"Player {p['player_name']} invalid movement angle: {p['movement_angle_deg']}"
        assert p["speed_kmh"] >= 0.0, f"Player {p['player_name']} negative speed"
        assert p["posture_state"] is not None
    print(f"  -> PASSED: All {len(players)} player coordinates and facing angles verified.")

    print("\n[TEST 7/7] Testing Tactical Moment Camera Linkage...")
    moments = cur.execute("SELECT id, event_name, primary_camera_id, critical_angle_metric, decision_outcome FROM tactical_moments").fetchall()
    for m in moments:
        # Ensure primary camera exists in camera_angles
        cam_check = cur.execute("SELECT COUNT(*) FROM camera_angles WHERE id = ?", (m["primary_camera_id"],)).fetchone()[0]
        assert cam_check == 1, f"Primary camera {m['primary_camera_id']} not found in camera_angles"
        print(f"  -> Moment: {m['event_name']} -> Camera: {m['primary_camera_id']} | Decision: {m['decision_outcome']}")
    print("  -> PASSED: Tactical moment camera bindings verified.")

    conn.close()
    print("\n" + "=" * 65)
    print("ALL 7 DATABASE VERIFICATION SUITES PASSED SUCCESSFULLY (100% PASS)")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    try:
        test_database_integrity()
    except AssertionError as e:
        print(f"\n[FAILED] Verification assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

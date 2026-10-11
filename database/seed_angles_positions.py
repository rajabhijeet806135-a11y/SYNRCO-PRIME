#!/usr/bin/env python3
"""
SYNCRO PRIME: Match Angles, Camera Perspectives & Spatial Positions Database Generator
Generates, seeds, and verifies the SQLite database (matches_telemetry.db)
along with SQL seed files and JSON fixtures.
"""

import os
import json
import sqlite3
import math
import time
from typing import Dict, Any, List

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "matches_telemetry.db")
SCHEMA_FILE = os.path.join(DB_DIR, "schema.sql")
FIXTURES_JSON = os.path.join(DB_DIR, "fixtures", "match_angles_positions.json")
SEED_SQL_FILE = os.path.join(DB_DIR, "seed_data.sql")

# Ensure fixtures directory exists
os.makedirs(os.path.join(DB_DIR, "fixtures"), exist_ok=True)

# ==============================================================================
# SEED DATA DEFINITIONS
# ==============================================================================

MATCHES_DATA = [
    {
        "id": "IND_AUS_T20_2026",
        "sport": "CRICKET",
        "title": "India vs Australia - 3rd T20 International",
        "home_team": "India (IND)",
        "away_team": "Australia (AUS)",
        "venue": "Melbourne Cricket Ground (MCG), Melbourne",
        "dimensions_length_m": 171.0,
        "dimensions_width_m": 148.0,
        "dimensions_height_m": 45.0,
        "status": "LIVE",
        "start_time": 1775304000000,
        "metadata_json": json.dumps({
            "competition": "ICC T20 World Super Series 2026",
            "pitch_type": "Hard Bounce Drop-in Pitch (22 yards = 20.12m)",
            "weather": "21°C Clear Night, Wind 8 km/h NW",
            "stadium_capacity": 100024,
            "drs_reviews_remaining": {"IND": 2, "AUS": 1}
        })
    },
    {
        "id": "MCI_RMA_UCL_2026",
        "sport": "FOOTBALL",
        "title": "Manchester City vs Real Madrid - UCL Semi-Final",
        "home_team": "Manchester City (MCI)",
        "away_team": "Real Madrid (RMA)",
        "venue": "Etihad Stadium, Manchester",
        "dimensions_length_m": 105.0,
        "dimensions_width_m": 68.0,
        "dimensions_height_m": 32.0,
        "status": "LIVE",
        "start_time": 1775304000000 + 3600000,
        "metadata_json": json.dumps({
            "competition": "UEFA Champions League Semi-Final Leg 2",
            "surface": "Hybrid Desso GrassMaster",
            "weather": "14°C Light Mist, Humidity 78%",
            "stadium_capacity": 53400,
            "var_system": "Semi-Automated Offside Optical (12 Cameras)"
        })
    },
    {
        "id": "LAL_GSW_NBA_2026",
        "sport": "BASKETBALL",
        "title": "Los Angeles Lakers vs Golden State Warriors - Game 7",
        "home_team": "Los Angeles Lakers (LAL)",
        "away_team": "Golden State Warriors (GSW)",
        "venue": "Crypto.com Arena, Los Angeles",
        "dimensions_length_m": 28.65,
        "dimensions_width_m": 15.24,
        "dimensions_height_m": 12.0,
        "status": "LIVE",
        "start_time": 1775304000000 + 7200000,
        "metadata_json": json.dumps({
            "competition": "NBA Western Conference Finals Game 7",
            "court_type": "High-Grade Hardwood Maple Court",
            "shot_clock_default": 24,
            "rim_height_m": 3.05,
            "arena_capacity": 19079
        })
    }
]

CAMERA_ANGLES_DATA = [
    # ---------------- CRICKET CAMERAS (IND vs AUS) ----------------
    {
        "id": "CAM_IND_AUS_MAIN",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "MAIN_BROADCAST",
        "label": "4K Ultra Broadcast",
        "icon": "🎥",
        "position_x": 0.0,
        "position_y": -72.0,
        "position_z": 24.5,
        "pitch_deg": -18.5,
        "yaw_deg": 90.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 44.0,
        "focal_length_mm": 85.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.1,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 0,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/main_4k.m3u8",
        "is_active": 1,
        "recommended_persona": "CASUAL",
        "description": "Standard high-angle gantry camera covering the full MCG oval and bowler-batsman dual axis."
    },
    {
        "id": "CAM_IND_AUS_SKY",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "SKY_TACTICAL",
        "label": "Sky Tactical 2D/3D Grid",
        "icon": "🛸",
        "position_x": 0.0,
        "position_y": 0.0,
        "position_z": 45.0,
        "pitch_deg": -90.0,
        "yaw_deg": 0.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 92.0,
        "focal_length_mm": 24.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 0.0,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 40,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/sky_tactical.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Overhead tactical spider-cam grid showing fielder ring placements, gaps, and running angles."
    },
    {
        "id": "CAM_IND_AUS_POV_KOHLI",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "PLAYER_POV",
        "label": "Kohli Helmet-Cam POV",
        "icon": "👤",
        "position_x": 10.06,  # Batsman crease on 20.12m pitch center
        "position_y": 0.0,
        "position_z": 1.74,
        "pitch_deg": -4.0,
        "yaw_deg": 180.0,     # Facing straight at the bowler down the pitch
        "roll_deg": 0.0,
        "field_of_view_deg": 115.0,
        "focal_length_mm": 18.0,
        "target_focal_x": -10.06,
        "target_focal_y": 0.0,
        "target_focal_z": 1.85,
        "resolution": "1920x1080",
        "frame_rate_fps": 120,
        "latency_offset_ms": 75,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/pov_kohli.m3u8",
        "is_active": 1,
        "recommended_persona": "GEN_Z",
        "description": "Ultra-immersive batsman helmet visor perspective facing 144 km/h express deliveries."
    },
    {
        "id": "CAM_IND_AUS_POV_STARC",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "PLAYER_POV",
        "label": "Starc Bowler Delivery Stride",
        "icon": "⚡",
        "position_x": -10.06, # Bowler crease
        "position_y": 0.15,
        "position_z": 2.18,
        "pitch_deg": -8.5,
        "yaw_deg": 0.0,       # Facing batsman down the pitch
        "roll_deg": 2.1,
        "field_of_view_deg": 96.0,
        "focal_length_mm": 28.0,
        "target_focal_x": 10.06,
        "target_focal_y": 0.0,
        "target_focal_z": 0.72,
        "resolution": "1920x1080",
        "frame_rate_fps": 120,
        "latency_offset_ms": 65,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/pov_starc.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Bowler delivery leap perspective capturing release point, seam rotation, and batsman trigger movements."
    },
    {
        "id": "CAM_IND_AUS_FAN_ENDZONE",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "FAN_ENDZONE",
        "label": "360° Great Southern Stand",
        "icon": "🏟️",
        "position_x": 0.0,
        "position_y": 76.5,
        "position_z": 12.0,
        "pitch_deg": -14.2,
        "yaw_deg": 270.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 130.0,
        "focal_length_mm": 16.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.0,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 30,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/fan_360.m3u8",
        "is_active": 1,
        "recommended_persona": "STADIUM",
        "description": "Full stadium immersion view from the historic Great Southern Stand with crowd decibel haptics."
    },
    {
        "id": "CAM_IND_AUS_HAWKEYE_DRS",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "HAWKEYE_3D",
        "label": "HawkEye DRS Ultra-SlowMo",
        "icon": "🎯",
        "position_x": 12.5,
        "position_y": -14.0,
        "position_z": 3.8,
        "pitch_deg": -12.4,
        "yaw_deg": 138.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 32.0,
        "focal_length_mm": 135.0,
        "target_focal_x": 6.8,  # Pitch impact bounce zone
        "target_focal_y": 0.2,
        "target_focal_z": 0.35,
        "resolution": "1920x1080",
        "frame_rate_fps": 500,
        "latency_offset_ms": 110,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/hawkeye_drs.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Calibrated 500fps sub-millimeter optical Hawkeye camera calculating pitch bounce angle and wicket projection."
    },
    {
        "id": "CAM_IND_AUS_REFEREE_UMPIRE",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "REFEREE_BODY_CAM",
        "label": "Bowler's End Umpire Cam",
        "icon": "⚖️",
        "position_x": -12.5,
        "position_y": 0.0,
        "position_z": 1.68,
        "pitch_deg": -1.8,
        "yaw_deg": 0.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 102.0,
        "focal_length_mm": 22.0,
        "target_focal_x": 10.06,
        "target_focal_y": 0.0,
        "target_focal_z": 0.75,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 50,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/umpire_cam.m3u8",
        "is_active": 1,
        "recommended_persona": "BROADCASTER",
        "description": "Standing umpire sight-line for judging LBW height, pitch alignment, and front-foot no-balls."
    },
    {
        "id": "CAM_IND_AUS_AERIAL_DRONE",
        "match_id": "IND_AUS_T20_2026",
        "camera_angle_type": "AERIAL_DRONE",
        "label": "MCG Orbital Drone Orbit",
        "icon": "🚁",
        "position_x": 48.0,
        "position_y": -42.0,
        "position_z": 32.0,
        "pitch_deg": -32.5,
        "yaw_deg": 140.0,
        "roll_deg": -3.5,
        "field_of_view_deg": 75.0,
        "focal_length_mm": 35.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.2,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 90,
        "stream_url": "https://stream.syncroprime.io/live/ind_aus/drone_orbit.m3u8",
        "is_active": 1,
        "recommended_persona": "CLUB_MEMBER",
        "description": "Continuous smooth orbiting 3D drone camera around the MCG stadium amphitheatre."
    },

    # ---------------- FOOTBALL CAMERAS (MCI vs RMA) ----------------
    {
        "id": "CAM_MCI_RMA_MAIN",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "MAIN_BROADCAST",
        "label": "Etihad Main Stand 4K",
        "icon": "🎥",
        "position_x": 0.0,
        "position_y": -42.0,
        "position_z": 18.5,
        "pitch_deg": -22.0,
        "yaw_deg": 90.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 52.0,
        "focal_length_mm": 70.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 0.5,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 0,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/main_4k.m3u8",
        "is_active": 1,
        "recommended_persona": "CASUAL",
        "description": "Colin Bell Stand primary gantry broadcast perspective covering all 105m of pitch."
    },
    {
        "id": "CAM_MCI_RMA_SKY",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "SKY_TACTICAL",
        "label": "Tactical 2D Pitch Matrix",
        "icon": "🛸",
        "position_x": 0.0,
        "position_y": 0.0,
        "position_z": 38.0,
        "pitch_deg": -90.0,
        "yaw_deg": 0.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 98.0,
        "focal_length_mm": 20.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 0.0,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 35,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/sky_tactical.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Tactical overhead pitch view detailing 3-2-4-1 pressing shape and defensive line depth."
    },
    {
        "id": "CAM_MCI_RMA_POV_HAALAND",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "PLAYER_POV",
        "label": "Haaland Striker Head-Cam",
        "icon": "👤",
        "position_x": 38.5,
        "position_y": 2.5,
        "position_z": 1.94,
        "pitch_deg": -3.5,
        "yaw_deg": 0.0,       # Facing Real Madrid goal
        "roll_deg": 0.0,
        "field_of_view_deg": 110.0,
        "focal_length_mm": 19.0,
        "target_focal_x": 52.5, # Goal line
        "target_focal_y": 0.0,
        "target_focal_z": 1.22,
        "resolution": "1920x1080",
        "frame_rate_fps": 120,
        "latency_offset_ms": 60,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/pov_haaland.m3u8",
        "is_active": 1,
        "recommended_persona": "GEN_Z",
        "description": "Erling Haaland striker perspective inside the 18-yard penalty box against Rüdiger."
    },
    {
        "id": "CAM_MCI_RMA_FAN_ENDZONE",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "FAN_ENDZONE",
        "label": "South Stand Curva Endzone",
        "icon": "🏟️",
        "position_x": -56.5,
        "position_y": 0.0,
        "position_z": 7.5,
        "pitch_deg": -10.5,
        "yaw_deg": 0.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 120.0,
        "focal_length_mm": 18.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.0,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 25,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/south_stand.m3u8",
        "is_active": 1,
        "recommended_persona": "CLUB_MEMBER",
        "description": "Ultra fan perspective right behind the goalmouth vibrating with Blue Moon chants."
    },
    {
        "id": "CAM_MCI_RMA_VAR_OFFSIDE",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "HAWKEYE_3D",
        "label": "VAR 18-Yard Offside Optical",
        "icon": "📐",
        "position_x": 36.0,
        "position_y": -36.0,
        "position_z": 6.5,
        "pitch_deg": -16.0,
        "yaw_deg": 90.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 38.0,
        "focal_length_mm": 105.0,
        "target_focal_x": 36.0,
        "target_focal_y": 0.0,
        "target_focal_z": 0.5,
        "resolution": "3840x2160",
        "frame_rate_fps": 240,
        "latency_offset_ms": 85,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/var_offside.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Strict calibrated optical plane camera used for millisecond semi-automated offside lines."
    },
    {
        "id": "CAM_MCI_RMA_REFEREE_BODY",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "REFEREE_BODY_CAM",
        "label": "UEFA Referee Chest Cam",
        "icon": "🦺",
        "position_x": 28.0,
        "position_y": -8.5,
        "position_z": 1.72,
        "pitch_deg": -2.0,
        "yaw_deg": 45.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 115.0,
        "focal_length_mm": 18.0,
        "target_focal_x": 38.0,
        "target_focal_y": 2.0,
        "target_focal_z": 1.2,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 55,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/referee_chest.m3u8",
        "is_active": 1,
        "recommended_persona": "BROADCASTER",
        "description": "Official on-field referee body camera capturing player dissent and penalty incidents."
    },
    {
        "id": "CAM_MCI_RMA_SIDELINE_PEP",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "SIDELINE_BENCH",
        "label": "Manager Tactical Dugout",
        "icon": "📋",
        "position_x": 0.0,
        "position_y": -35.0,
        "position_z": 2.2,
        "pitch_deg": -3.0,
        "yaw_deg": 90.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 65.0,
        "focal_length_mm": 50.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.0,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 40,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/dugout_pep.m3u8",
        "is_active": 1,
        "recommended_persona": "CASUAL",
        "description": "Sideline coaching box camera capturing tactical orders, gesticulations, and reactions."
    },
    {
        "id": "CAM_MCI_RMA_AERIAL_DRONE",
        "match_id": "MCI_RMA_UCL_2026",
        "camera_angle_type": "AERIAL_DRONE",
        "label": "Etihad Cable-Cam Aerial",
        "icon": "🛸",
        "position_x": 25.0,
        "position_y": -15.0,
        "position_z": 26.0,
        "pitch_deg": -42.0,
        "yaw_deg": 75.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 82.0,
        "focal_length_mm": 28.0,
        "target_focal_x": 38.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.0,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 70,
        "stream_url": "https://stream.syncroprime.io/live/mci_rma/cable_cam.m3u8",
        "is_active": 1,
        "recommended_persona": "STADIUM",
        "description": "High-velocity 4-point cable aerial camera diving through attacking transitions."
    },

    # ---------------- BASKETBALL CAMERAS (LAL vs GSW) ----------------
    {
        "id": "CAM_LAL_GSW_MAIN",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "MAIN_BROADCAST",
        "label": "Center Court 4K Broadcast",
        "icon": "🎥",
        "position_x": 0.0,
        "position_y": -12.5,
        "position_z": 6.8,
        "pitch_deg": -26.0,
        "yaw_deg": 90.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 56.0,
        "focal_length_mm": 60.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.2,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 0,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/main_4k.m3u8",
        "is_active": 1,
        "recommended_persona": "CASUAL",
        "description": "Center sideline camera covering both paint keys and the 3-point arcs."
    },
    {
        "id": "CAM_LAL_GSW_SKY",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "SKY_TACTICAL",
        "label": "Tactical Full Court 2D",
        "icon": "🛸",
        "position_x": 0.0,
        "position_y": 0.0,
        "position_z": 15.0,
        "pitch_deg": -90.0,
        "yaw_deg": 0.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 90.0,
        "focal_length_mm": 22.0,
        "target_focal_x": 0.0,
        "target_focal_y": 0.0,
        "target_focal_z": 0.0,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 25,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/sky_tactical.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Birds-eye court view displaying pick-and-roll switches and spacing geometry."
    },
    {
        "id": "CAM_LAL_GSW_POV_LEBRON",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "PLAYER_POV",
        "label": "LeBron James Headband POV",
        "icon": "👑",
        "position_x": 8.5,
        "position_y": 1.2,
        "position_z": 2.06,
        "pitch_deg": -4.0,
        "yaw_deg": 0.0,       # Facing basket
        "roll_deg": 0.0,
        "field_of_view_deg": 120.0,
        "focal_length_mm": 17.0,
        "target_focal_x": 13.75, # Basket hoop
        "target_focal_y": 0.0,
        "target_focal_z": 3.05,
        "resolution": "1920x1080",
        "frame_rate_fps": 120,
        "latency_offset_ms": 50,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/pov_lebron.m3u8",
        "is_active": 1,
        "recommended_persona": "GEN_Z",
        "description": "LeBron James headband optical view during downhill drives and clutch isolations."
    },
    {
        "id": "CAM_LAL_GSW_POV_CURRY",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "PLAYER_POV",
        "label": "Steph Curry Shooter Head-Cam",
        "icon": "🎯",
        "position_x": 6.8,
        "position_y": -6.2,   # 3-point corner/wing
        "position_z": 1.88,
        "pitch_deg": 12.0,    # Looking up toward hoop release
        "yaw_deg": 48.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 115.0,
        "focal_length_mm": 18.0,
        "target_focal_x": 13.75,
        "target_focal_y": 0.0,
        "target_focal_z": 3.05,
        "resolution": "1920x1080",
        "frame_rate_fps": 120,
        "latency_offset_ms": 45,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/pov_curry.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Stephen Curry rapid release POV capturing shooting wrist flexion and arc entry."
    },
    {
        "id": "CAM_LAL_GSW_UNDER_RIM",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "FAN_ENDZONE",
        "label": "Baseline Under-the-Rim 360°",
        "icon": "🏀",
        "position_x": 14.5,
        "position_y": 0.0,
        "position_z": 2.8,
        "pitch_deg": 18.0,
        "yaw_deg": 180.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 125.0,
        "focal_length_mm": 16.0,
        "target_focal_x": 13.75,
        "target_focal_y": 0.0,
        "target_focal_z": 3.05,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 20,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/under_rim.m3u8",
        "is_active": 1,
        "recommended_persona": "STADIUM",
        "description": "Under-the-rim baseline wide perspective for poster dunks and rim contests."
    },
    {
        "id": "CAM_LAL_GSW_BACKBOARD_SLOW",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "HAWKEYE_3D",
        "label": "High-Angle Glass Slow-Mo",
        "icon": "💎",
        "position_x": 13.9,
        "position_y": 0.0,
        "position_z": 4.2,
        "pitch_deg": -35.0,
        "yaw_deg": 180.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 45.0,
        "focal_length_mm": 90.0,
        "target_focal_x": 13.75,
        "target_focal_y": 0.0,
        "target_focal_z": 3.05,
        "resolution": "1920x1080",
        "frame_rate_fps": 300,
        "latency_offset_ms": 75,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/backboard_slow.m3u8",
        "is_active": 1,
        "recommended_persona": "HARDCORE",
        "description": "Ultra slow-motion 300fps backboard camera for goaltending and buzzer release verification."
    },
    {
        "id": "CAM_LAL_GSW_REFEREE_LEAD",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "REFEREE_BODY_CAM",
        "label": "Lead Referee Baseline Cam",
        "icon": "🦺",
        "position_x": 14.2,
        "position_y": -4.5,
        "position_z": 1.82,
        "pitch_deg": 5.0,
        "yaw_deg": 160.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 105.0,
        "focal_length_mm": 20.0,
        "target_focal_x": 11.5,
        "target_focal_y": 0.0,
        "target_focal_z": 2.0,
        "resolution": "1920x1080",
        "frame_rate_fps": 60,
        "latency_offset_ms": 40,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/referee_lead.m3u8",
        "is_active": 1,
        "recommended_persona": "BROADCASTER",
        "description": "Lead official perspective for charging fouls, restricted area blocks, and hand checks."
    },
    {
        "id": "CAM_LAL_GSW_FLOOR_CELEB",
        "match_id": "LAL_GSW_NBA_2026",
        "camera_angle_type": "SIDELINE_BENCH",
        "label": "Courtside VIP Floor Seat",
        "icon": "✨",
        "position_x": 2.0,
        "position_y": -8.0,
        "position_z": 0.95,
        "pitch_deg": 8.0,
        "yaw_deg": 75.0,
        "roll_deg": 0.0,
        "field_of_view_deg": 78.0,
        "focal_length_mm": 35.0,
        "target_focal_x": 5.0,
        "target_focal_y": 0.0,
        "target_focal_z": 1.8,
        "resolution": "3840x2160",
        "frame_rate_fps": 60,
        "latency_offset_ms": 30,
        "stream_url": "https://stream.syncroprime.io/live/lal_gsw/floor_vip.m3u8",
        "is_active": 1,
        "recommended_persona": "CLUB_MEMBER",
        "description": "Row 1 Courtside luxury perspective with court sneaker squeaks and player bench trash talk."
    }
]

BALL_TELEMETRY_DATA = [
    # ---------------- CRICKET BALL TRAJECTORY SEQUENCE (Starc -> Kohli DRS & Six) ----------------
    {
        "id": "BALL_IND_AUS_84200",
        "match_id": "IND_AUS_T20_2026",
        "timestamp_ms": 1775304001000,
        "frame_idx": 84200,
        "position_x": -9.8,
        "position_y": 0.15,
        "position_z": 2.15,
        "speed_kmh": 144.2,
        "spin_rpm": 2240.0,
        "spin_axis_angle_deg": 194.0,
        "launch_angle_deg": -6.8,       # Bowler release angled downward
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": -6.8,
        "azimuth_angle_deg": 0.4,
        "flight_phase": "RELEASE",
        "shot_arc_probability": 0.0,
        "xg_snapshot": None,
        "hawkeye_pitch_x": 6.8,
        "hawkeye_pitch_y": 0.2
    },
    {
        "id": "BALL_IND_AUS_84205",
        "match_id": "IND_AUS_T20_2026",
        "timestamp_ms": 1775304001100,
        "frame_idx": 84205,
        "position_x": -1.2,
        "position_y": 0.18,
        "position_z": 1.15,
        "speed_kmh": 140.5,
        "spin_rpm": 2210.0,
        "spin_axis_angle_deg": 192.5,
        "launch_angle_deg": -6.8,
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": -7.2,
        "azimuth_angle_deg": 0.5,
        "flight_phase": "IN_FLIGHT",
        "shot_arc_probability": 0.0,
        "xg_snapshot": None,
        "hawkeye_pitch_x": 6.8,
        "hawkeye_pitch_y": 0.2
    },
    {
        "id": "BALL_IND_AUS_84210",
        "match_id": "IND_AUS_T20_2026",
        "timestamp_ms": 1775304001200,
        "frame_idx": 84210,
        "position_x": 6.8,            # Pitch bounce point
        "position_y": 0.2,
        "position_z": 0.08,
        "speed_kmh": 134.8,
        "spin_rpm": 2150.0,
        "spin_axis_angle_deg": 188.0,
        "launch_angle_deg": -6.8,
        "impact_angle_deg": 3.2,       # Hawkeye 3.2° pitch angle!
        "elevation_angle_deg": 3.2,
        "azimuth_angle_deg": 0.9,      # Slight off-cutter deviation
        "flight_phase": "PITCH_BOUNCE",
        "shot_arc_probability": 0.12,
        "xg_snapshot": None,
        "hawkeye_pitch_x": 6.8,
        "hawkeye_pitch_y": 0.2
    },
    {
        "id": "BALL_IND_AUS_84215",
        "match_id": "IND_AUS_T20_2026",
        "timestamp_ms": 1775304001300,
        "frame_idx": 84215,
        "position_x": 9.8,            # Impact at batsman pad / bat crease
        "position_y": 0.12,
        "position_z": 0.42,
        "speed_kmh": 128.4,
        "spin_rpm": 2080.0,
        "spin_axis_angle_deg": 185.0,
        "launch_angle_deg": -6.8,
        "impact_angle_deg": 4.1,       # Trajectory impact angle hitting pad
        "elevation_angle_deg": 4.1,
        "azimuth_angle_deg": 1.1,      # Hawkeye projecting to hit leg stump
        "flight_phase": "BAT_IMPACT",
        "shot_arc_probability": 0.72,
        "xg_snapshot": None,
        "hawkeye_pitch_x": 6.8,
        "hawkeye_pitch_y": 0.2
    },
    {
        "id": "BALL_IND_AUS_84225",
        "match_id": "IND_AUS_T20_2026",
        "timestamp_ms": 1775304001500,
        "frame_idx": 84225,
        "position_x": 22.4,
        "position_y": -18.2,
        "position_z": 12.8,
        "speed_kmh": 148.0,           # Kohli 98m Six exit velocity!
        "spin_rpm": 1820.0,
        "spin_axis_angle_deg": 65.0,
        "launch_angle_deg": 32.0,      # Kohli 32° launch angle!
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": 28.5,
        "azimuth_angle_deg": 238.0,    # Pulled over deep mid-wicket
        "flight_phase": "ARC_PEAK",
        "shot_arc_probability": 0.96,
        "xg_snapshot": None,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },

    # ---------------- FOOTBALL BALL TRAJECTORY SEQUENCE (De Bruyne Cross -> Haaland Goal) ----------------
    {
        "id": "BALL_MCI_RMA_120420",
        "match_id": "MCI_RMA_UCL_2026",
        "timestamp_ms": 1775304002000,
        "frame_idx": 120420,
        "position_x": 28.5,           # De Bruyne cross delivery on right wing
        "position_y": 24.2,
        "position_z": 0.15,
        "speed_kmh": 84.5,
        "spin_rpm": 640.0,
        "spin_axis_angle_deg": 112.0,
        "launch_angle_deg": 24.5,      # Inswinging cross launch angle
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": 24.5,
        "azimuth_angle_deg": 332.0,
        "flight_phase": "RELEASE",
        "shot_arc_probability": 0.35,
        "xg_snapshot": 0.22,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },
    {
        "id": "BALL_MCI_RMA_120430",
        "match_id": "MCI_RMA_UCL_2026",
        "timestamp_ms": 1775304002200,
        "frame_idx": 120430,
        "position_x": 38.2,
        "position_y": 14.5,
        "position_z": 3.42,
        "speed_kmh": 76.2,
        "spin_rpm": 610.0,
        "spin_axis_angle_deg": 110.0,
        "launch_angle_deg": 24.5,
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": 14.8,
        "azimuth_angle_deg": 336.0,
        "flight_phase": "IN_FLIGHT",
        "shot_arc_probability": 0.58,
        "xg_snapshot": 0.45,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },
    {
        "id": "BALL_MCI_RMA_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "timestamp_ms": 1775304002400,
        "frame_idx": 120440,
        "position_x": 46.2,           # Haaland volley contact in 6-yard box
        "position_y": 1.8,
        "position_z": 1.25,
        "speed_kmh": 112.5,           # Striker volley blast!
        "spin_rpm": 840.0,
        "spin_axis_angle_deg": 45.0,
        "launch_angle_deg": 14.2,      # Low rocket toward top-left corner
        "impact_angle_deg": 28.4,      # Shot angle subtended to goal: 28.4° (0.42 rad)
        "elevation_angle_deg": 11.5,
        "azimuth_angle_deg": 354.0,
        "flight_phase": "GOAL_BOUND",
        "shot_arc_probability": 0.89,
        "xg_snapshot": 0.74,           # High-danger xG snapshot!
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },
    {
        "id": "BALL_MCI_RMA_120445",
        "match_id": "MCI_RMA_UCL_2026",
        "timestamp_ms": 1775304002500,
        "frame_idx": 120445,
        "position_x": 52.5,           # Past goal line into top corner netting
        "position_y": -2.4,
        "position_z": 2.15,
        "speed_kmh": 98.0,
        "spin_rpm": 780.0,
        "spin_axis_angle_deg": 40.0,
        "launch_angle_deg": 14.2,
        "impact_angle_deg": 8.2,
        "elevation_angle_deg": 5.0,
        "azimuth_angle_deg": 355.0,
        "flight_phase": "NET_ENTRY",
        "shot_arc_probability": 1.0,
        "xg_snapshot": 1.0,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },

    # ---------------- BASKETBALL BALL TRAJECTORY SEQUENCE (Curry Step-Back 3-Pointer) ----------------
    {
        "id": "BALL_LAL_GSW_99395",
        "match_id": "LAL_GSW_NBA_2026",
        "timestamp_ms": 1775304003500,
        "frame_idx": 99395,
        "position_x": 6.5,
        "position_y": -5.8,
        "position_z": 2.85,           # Ball release from Curry's hand
        "speed_kmh": 34.2,
        "spin_rpm": 320.0,            # High backspin
        "spin_axis_angle_deg": 270.0,
        "launch_angle_deg": 48.5,      # Optimal 48.5° 3-point launch angle!
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": 48.5,
        "azimuth_angle_deg": 38.5,
        "flight_phase": "RELEASE",
        "shot_arc_probability": 0.68,
        "xg_snapshot": None,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },
    {
        "id": "BALL_LAL_GSW_99405",
        "match_id": "LAL_GSW_NBA_2026",
        "timestamp_ms": 1775304003700,
        "frame_idx": 99405,
        "position_x": 10.2,
        "position_y": -2.8,
        "position_z": 4.75,           # Apex of rainbow arc
        "speed_kmh": 26.5,
        "spin_rpm": 310.0,
        "spin_axis_angle_deg": 270.0,
        "launch_angle_deg": 48.5,
        "impact_angle_deg": 0.0,
        "elevation_angle_deg": 2.5,
        "azimuth_angle_deg": 38.0,
        "flight_phase": "ARC_PEAK",
        "shot_arc_probability": 0.78,
        "xg_snapshot": None,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    },
    {
        "id": "BALL_LAL_GSW_99415",
        "match_id": "LAL_GSW_NBA_2026",
        "timestamp_ms": 1775304003900,
        "frame_idx": 99415,
        "position_x": 13.75,          # Swish through center of 3.05m high hoop
        "position_y": 0.0,
        "position_z": 3.05,
        "speed_kmh": 31.8,
        "spin_rpm": 295.0,
        "spin_axis_angle_deg": 270.0,
        "launch_angle_deg": 48.5,
        "impact_angle_deg": 44.8,      # Clean 44.8° hoop entry angle!
        "elevation_angle_deg": -44.8,
        "azimuth_angle_deg": 37.8,
        "flight_phase": "NET_ENTRY",
        "shot_arc_probability": 1.0,
        "xg_snapshot": None,
        "hawkeye_pitch_x": None,
        "hawkeye_pitch_y": None
    }
]

PLAYER_POSITIONS_DATA = [
    # ---------------- CRICKET PLAYERS (IND vs AUS, Frame 84210) ----------------
    {
        "id": "PLPOS_IND_AUS_KOHLI_84210",
        "match_id": "IND_AUS_T20_2026",
        "frame_idx": 84210,
        "timestamp_ms": 1775304001200,
        "player_id": "ind_18_kohli",
        "player_name": "Virat Kohli",
        "team": "IND",
        "role": "BATSMAN",
        "position_x": 10.06,
        "position_y": 0.0,
        "position_z": 0.0,
        "facing_angle_deg": 180.0,      # Facing straight down the pitch at bowler
        "movement_angle_deg": 220.0,    # Weight transfer trigger movement
        "velocity_vx": -0.85,
        "velocity_vy": -0.32,
        "velocity_vz": 0.0,
        "speed_kmh": 22.4,
        "acceleration_ms2": 2.8,
        "heart_rate_bpm": 152,
        "defensive_separation_m": 16.5, # Distance to slip cordon
        "defensive_separation_angle_deg": 35.0,
        "target_distance_m": 0.35,      # Distance to batting crease stumps
        "target_angle_deg": 0.0,
        "posture_state": "ON_STRIKE"
    },
    {
        "id": "PLPOS_IND_AUS_STARC_84210",
        "match_id": "IND_AUS_T20_2026",
        "frame_idx": 84210,
        "timestamp_ms": 1775304001200,
        "player_id": "aus_56_starc",
        "player_name": "Mitchell Starc",
        "team": "AUS",
        "role": "BOWLER",
        "position_x": -7.2,
        "position_y": 0.25,
        "position_z": 0.0,
        "facing_angle_deg": 0.0,        # Facing batsman
        "movement_angle_deg": 0.0,
        "velocity_vx": 7.8,
        "velocity_vy": 0.1,
        "velocity_vz": 0.0,
        "speed_kmh": 28.1,
        "acceleration_ms2": -1.4,       # Decelerating in follow-through
        "heart_rate_bpm": 168,
        "defensive_separation_m": 17.2, # Distance to batsman
        "defensive_separation_angle_deg": 0.0,
        "target_distance_m": 17.2,
        "target_angle_deg": 0.0,
        "posture_state": "BOWLING_STRIDE"
    },
    {
        "id": "PLPOS_IND_AUS_CAREY_84210",
        "match_id": "IND_AUS_T20_2026",
        "frame_idx": 84210,
        "timestamp_ms": 1775304001200,
        "player_id": "aus_07_carey",
        "player_name": "Alex Carey",
        "team": "AUS",
        "role": "WICKET_KEEPER",
        "position_x": 19.8,
        "position_y": 0.1,
        "position_z": 0.0,
        "facing_angle_deg": 180.0,
        "movement_angle_deg": 180.0,
        "velocity_vx": 0.1,
        "velocity_vy": 0.0,
        "velocity_vz": 0.0,
        "speed_kmh": 6.2,
        "acceleration_ms2": 0.5,
        "heart_rate_bpm": 138,
        "defensive_separation_m": 9.7,
        "defensive_separation_angle_deg": 180.0,
        "target_distance_m": 9.7,
        "target_angle_deg": 0.0,
        "posture_state": "SLIP_CORDON_STANCE"
    },
    {
        "id": "PLPOS_IND_AUS_SMITH_84210",
        "match_id": "IND_AUS_T20_2026",
        "frame_idx": 84210,
        "timestamp_ms": 1775304001200,
        "player_id": "aus_49_smith",
        "player_name": "Steve Smith",
        "team": "AUS",
        "role": "SLIP_1",
        "position_x": 20.4,
        "position_y": -3.8,
        "position_z": 0.0,
        "facing_angle_deg": 195.0,      # Angled towards bat edge
        "movement_angle_deg": 195.0,
        "velocity_vx": 0.0,
        "velocity_vy": 0.0,
        "velocity_vz": 0.0,
        "speed_kmh": 0.0,
        "acceleration_ms2": 0.0,
        "heart_rate_bpm": 132,
        "defensive_separation_m": 10.9,
        "defensive_separation_angle_deg": 200.0,
        "target_distance_m": 10.9,
        "target_angle_deg": 19.8,
        "posture_state": "SLIP_CORDON_STANCE"
    },

    # ---------------- FOOTBALL PLAYERS (MCI vs RMA, Frame 120440) ----------------
    {
        "id": "PLPOS_MCI_RMA_HAALAND_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "frame_idx": 120440,
        "timestamp_ms": 1775304002400,
        "player_id": "mci_09_haaland",
        "player_name": "Erling Haaland",
        "team": "MCI",
        "role": "STRIKER",
        "position_x": 46.2,
        "position_y": 1.8,
        "position_z": 0.0,
        "facing_angle_deg": 354.0,      # Pointing directly at Real Madrid goal mouth
        "movement_angle_deg": 350.0,    # Attacking near post
        "velocity_vx": 8.9,
        "velocity_vy": -0.8,
        "velocity_vz": 0.0,
        "speed_kmh": 33.8,              # Sprint burst!
        "acceleration_ms2": 3.6,
        "heart_rate_bpm": 174,
        "defensive_separation_m": 1.4,  # Tight physical duel with Rüdiger
        "defensive_separation_angle_deg": 105.0,
        "target_distance_m": 6.5,       # Distance to goal line
        "target_angle_deg": 28.4,       # Subtended goal angle 28.4° (0.42 rad)
        "posture_state": "OFF_BALL_SPRINT"
    },
    {
        "id": "PLPOS_MCI_RMA_RUDIGER_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "frame_idx": 120440,
        "timestamp_ms": 1775304002400,
        "player_id": "rma_22_rudiger",
        "player_name": "Antonio Rüdiger",
        "team": "RMA",
        "role": "DEFENDER",
        "position_x": 47.4,
        "position_y": 2.2,
        "position_z": 0.0,
        "facing_angle_deg": 175.0,      # Facing Haaland & ball delivery
        "movement_angle_deg": 348.0,    # Recovering back towards goal
        "velocity_vx": 8.5,
        "velocity_vy": -0.9,
        "velocity_vz": 0.0,
        "speed_kmh": 32.6,
        "acceleration_ms2": 3.1,
        "heart_rate_bpm": 178,
        "defensive_separation_m": 1.4,
        "defensive_separation_angle_deg": 285.0,
        "target_distance_m": 5.4,
        "target_angle_deg": 32.0,
        "posture_state": "DEFENSIVE_BLOCK"
    },
    {
        "id": "PLPOS_MCI_RMA_COURTOIS_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "frame_idx": 120440,
        "timestamp_ms": 1775304002400,
        "player_id": "rma_01_courtois",
        "player_name": "Thibaut Courtois",
        "team": "RMA",
        "role": "GOALKEEPER",
        "position_x": 51.2,
        "position_y": 0.5,
        "position_z": 0.0,
        "facing_angle_deg": 180.0,      # Angled towards incoming volley
        "movement_angle_deg": 260.0,    # Diving lateral save
        "velocity_vx": -0.8,
        "velocity_vy": -2.4,
        "velocity_vz": 0.6,
        "speed_kmh": 12.2,
        "acceleration_ms2": 4.2,
        "heart_rate_bpm": 162,
        "defensive_separation_m": 5.2,
        "defensive_separation_angle_deg": 195.0,
        "target_distance_m": 1.3,
        "target_angle_deg": 88.0,
        "posture_state": "DIVING_SAVE"
    },
    {
        "id": "PLPOS_MCI_RMA_KDB_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "frame_idx": 120440,
        "timestamp_ms": 1775304002400,
        "player_id": "mci_17_debruyne",
        "player_name": "Kevin De Bruyne",
        "team": "MCI",
        "role": "MIDFIELDER",
        "position_x": 32.4,
        "position_y": 21.5,
        "position_z": 0.0,
        "facing_angle_deg": 340.0,      # Watching cross trajectory
        "movement_angle_deg": 0.0,
        "velocity_vx": 1.8,
        "velocity_vy": 0.0,
        "velocity_vz": 0.0,
        "speed_kmh": 14.5,
        "acceleration_ms2": 0.2,
        "heart_rate_bpm": 166,
        "defensive_separation_m": 6.8,
        "defensive_separation_angle_deg": 18.0,
        "target_distance_m": 29.5,
        "target_angle_deg": 14.2,
        "posture_state": "HIGH_PRESSING"
    },

    # ---------------- BASKETBALL PLAYERS (LAL vs GSW, Frame 99400) ----------------
    {
        "id": "PLPOS_LAL_GSW_CURRY_99400",
        "match_id": "LAL_GSW_NBA_2026",
        "frame_idx": 99400,
        "timestamp_ms": 1775304003600,
        "player_id": "gsw_30_curry",
        "player_name": "Stephen Curry",
        "team": "GSW",
        "role": "GUARD",
        "position_x": 6.5,
        "position_y": -5.8,
        "position_z": 0.0,
        "facing_angle_deg": 38.5,       # Facing basketball rim
        "movement_angle_deg": 218.5,    # Step-back separation move
        "velocity_vx": -1.4,
        "velocity_vy": 1.1,
        "velocity_vz": 0.0,
        "speed_kmh": 21.2,
        "acceleration_ms2": 3.8,
        "heart_rate_bpm": 165,
        "defensive_separation_m": 2.1,  # Contested separation
        "defensive_separation_angle_deg": 42.0,
        "target_distance_m": 7.42,      # NBA 3-point distance
        "target_angle_deg": 38.5,
        "posture_state": "SET_SHOT"
    },
    {
        "id": "PLPOS_LAL_GSW_LEBRON_99400",
        "match_id": "LAL_GSW_NBA_2026",
        "frame_idx": 99400,
        "timestamp_ms": 1775304003600,
        "player_id": "lal_23_james",
        "player_name": "LeBron James",
        "team": "LAL",
        "role": "FORWARD",
        "position_x": 8.1,
        "position_y": -4.2,
        "position_z": 0.0,
        "facing_angle_deg": 218.5,      # Contesting Curry's jump shot
        "movement_angle_deg": 218.5,    # Closeout contest
        "velocity_vx": -2.2,
        "velocity_vy": -1.4,
        "velocity_vz": 0.8,
        "speed_kmh": 18.5,
        "acceleration_ms2": 4.1,
        "heart_rate_bpm": 160,
        "defensive_separation_m": 2.1,
        "defensive_separation_angle_deg": 0.0,
        "target_distance_m": 7.2,
        "target_angle_deg": 220.0,
        "posture_state": "DEFENSIVE_BLOCK"
    },
    {
        "id": "PLPOS_LAL_GSW_AD_99400",
        "match_id": "LAL_GSW_NBA_2026",
        "frame_idx": 99400,
        "timestamp_ms": 1775304003600,
        "player_id": "lal_03_davis",
        "player_name": "Anthony Davis",
        "team": "LAL",
        "role": "CENTER",
        "position_x": 12.4,
        "position_y": 0.5,
        "position_z": 0.0,
        "facing_angle_deg": 220.0,      # Positioning for defensive rebound
        "movement_angle_deg": 180.0,
        "velocity_vx": -0.5,
        "velocity_vy": 0.0,
        "velocity_vz": 0.0,
        "speed_kmh": 9.4,
        "acceleration_ms2": 1.2,
        "heart_rate_bpm": 156,
        "defensive_separation_m": 1.2,
        "defensive_separation_angle_deg": 180.0,
        "target_distance_m": 1.5,
        "target_angle_deg": 18.0,
        "posture_state": "DEFENSIVE_BLOCK"
    }
]

TACTICAL_MOMENTS_DATA = [
    {
        "id": "MOMENT_CRICKET_DRS_LBW_84210",
        "match_id": "IND_AUS_T20_2026",
        "event_name": "DRS_LBW_REVIEW_HAWKEYE",
        "sport": "CRICKET",
        "timestamp_ms": 1775304001200,
        "primary_camera_id": "CAM_IND_AUS_HAWKEYE_DRS",
        "secondary_cameras_json": json.dumps([
            "CAM_IND_AUS_POV_KOHLI",
            "CAM_IND_AUS_REFEREE_UMPIRE",
            "CAM_IND_AUS_MAIN"
        ]),
        "ball_position_json": json.dumps({
            "x": 6.8, "y": 0.2, "z": 0.08,
            "speed_kmh": 144.2,
            "pitch_angle_deg": 3.2,
            "swing_angle_deg": 1.1,
            "seam_angle_deg": 18.4
        }),
        "key_player_positions_json": json.dumps({
            "batsman": {"id": "ind_18_kohli", "name": "Virat Kohli", "x": 10.06, "y": 0.0},
            "bowler": {"id": "aus_56_starc", "name": "Mitchell Starc", "x": -7.2, "y": 0.25}
        }),
        "critical_angle_metric": "HawkEye Pitch Angle: 3.2° | Impact Deviation: 1.1° | xWicket: 0.72",
        "decision_outcome": "OUT",
        "ai_narrative": "Umpire signal DRS review for LBW. Ball-tracking Hawkeye cameras engaged at 3.2° pitch angle, confirming impact in-line and hitting leg stump."
    },
    {
        "id": "MOMENT_FOOTBALL_VAR_PENALTY_120440",
        "match_id": "MCI_RMA_UCL_2026",
        "event_name": "VAR_PENALTY_OFFSIDE_CHECK",
        "sport": "FOOTBALL",
        "timestamp_ms": 1775304002400,
        "primary_camera_id": "CAM_MCI_RMA_VAR_OFFSIDE",
        "secondary_cameras_json": json.dumps([
            "CAM_MCI_RMA_FAN_ENDZONE",
            "CAM_MCI_RMA_REFEREE_BODY",
            "CAM_MCI_RMA_MAIN"
        ]),
        "ball_position_json": json.dumps({
            "x": 46.2, "y": 1.8, "z": 1.25,
            "speed_kmh": 112.5,
            "goal_angle_deg": 28.4,
            "subtended_angle_rad": 0.42,
            "xg_snapshot": 0.74
        }),
        "key_player_positions_json": json.dumps({
            "striker": {"id": "mci_09_haaland", "name": "Erling Haaland", "x": 46.2, "y": 1.8},
            "defender": {"id": "rma_22_rudiger", "name": "Antonio Rüdiger", "x": 47.4, "y": 2.2}
        }),
        "critical_angle_metric": "Goalmouth Angle: 28.4° | Offside Gap: +0.38m (Onside) | xG: 0.74",
        "decision_outcome": "PENALTY_GIVEN",
        "ai_narrative": "VAR pitchside monitor review confirms offside line clear by 0.38m; foul awarded inside penalty box."
    },
    {
        "id": "MOMENT_BASKETBALL_BUZZER_BEATER_99400",
        "match_id": "LAL_GSW_NBA_2026",
        "event_name": "CLUTCH_BUZZER_BEATER_3PT",
        "sport": "BASKETBALL",
        "timestamp_ms": 1775304003600,
        "primary_camera_id": "CAM_LAL_GSW_BACKBOARD_SLOW",
        "secondary_cameras_json": json.dumps([
            "CAM_LAL_GSW_POV_CURRY",
            "CAM_LAL_GSW_UNDER_RIM",
            "CAM_LAL_GSW_MAIN"
        ]),
        "ball_position_json": json.dumps({
            "x": 6.5, "y": -5.8, "z": 2.85,
            "speed_kmh": 34.2,
            "launch_angle_deg": 48.5,
            "hoop_entry_angle_deg": 44.8,
            "shot_arc_probability": 0.68
        }),
        "key_player_positions_json": json.dumps({
            "shooter": {"id": "gsw_30_curry", "name": "Stephen Curry", "x": 6.5, "y": -5.8},
            "defender": {"id": "lal_23_james", "name": "LeBron James", "x": 8.1, "y": -4.2}
        }),
        "critical_angle_metric": "3PT Release Launch Angle: 48.5° | Net Entry Angle: 44.8° | Clock: 0.4s",
        "decision_outcome": "SHOT_MADE",
        "ai_narrative": "Game 7 buzzer-beater released with 0.4 seconds remaining at optimal 48.5° arc angle over contest."
    }
]

CAMERA_PRESETS_DATA = [
    # Cricket Presets
    {"id": "PRESET_CRICKET_CASUAL", "match_id": "IND_AUS_T20_2026", "name": "Casual TV Mode", "camera_id": "CAM_IND_AUS_MAIN", "persona": "CASUAL", "transition_time_ms": 400, "description": "Crisp wide coverage with automated AI commentary"},
    {"id": "PRESET_CRICKET_GENZ", "match_id": "IND_AUS_T20_2026", "name": "High-Octane POV", "camera_id": "CAM_IND_AUS_POV_KOHLI", "persona": "GEN_Z", "transition_time_ms": 200, "description": "Helmet-cam thrill with 15s prediction popups"},
    {"id": "PRESET_CRICKET_HARDCORE", "match_id": "IND_AUS_T20_2026", "name": "HawkEye Analytics Hub", "camera_id": "CAM_IND_AUS_HAWKEYE_DRS", "persona": "HARDCORE", "transition_time_ms": 150, "description": "Sub-millimeter Hawkeye pitch telemetry and release angles"},
    {"id": "PRESET_CRICKET_STADIUM", "match_id": "IND_AUS_T20_2026", "name": "MCG 360° Great Southern", "camera_id": "CAM_IND_AUS_FAN_ENDZONE", "persona": "STADIUM", "transition_time_ms": 300, "description": "Direct stadium seat view with decibel resonance"},
    
    # Football Presets
    {"id": "PRESET_FOOTBALL_CASUAL", "match_id": "MCI_RMA_UCL_2026", "name": "Etihad Gantry Main", "camera_id": "CAM_MCI_RMA_MAIN", "persona": "CASUAL", "transition_time_ms": 400, "description": "Clear full-pitch broadcast view"},
    {"id": "PRESET_FOOTBALL_HARDCORE", "match_id": "MCI_RMA_UCL_2026", "name": "Sky Tactical Grid", "camera_id": "CAM_MCI_RMA_SKY", "persona": "HARDCORE", "transition_time_ms": 200, "description": "Formation lines, pressing coordinates, and xG heatmaps"},
    {"id": "PRESET_FOOTBALL_GENZ", "match_id": "MCI_RMA_UCL_2026", "name": "Striker POV", "camera_id": "CAM_MCI_RMA_POV_HAALAND", "persona": "GEN_Z", "transition_time_ms": 250, "description": "Haaland forward view right in the box"},
    {"id": "PRESET_FOOTBALL_CLANS", "match_id": "MCI_RMA_UCL_2026", "name": "South Stand Ultra Fan", "camera_id": "CAM_MCI_RMA_FAN_ENDZONE", "persona": "CLUB_MEMBER", "transition_time_ms": 300, "description": "Behind-the-goal curva clan battle stream"},

    # Basketball Presets
    {"id": "PRESET_BASKETBALL_CASUAL", "match_id": "LAL_GSW_NBA_2026", "name": "Center Court 4K", "camera_id": "CAM_LAL_GSW_MAIN", "persona": "CASUAL", "transition_time_ms": 400, "description": "Standard prime network television view"},
    {"id": "PRESET_BASKETBALL_HARDCORE", "match_id": "LAL_GSW_NBA_2026", "name": "Glass Slow-Mo & Trajectories", "camera_id": "CAM_LAL_GSW_BACKBOARD_SLOW", "persona": "HARDCORE", "transition_time_ms": 150, "description": "Shot arc release angles and high-speed telemetry"}
]


# ==============================================================================
# DATABASE POPULATION FUNCTIONS
# ==============================================================================

def initialize_and_seed_database(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Executes schema DDL and populates all tables with match angles and positions."""
    print(f"[Seed] Initializing SQLite database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    # Apply Schema
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    cur = conn.cursor()

    # 1. Matches
    for m in MATCHES_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO matches (
                id, sport, title, home_team, away_team, venue,
                dimensions_length_m, dimensions_width_m, dimensions_height_m,
                status, start_time, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["id"], m["sport"], m["title"], m["home_team"], m["away_team"], m["venue"],
            m["dimensions_length_m"], m["dimensions_width_m"], m["dimensions_height_m"],
            m["status"], m["start_time"], m["metadata_json"]
        ))

    # 2. Camera Angles
    for c in CAMERA_ANGLES_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO camera_angles (
                id, match_id, camera_angle_type, label, icon,
                position_x, position_y, position_z,
                pitch_deg, yaw_deg, roll_deg, field_of_view_deg, focal_length_mm,
                target_focal_x, target_focal_y, target_focal_z,
                resolution, frame_rate_fps, latency_offset_ms, stream_url,
                is_active, recommended_persona, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"], c["match_id"], c["camera_angle_type"], c["label"], c["icon"],
            c["position_x"], c["position_y"], c["position_z"],
            c["pitch_deg"], c["yaw_deg"], c["roll_deg"], c["field_of_view_deg"], c.get("focal_length_mm"),
            c["target_focal_x"], c["target_focal_y"], c["target_focal_z"],
            c["resolution"], c["frame_rate_fps"], c["latency_offset_ms"], c["stream_url"],
            c["is_active"], c["recommended_persona"], c.get("description")
        ))

    # 3. Ball Telemetry Frames
    for b in BALL_TELEMETRY_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO ball_telemetry_frames (
                id, match_id, timestamp_ms, frame_idx,
                position_x, position_y, position_z, speed_kmh, spin_rpm,
                spin_axis_angle_deg, launch_angle_deg, impact_angle_deg,
                elevation_angle_deg, azimuth_angle_deg, flight_phase,
                shot_arc_probability, xg_snapshot, hawkeye_pitch_x, hawkeye_pitch_y
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b["id"], b["match_id"], b["timestamp_ms"], b["frame_idx"],
            b["position_x"], b["position_y"], b["position_z"], b["speed_kmh"], b["spin_rpm"],
            b["spin_axis_angle_deg"], b["launch_angle_deg"], b["impact_angle_deg"],
            b["elevation_angle_deg"], b["azimuth_angle_deg"], b["flight_phase"],
            b["shot_arc_probability"], b["xg_snapshot"], b.get("hawkeye_pitch_x"), b.get("hawkeye_pitch_y")
        ))

    # 4. Player Positions
    for p in PLAYER_POSITIONS_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO player_positions (
                id, match_id, frame_idx, timestamp_ms,
                player_id, player_name, team, role,
                position_x, position_y, position_z,
                facing_angle_deg, movement_angle_deg,
                velocity_vx, velocity_vy, velocity_vz,
                speed_kmh, acceleration_ms2, heart_rate_bpm,
                defensive_separation_m, defensive_separation_angle_deg,
                target_distance_m, target_angle_deg, posture_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["match_id"], p["frame_idx"], p["timestamp_ms"],
            p["player_id"], p["player_name"], p["team"], p["role"],
            p["position_x"], p["position_y"], p["position_z"],
            p["facing_angle_deg"], p["movement_angle_deg"],
            p["velocity_vx"], p["velocity_vy"], p["velocity_vz"],
            p["speed_kmh"], p["acceleration_ms2"], p["heart_rate_bpm"],
            p["defensive_separation_m"], p["defensive_separation_angle_deg"],
            p["target_distance_m"], p["target_angle_deg"], p["posture_state"]
        ))

    # 5. Tactical Moments
    for t in TACTICAL_MOMENTS_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO tactical_moments (
                id, match_id, event_name, sport, timestamp_ms,
                primary_camera_id, secondary_cameras_json,
                ball_position_json, key_player_positions_json,
                critical_angle_metric, decision_outcome, ai_narrative
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"], t["match_id"], t["event_name"], t["sport"], t["timestamp_ms"],
            t["primary_camera_id"], t["secondary_cameras_json"],
            t["ball_position_json"], t["key_player_positions_json"],
            t["critical_angle_metric"], t["decision_outcome"], t["ai_narrative"]
        ))

    # 6. Camera Presets
    for cp in CAMERA_PRESETS_DATA:
        cur.execute("""
            INSERT OR REPLACE INTO camera_presets (
                id, match_id, name, camera_id, persona, transition_time_ms, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cp["id"], cp["match_id"], cp["name"], cp["camera_id"], cp["persona"],
            cp["transition_time_ms"], cp["description"]
        ))

    conn.commit()
    print("[Seed] Successfully committed all records.")
    return conn

def export_json_fixtures():
    """Exports structured JSON fixtures for API mocking and frontend ingestion."""
    fixtures = {
        "export_timestamp": int(time.time() * 1000),
        "matches": MATCHES_DATA,
        "camera_angles": CAMERA_ANGLES_DATA,
        "ball_telemetry_frames": BALL_TELEMETRY_DATA,
        "player_positions": PLAYER_POSITIONS_DATA,
        "tactical_moments": TACTICAL_MOMENTS_DATA,
        "camera_presets": CAMERA_PRESETS_DATA
    }
    with open(FIXTURES_JSON, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)
    print(f"[Seed] Exported JSON fixtures to: {FIXTURES_JSON}")

def export_seed_sql(conn: sqlite3.Connection):
    """Dumps all data into an executable SQL insert file."""
    with open(SEED_SQL_FILE, "w", encoding="utf-8") as f:
        f.write("-- SYNCRO PRIME Seed Data Dump\n")
        f.write("-- Matches, Camera Angles, Ball Telemetry, Player Coordinates & Tactical Moments\n\n")
        for line in conn.iterdump():
            if line.startswith("INSERT INTO"):
                f.write(line + "\n")
    print(f"[Seed] Exported SQL seed dump to: {SEED_SQL_FILE}")

def print_database_summary(conn: sqlite3.Connection):
    """Queries and prints table counts and verification samples."""
    cur = conn.cursor()
    print("\n" + "=" * 70)
    print("SYNCRO PRIME: MATCH ANGLES & POSITIONS DATABASE SUMMARY")
    print("=" * 70)

    tables = ["matches", "camera_angles", "ball_telemetry_frames", "player_positions", "tactical_moments", "camera_presets"]
    for t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  • Table '{t}': {count} records")

    print("\n--- Available Matches ---")
    for row in cur.execute("SELECT id, sport, title, venue FROM matches").fetchall():
        print(f"  [{row[1]}] {row[0]}: {row[2]} ({row[3]})")

    print("\n--- Camera Perspectives by Match ---")
    for row in cur.execute("""
        SELECT m.sport, c.camera_angle_type, c.label, c.position_x, c.position_y, c.position_z, c.pitch_deg, c.yaw_deg, c.recommended_persona
        FROM camera_angles c
        JOIN matches m ON m.id = c.match_id
        ORDER BY m.sport, c.id
    """).fetchall():
        print(f"  [{row[0]}] {row[1]:<17} | {row[2]:<26} | Pos: ({row[3]:>5.1f}, {row[4]:>5.1f}, {row[5]:>4.1f}m) | Angles: (P:{row[6]:>5.1f}°, Y:{row[7]:>5.1f}°) | {row[8]}")

    print("\n--- Key 3D Ball Angles & Speeds ---")
    for row in cur.execute("""
        SELECT match_id, frame_idx, speed_kmh, launch_angle_deg, impact_angle_deg, flight_phase
        FROM ball_telemetry_frames
    """).fetchall():
        print(f"  Match: {row[0]} | Frame #{row[1]} | Speed: {row[2]} km/h | Launch: {row[3]}° | Impact: {row[4]}° | Phase: {row[5]}")

    print("\n--- Key Player Coordinates & Orientation Angles ---")
    for row in cur.execute("""
        SELECT match_id, player_name, role, position_x, position_y, facing_angle_deg, speed_kmh, target_angle_deg, posture_state
        FROM player_positions
    """).fetchall():
        print(f"  {row[1]} ({row[2]} - {row[0]}): Pos: ({row[3]:.1f}, {row[4]:.1f}) | Facing: {row[5]:.1f}° | Speed: {row[6]} km/h | Target Subtended: {row[7]:.1f}° | {row[8]}")

    print("\n--- Tactical Moments Linked with Critical Camera Angles ---")
    for row in cur.execute("""
        SELECT event_name, sport, primary_camera_id, critical_angle_metric, decision_outcome
        FROM tactical_moments
    """).fetchall():
        print(f"  Event: {row[0]} ({row[1]})")
        print(f"    Primary Camera: {row[2]}")
        print(f"    Critical Metric: {row[3]}")
        print(f"    Verdict Outcome: {row[4]}")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    conn = initialize_and_seed_database()
    export_json_fixtures()
    export_seed_sql(conn)
    print_database_summary(conn)
    conn.close()

import sqlite3
import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from app.config import settings

try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    aiosqlite = None
    HAS_AIOSQLITE = False

class TelemetryDatabaseManager:
    """
    Manages connections and queries for the Match Angles, Camera Perspectives
    and Spatial Coordinates Database (matches_telemetry.db).
    Supports both aiosqlite and asyncio.to_thread(sqlite3) fallback.
    """
    _instance: Optional['TelemetryDatabaseManager'] = None

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.MATCHES_DB_FILE

    @classmethod
    def get_instance(cls) -> 'TelemetryDatabaseManager':
        if cls._instance is None:
            cls._instance = TelemetryDatabaseManager()
        return cls._instance

    def get_sync_connection(self) -> sqlite3.Connection:
        """Returns standard sqlite3 connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def _execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Executes a SELECT query asynchronously."""
        def _sync_select():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(query, params)
                return cur.fetchall()
        return await asyncio.to_thread(_sync_select)

    async def _execute_write(self, write_fn):
        """Executes write operations in background thread with WAL mode."""
        def _sync_write():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                res = write_fn(cur)
                conn.commit()
                return res
        return await asyncio.to_thread(_sync_write)

    async def get_all_matches(self) -> List[Dict[str, Any]]:
        """Retrieves all matches."""
        rows = await self._execute_query("SELECT * FROM matches ORDER BY start_time ASC")
        return [
            {
                "id": r["id"],
                "sport": r["sport"],
                "title": r["title"],
                "homeTeam": r["home_team"],
                "awayTeam": r["away_team"],
                "venue": r["venue"],
                "dimensions": {
                    "lengthM": r["dimensions_length_m"],
                    "widthM": r["dimensions_width_m"],
                    "heightM": r["dimensions_height_m"],
                },
                "status": r["status"],
                "startTime": r["start_time"],
                "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            }
            for r in rows
        ]

    async def get_camera_angles(
        self,
        match_id: str,
        angle_type: Optional[str] = None,
        persona: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves camera angles with precise 3D position and rotation angles."""
        query = "SELECT * FROM camera_angles WHERE match_id = ?"
        params: List[Any] = [match_id]

        if angle_type:
            query += " AND camera_angle_type = ?"
            params.append(angle_type)
        if persona:
            query += " AND recommended_persona = ?"
            params.append(persona)

        query += " ORDER BY id ASC"
        rows = await self._execute_query(query, tuple(params))
        return [
            {
                "id": r["id"],
                "matchId": r["match_id"],
                "angleType": r["camera_angle_type"],
                "label": r["label"],
                "icon": r["icon"],
                "position": {
                    "x": r["position_x"],
                    "y": r["position_y"],
                    "z": r["position_z"]
                },
                "rotation": {
                    "pitchDeg": r["pitch_deg"],
                    "yawDeg": r["yaw_deg"],
                    "rollDeg": r["roll_deg"]
                },
                "optics": {
                    "fieldOfViewDeg": r["field_of_view_deg"],
                    "focalLengthMm": r["focal_length_mm"],
                    "targetFocalPoint": {
                        "x": r["target_focal_x"],
                        "y": r["target_focal_y"],
                        "z": r["target_focal_z"]
                    }
                },
                "stream": {
                    "resolution": r["resolution"],
                    "frameRateFps": r["frame_rate_fps"],
                    "latencyOffsetMs": r["latency_offset_ms"],
                    "streamUrl": r["stream_url"]
                },
                "isActive": bool(r["is_active"]),
                "recommendedPersona": r["recommended_persona"],
                "description": r["description"]
            }
            for r in rows
        ]

    async def get_camera_by_id(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single camera angle by its ID."""
        rows = await self._execute_query("SELECT * FROM camera_angles WHERE id = ?", (camera_id,))
        if not rows:
            return None
        r = rows[0]
        return {
            "id": r["id"],
            "matchId": r["match_id"],
            "angleType": r["camera_angle_type"],
            "label": r["label"],
            "icon": r["icon"],
            "position": {"x": r["position_x"], "y": r["position_y"], "z": r["position_z"]},
            "rotation": {"pitchDeg": r["pitch_deg"], "yawDeg": r["yaw_deg"], "rollDeg": r["roll_deg"]},
            "optics": {
                "fieldOfViewDeg": r["field_of_view_deg"],
                "focalLengthMm": r["focal_length_mm"],
                "targetFocalPoint": {"x": r["target_focal_x"], "y": r["target_focal_y"], "z": r["target_focal_z"]}
            },
            "stream": {
                "resolution": r["resolution"],
                "frameRateFps": r["frame_rate_fps"],
                "latencyOffsetMs": r["latency_offset_ms"],
                "streamUrl": r["stream_url"]
            },
            "isActive": bool(r["is_active"]),
            "recommendedPersona": r["recommended_persona"],
            "description": r["description"]
        }

    async def get_ball_telemetry_frames(
        self,
        match_id: str,
        frame_idx: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieves ball telemetry frames with trajectory and impact angles."""
        query = "SELECT * FROM ball_telemetry_frames WHERE match_id = ?"
        params: List[Any] = [match_id]

        if frame_idx is not None:
            query += " AND frame_idx = ?"
            params.append(frame_idx)

        query += " ORDER BY frame_idx ASC LIMIT ?"
        params.append(limit)

        rows = await self._execute_query(query, tuple(params))
        return [
            {
                "id": r["id"],
                "matchId": r["match_id"],
                "timestampMs": r["timestamp_ms"],
                "frameIdx": r["frame_idx"],
                "position": {"x": r["position_x"], "y": r["position_y"], "z": r["position_z"]},
                "speedKmh": r["speed_kmh"],
                "spinRpm": r["spin_rpm"],
                "spinAxisAngleDeg": r["spin_axis_angle_deg"],
                "angles": {
                    "launchAngleDeg": r["launch_angle_deg"],
                    "impactAngleDeg": r["impact_angle_deg"],
                    "elevationAngleDeg": r["elevation_angle_deg"],
                    "azimuthAngleDeg": r["azimuth_angle_deg"]
                },
                "flightPhase": r["flight_phase"],
                "shotArcProbability": r["shot_arc_probability"],
                "xgSnapshot": r["xg_snapshot"],
                "hawkeyePitchPoint": {
                    "x": r["hawkeye_pitch_x"],
                    "y": r["hawkeye_pitch_y"]
                } if r["hawkeye_pitch_x"] is not None else None
            }
            for r in rows
        ]

    async def get_player_positions(
        self,
        match_id: str,
        frame_idx: Optional[int] = None,
        player_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves player spatial coordinates and directional angles."""
        query = "SELECT * FROM player_positions WHERE match_id = ?"
        params: List[Any] = [match_id]

        if frame_idx is not None:
            query += " AND frame_idx = ?"
            params.append(frame_idx)
        if player_id:
            query += " AND player_id = ?"
            params.append(player_id)

        query += " ORDER BY frame_idx ASC, team ASC, role ASC"
        rows = await self._execute_query(query, tuple(params))
        return [
            {
                "id": r["id"],
                "matchId": r["match_id"],
                "frameIdx": r["frame_idx"],
                "timestampMs": r["timestamp_ms"],
                "playerId": r["player_id"],
                "playerName": r["player_name"],
                "team": r["team"],
                "role": r["role"],
                "position": {"x": r["position_x"], "y": r["position_y"], "z": r["position_z"]},
                "angles": {
                    "facingAngleDeg": r["facing_angle_deg"],
                    "movementAngleDeg": r["movement_angle_deg"],
                    "defensiveSeparationAngleDeg": r["defensive_separation_angle_deg"],
                    "targetAngleDeg": r["target_angle_deg"]
                },
                "velocity": {
                    "vx": r["velocity_vx"],
                    "vy": r["velocity_vy"],
                    "vz": r["velocity_vz"]
                },
                "speedKmh": r["speed_kmh"],
                "accelerationMs2": r["acceleration_ms2"],
                "heartRateBpm": r["heart_rate_bpm"],
                "defensiveSeparationM": r["defensive_separation_m"],
                "targetDistanceM": r["target_distance_m"],
                "postureState": r["posture_state"]
            }
            for r in rows
        ]

    async def get_tactical_moments(self, match_id: str) -> List[Dict[str, Any]]:
        """Retrieves moments linking telemetry, decisive angles, and camera perspectives."""
        rows = await self._execute_query("SELECT * FROM tactical_moments WHERE match_id = ?", (match_id,))
        return [
            {
                "id": r["id"],
                "matchId": r["match_id"],
                "eventName": r["event_name"],
                "sport": r["sport"],
                "timestampMs": r["timestamp_ms"],
                "primaryCameraId": r["primary_camera_id"],
                "secondaryCameras": json.loads(r["secondary_cameras_json"]) if r["secondary_cameras_json"] else [],
                "ballPosition": json.loads(r["ball_position_json"]) if r["ball_position_json"] else {},
                "keyPlayerPositions": json.loads(r["key_player_positions_json"]) if r["key_player_positions_json"] else {},
                "criticalAngleMetric": r["critical_angle_metric"],
                "decisionOutcome": r["decision_outcome"],
                "aiNarrative": r["ai_narrative"]
            }
            for r in rows
        ]

    async def get_camera_presets(self, match_id: str, persona: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves quick camera switching presets."""
        query = "SELECT * FROM camera_presets WHERE match_id = ?"
        params: List[Any] = [match_id]
        if persona:
            query += " AND persona = ?"
            params.append(persona)

        rows = await self._execute_query(query, tuple(params))
        return [
            {
                "id": r["id"],
                "matchId": r["match_id"],
                "name": r["name"],
                "cameraId": r["camera_id"],
                "persona": r["persona"],
                "transitionTimeMs": r["transition_time_ms"],
                "description": r["description"]
            }
            for r in rows
        ]

    async def record_telemetry_frame(
        self,
        match_id: str,
        frame_idx: int,
        timestamp_ms: int,
        ball: Dict[str, Any],
        players: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Persists a new frame's ball trajectory angles and player spatial positions."""
        def _write(cur):
            # 1. Insert Ball Frame
            ball_id = f"BALL_{match_id}_{frame_idx}"
            cur.execute("""
                INSERT OR REPLACE INTO ball_telemetry_frames (
                    id, match_id, timestamp_ms, frame_idx,
                    position_x, position_y, position_z,
                    speed_kmh, spin_rpm, spin_axis_angle_deg,
                    launch_angle_deg, impact_angle_deg,
                    elevation_angle_deg, azimuth_angle_deg,
                    flight_phase, shot_arc_probability, xg_snapshot,
                    hawkeye_pitch_x, hawkeye_pitch_y
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ball_id, match_id, timestamp_ms, frame_idx,
                ball.get("x", 0.0), ball.get("y", 0.0), ball.get("z", 0.0),
                ball.get("speed_kmh", 0.0), ball.get("spin_rpm"), ball.get("spin_axis_angle_deg"),
                ball.get("launch_angle_deg", 0.0), ball.get("impact_angle_deg", 0.0),
                ball.get("elevation_angle_deg", 0.0), ball.get("azimuth_angle_deg", 0.0),
                ball.get("flight_phase", "IN_FLIGHT"), ball.get("shot_arc_probability"), ball.get("xg_snapshot"),
                ball.get("hawkeye_pitch_x"), ball.get("hawkeye_pitch_y")
            ))

            # 2. Insert Player Positions
            for p in players:
                p_id = f"PLPOS_{match_id}_{p.get('player_id', 'unknown')}_{frame_idx}"
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
                    p_id, match_id, frame_idx, timestamp_ms,
                    p.get("player_id"), p.get("player_name", "Athlete"), p.get("team", "T1"), p.get("role", "PLAYER"),
                    p.get("x", 0.0), p.get("y", 0.0), p.get("z", 0.0),
                    p.get("facing_angle_deg", 0.0), p.get("movement_angle_deg", 0.0),
                    p.get("vx", 0.0), p.get("vy", 0.0), p.get("vz", 0.0),
                    p.get("speed_kmh", 0.0), p.get("acceleration_ms2", 0.0), p.get("heart_rate_bpm"),
                    p.get("defensive_separation_m"), p.get("defensive_separation_angle_deg"),
                    p.get("target_distance_m"), p.get("target_angle_deg", 0.0), p.get("posture_state", "RUNNING")
                ))
            return {"status": "persisted", "frameIdx": frame_idx, "playersCount": len(players)}

        return await self._execute_write(_write)

telemetry_db = TelemetryDatabaseManager.get_instance()

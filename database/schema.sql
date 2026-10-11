-- ==============================================================================
-- SYNCRO PRIME: Match Angles, Camera Perspectives & Spatial Positions Schema
-- High-Concurrency, Ultra-Low-Latency Multi-Sport Telemetry Database
-- Supports: Football, Cricket, Basketball
-- Storage Engine: SQLite (WAL Mode, Normalized Relational Schema)
-- ==============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- ------------------------------------------------------------------------------
-- 1. MATCHES TABLE
-- Master catalog of sports fixtures with arena coordinate boundaries.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,                            -- e.g. 'IND_AUS_T20_2026'
    sport TEXT NOT NULL CHECK(sport IN ('CRICKET', 'FOOTBALL', 'BASKETBALL')),
    title TEXT NOT NULL,                           -- Match display title
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    venue TEXT NOT NULL,                           -- Stadium / Arena name
    dimensions_length_m REAL NOT NULL,             -- Field/Pitch length in meters
    dimensions_width_m REAL NOT NULL,              -- Field/Pitch width in meters
    dimensions_height_m REAL NOT NULL,             -- Vertical ceiling / clearance (m)
    status TEXT NOT NULL DEFAULT 'LIVE' CHECK(status IN ('UPCOMING', 'LIVE', 'HALFTIME', 'COMPLETED')),
    start_time INTEGER NOT NULL,                   -- Epoch timestamp ms
    metadata_json TEXT                             -- Additional match configuration (JSON)
);

-- ------------------------------------------------------------------------------
-- 2. CAMERA ANGLES TABLE
-- Multi-Perspective broadcast, tactical, and POV camera feeds.
-- Stores precise 3D coordinates (X, Y, Z), optical rotation angles (Pitch, Yaw, Roll),
-- field of view (FOV), target focal points, and live stream connection URIs.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS camera_angles (
    id TEXT PRIMARY KEY,                            -- e.g. 'CAM_IND_AUS_MAIN'
    match_id TEXT NOT NULL,                         -- Reference to matches(id)
    camera_angle_type TEXT NOT NULL CHECK(
        camera_angle_type IN (
            'MAIN_BROADCAST',
            'SKY_TACTICAL',
            'PLAYER_POV',
            'FAN_ENDZONE',
            'HAWKEYE_3D',
            'REFEREE_BODY_CAM',
            'SIDELINE_BENCH',
            'AERIAL_DRONE'
        )
    ),
    label TEXT NOT NULL,                            -- User-facing display title (e.g. '4K Ultra Broadcast')
    icon TEXT NOT NULL DEFAULT '🎥',                -- UI representation emote / icon
    position_x REAL NOT NULL,                       -- Camera X coordinate in pitch meters (-Length/2 to +Length/2)
    position_y REAL NOT NULL,                       -- Camera Y coordinate in pitch meters (-Width/2 to +Width/2)
    position_z REAL NOT NULL,                       -- Camera elevation / height in meters above ground
    pitch_deg REAL NOT NULL,                        -- Tilt angle (-90° pointing down, +90° pointing up)
    yaw_deg REAL NOT NULL,                          -- Horizontal pan angle (0° to 360°, 0° = +X direction)
    roll_deg REAL NOT NULL DEFAULT 0.0,             -- Cant / tilt angle (-180° to +180°)
    field_of_view_deg REAL NOT NULL,                -- Optical Field of View (e.g. 35° telephoto to 120° wide)
    focal_length_mm REAL,                           -- Lens focal length in mm
    target_focal_x REAL NOT NULL DEFAULT 0.0,       -- Look-at focal point X
    target_focal_y REAL NOT NULL DEFAULT 0.0,       -- Look-at focal point Y
    target_focal_z REAL NOT NULL DEFAULT 1.0,       -- Look-at focal point Z
    resolution TEXT NOT NULL DEFAULT '3840x2160',   -- Stream resolution
    frame_rate_fps INTEGER NOT NULL DEFAULT 60,     -- Optical capture frame rate (60fps, 120fps, 500fps)
    latency_offset_ms INTEGER NOT NULL DEFAULT 0,   -- Sync alignment offset in milliseconds
    stream_url TEXT NOT NULL,                       -- RTSP / WebRTC / LL-CMAF stream URI
    is_active INTEGER NOT NULL DEFAULT 1,           -- 1 = Online, 0 = Standby
    recommended_persona TEXT NOT NULL DEFAULT 'CASUAL' CHECK(
        recommended_persona IN ('CASUAL', 'GEN_Z', 'HARDCORE', 'CLUB_MEMBER', 'STADIUM', 'BROADCASTER')
    ),
    description TEXT,                               -- Tactical or contextual description
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 3. BALL TELEMETRY FRAMES TABLE
-- Frame-by-frame 3D ball coordinates, launch angles, impact angles, spin, and velocity.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ball_telemetry_frames (
    id TEXT PRIMARY KEY,                            -- e.g. 'BALL_IND_AUS_84210'
    match_id TEXT NOT NULL,                         -- Reference to matches(id)
    timestamp_ms INTEGER NOT NULL,                  -- Epoch timestamp ms
    frame_idx INTEGER NOT NULL,                     -- Sequential optical frame index
    position_x REAL NOT NULL,                       -- Ball 3D position X (meters)
    position_y REAL NOT NULL,                       -- Ball 3D position Y (meters)
    position_z REAL NOT NULL,                       -- Ball 3D position Z (elevation in meters)
    speed_kmh REAL NOT NULL,                        -- Ball velocity in km/h
    spin_rpm REAL,                                  -- Ball spin rate in revolutions per minute
    spin_axis_angle_deg REAL,                       -- Spin vector tilt angle (0° - 360°)
    launch_angle_deg REAL,                          -- Initial trajectory release/launch angle (-90° to +90°)
    impact_angle_deg REAL,                          -- Pitch bounce / contact impact angle (e.g. Hawkeye 3.2°)
    elevation_angle_deg REAL,                       -- Instantaneous vertical angle from ground plane
    azimuth_angle_deg REAL,                         -- Instantaneous horizontal compass angle (0° - 360°)
    flight_phase TEXT NOT NULL DEFAULT 'IN_FLIGHT' CHECK(
        flight_phase IN (
            'RUN_UP',
            'RELEASE',
            'IN_FLIGHT',
            'PITCH_BOUNCE',
            'BAT_IMPACT',
            'GOAL_BOUND',
            'ARC_PEAK',
            'NET_ENTRY'
        )
    ),
    shot_arc_probability REAL,                      -- Probability of trajectory converting (0.0 to 1.0)
    xg_snapshot REAL,                               -- Expected Goals value at shot moment (0.0 to 1.0)
    hawkeye_pitch_x REAL,                           -- Hawkeye bounce coordinate X
    hawkeye_pitch_y REAL,                           -- Hawkeye bounce coordinate Y
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 4. PLAYER POSITIONS TABLE
-- Frame-accurate player spatial coordinates, heading angles, velocity vectors,
-- tactical roles, heart rate, and calculated geometric angles to target.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_positions (
    id TEXT PRIMARY KEY,                            -- e.g. 'PLPOS_IND_AUS_KOHLI_84210'
    match_id TEXT NOT NULL,                         -- Reference to matches(id)
    frame_idx INTEGER NOT NULL,                     -- Optical frame index
    timestamp_ms INTEGER NOT NULL,                  -- Epoch timestamp ms
    player_id TEXT NOT NULL,                        -- Unique athlete identifier
    player_name TEXT NOT NULL,                      -- Full name
    team TEXT NOT NULL,                             -- Team acronym (e.g. 'IND', 'AUS', 'MCI', 'RMA')
    role TEXT NOT NULL,                             -- Tactical role (BATSMAN, BOWLER, STRIKER, etc.)
    position_x REAL NOT NULL,                       -- Player coordinate X (meters)
    position_y REAL NOT NULL,                       -- Player coordinate Y (meters)
    position_z REAL NOT NULL DEFAULT 0.0,           -- Player elevation (meters)
    facing_angle_deg REAL NOT NULL,                 -- Heading/orientation direction (0° to 360°)
    movement_angle_deg REAL NOT NULL,               -- Direction of velocity vector (0° to 360°)
    velocity_vx REAL NOT NULL DEFAULT 0.0,          -- Velocity component X (m/s)
    velocity_vy REAL NOT NULL DEFAULT 0.0,          -- Velocity component Y (m/s)
    velocity_vz REAL NOT NULL DEFAULT 0.0,          -- Velocity component Z (m/s)
    speed_kmh REAL NOT NULL,                        -- Absolute speed in km/h
    acceleration_ms2 REAL NOT NULL DEFAULT 0.0,     -- Acceleration magnitude (m/s²)
    heart_rate_bpm INTEGER,                         -- Biometric telemetry sensor
    defensive_separation_m REAL,                    -- Distance to nearest opposing defender (meters)
    defensive_separation_angle_deg REAL,            -- Angle to nearest defender relative to heading
    target_distance_m REAL,                         -- Distance to target (goal line, stumps, or rim)
    target_angle_deg REAL,                          -- Subtended shot/pass angle to target in degrees
    posture_state TEXT NOT NULL DEFAULT 'RUNNING' CHECK(
        posture_state IN (
            'ON_STRIKE',
            'BOWLING_STRIDE',
            'SLIP_CORDON_STANCE',
            'OFF_BALL_SPRINT',
            'HIGH_PRESSING',
            'DEFENSIVE_BLOCK',
            'DIVING_SAVE',
            'SET_SHOT',
            'ISOLATION_DRIBBLE'
        )
    ),
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 5. TACTICAL MOMENTS TABLE
-- High-impact match events (DRS reviews, VAR penalty checks, clutch buzzer beaters)
-- linking telemetry, decisive angles, decision outcomes, and primary camera views.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tactical_moments (
    id TEXT PRIMARY KEY,                            -- e.g. 'MOMENT_DRS_LBW_84210'
    match_id TEXT NOT NULL,                         -- Reference to matches(id)
    event_name TEXT NOT NULL,                       -- e.g. 'DRS_LBW_REVIEW_HAWKEYE'
    sport TEXT NOT NULL,                            -- CRICKET, FOOTBALL, BASKETBALL
    timestamp_ms INTEGER NOT NULL,                  -- Epoch timestamp ms
    primary_camera_id TEXT NOT NULL,                -- Recommended camera angle for viewing
    secondary_cameras_json TEXT,                    -- Array of alternative camera angle IDs (JSON)
    ball_position_json TEXT NOT NULL,               -- 3D ball state at moment of event (JSON)
    key_player_positions_json TEXT NOT NULL,        -- Key players coordinates & angles (JSON)
    critical_angle_metric TEXT NOT NULL,            -- e.g. 'Hawkeye Pitch Angle: 3.2° | Impact Deviation: 1.1°'
    decision_outcome TEXT NOT NULL,                 -- 'OUT', 'NOT OUT', 'PENALTY_GIVEN', 'GOAL', etc.
    ai_narrative TEXT NOT NULL,                     -- Contextual VLM explanation
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY(primary_camera_id) REFERENCES camera_angles(id)
);

-- ------------------------------------------------------------------------------
-- 6. CAMERA PRESETS TABLE
-- Quick-switch viewing profiles tailored for distinct user personas & directors.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS camera_presets (
    id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    name TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    persona TEXT NOT NULL CHECK(
        persona IN ('CASUAL', 'GEN_Z', 'HARDCORE', 'CLUB_MEMBER', 'STADIUM', 'BROADCASTER')
    ),
    transition_time_ms INTEGER NOT NULL DEFAULT 300,
    description TEXT,
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY(camera_id) REFERENCES camera_angles(id)
);

-- ------------------------------------------------------------------------------
-- INDEXES FOR SUB-5MS QUERY PERFORMANCE
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_camera_match ON camera_angles(match_id);
CREATE INDEX IF NOT EXISTS idx_camera_type ON camera_angles(camera_angle_type);
CREATE INDEX IF NOT EXISTS idx_camera_persona ON camera_angles(recommended_persona);

CREATE INDEX IF NOT EXISTS idx_ball_match_frame ON ball_telemetry_frames(match_id, frame_idx);
CREATE INDEX IF NOT EXISTS idx_ball_match_ts ON ball_telemetry_frames(match_id, timestamp_ms);

CREATE INDEX IF NOT EXISTS idx_player_match_frame ON player_positions(match_id, frame_idx);
CREATE INDEX IF NOT EXISTS idx_player_match_player ON player_positions(match_id, player_id);

CREATE INDEX IF NOT EXISTS idx_moments_match ON tactical_moments(match_id);
CREATE INDEX IF NOT EXISTS idx_moments_event ON tactical_moments(event_name);

CREATE INDEX IF NOT EXISTS idx_presets_match_persona ON camera_presets(match_id, persona);

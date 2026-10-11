# SYNCRO PRIME: Match Angles, Camera Perspectives & Spatial Positions Database

Welcome to the **SYNCRO PRIME Match Angles & Positions Database**, engineered for high-concurrency, ultra-low-latency sports companions and multi-audience broadcast simulation across **Cricket, Football, and Basketball**.

This database provides high-precision **3D spatial tracking coordinates $(X, Y, Z)$**, **optical camera rotation angles (Pitch, Yaw, Roll, FOV)**, **ball trajectory angles (Launch, Hawkeye pitch bounce, Goalmouth subtended)**, and **player orientation heading angles ($0^\circ - 360^\circ$)** to test the entire backend and telemetry pipeline.

---

## 1. Directory Structure

```
database/
├── matches_telemetry.db       # Active SQLite Relational Database (WAL mode enabled)
├── schema.sql                 # Pristine SQL DDL Schema with normalized tables & indexes
├── seed_data.sql              # Pure SQL dump of all seed records
├── seed_angles_positions.py   # Seeding & inspection CLI script
├── verify_database.py         # 7-Suite automated integrity & angle geometry test runner
├── run_tests.py               # Async backend integration test runner
├── README.md                  # Complete architectural documentation (this file)
└── fixtures/
    └── match_angles_positions.json  # Comprehensive JSON dataset for API mocks & testing
```

---

## 2. Relational Schema Architecture

The database is built on 6 core normalized tables:

| Table | Records | Description | Primary Key |
|---|---|---|---|
| `matches` | 3 | Master fixture catalog across sports with arena metric dimensions | `id` |
| `camera_angles` | 24 | Multi-angle perspectives with 3D positions, Pitch/Yaw/Roll, FOV, and stream URLs | `id` |
| `ball_telemetry_frames` | 13 | Frame-by-frame 3D coordinates, launch angles, Hawkeye pitch impact, spin & speed | `id` |
| `player_positions` | 12 | Athlete spatial coordinates, facing heading angles, velocity vectors, and roles | `id` |
| `tactical_moments` | 3 | Critical match moments (DRS LBW, VAR Penalty, Buzzer Beater) bound to primary cameras | `id` |
| `camera_presets` | 10 | Quick camera switching profiles tailored for the 6 audience personas | `id` |

---

## 3. Spatial Coordinates & Optical Angles System

### 3.1 Arena 3D Coordinate Frame $(X, Y, Z)$
- **Origin $(0, 0, 0)$**: Exact center of the pitch, court, or oval at turf/hardwood level.
- **$X$-Axis**: Longitude along the length of the arena (Meters).
- **$Y$-Axis**: Latitude along the width of the arena (Meters).
- **$Z$-Axis**: Elevation / height above ground level (Meters).

### 3.2 Camera Rotational Angles
- **Pitch ($\theta_{\text{pitch}}$)**: Optical tilt up/down ($-90^\circ$ pointing vertically down to $+90^\circ$ pointing skyward).
- **Yaw ($\phi_{\text{yaw}}$)**: Optical horizontal pan ($0^\circ$ to $360^\circ$, where $0^\circ$ points down the positive $X$-axis).
- **Roll ($\psi_{\text{roll}}$)**: Cant angle around optical axis ($-180^\circ$ to $+180^\circ$).
- **Field of View ($\text{FOV}$)**: Optical angular width ($30^\circ$ telephoto slow-mo to $130^\circ$ ultra-wide).

### 3.3 Trajectory & Geometric Angles
- **Launch Angle**: Initial elevation angle of release or strike (e.g. Kohli $32.0^\circ$ launch angle, Curry $48.5^\circ$ 3-point release).
- **Hawkeye Pitch Bounce Angle**: Calibrated impact angle onto pitch surface ($3.2^\circ$ LBW ball-tracking).
- **Goalmouth Subtended Angle**: Geometric angle subtended by goal posts ($\theta_{\text{goal}} = 28.4^\circ$, $0.42\text{ rad}$, xG: $0.74$).
- **Player Heading Angle**: Cardinal facing orientation of athlete ($0^\circ$ to $360^\circ$).

---

## 4. Supported Matches & Camera Perspectives

### 1. Cricket: India vs Australia (`IND_AUS_T20_2026`)
- **Venue**: Melbourne Cricket Ground (MCG), $171\text{m} \times 148\text{m} \times 45\text{m}$
- **Cameras (8 Perspectives)**:
  1. `CAM_IND_AUS_MAIN` — 4K Ultra Broadcast ($P: -18.5^\circ, Y: 90.0^\circ$)
  2. `CAM_IND_AUS_SKY` — Sky Tactical 2D/3D Grid ($P: -90.0^\circ, Y: 0.0^\circ$)
  3. `CAM_IND_AUS_POV_KOHLI` — Kohli Helmet-Cam POV ($P: -4.0^\circ, Y: 180.0^\circ$)
  4. `CAM_IND_AUS_POV_STARC` — Starc Bowler Delivery Leap ($P: -8.5^\circ, Y: 0.0^\circ$)
  5. `CAM_IND_AUS_FAN_ENDZONE` — 360° Great Southern Stand ($P: -14.2^\circ, Y: 270.0^\circ$)
  6. `CAM_IND_AUS_HAWKEYE_DRS` — HawkEye DRS Ultra-SlowMo 500fps ($P: -12.4^\circ, Y: 138.0^\circ$)
  7. `CAM_IND_AUS_REFEREE_UMPIRE` — Bowler's End Umpire Cam ($P: -1.8^\circ, Y: 0.0^\circ$)
  8. `CAM_IND_AUS_AERIAL_DRONE` — MCG Orbital 3D Drone ($P: -32.5^\circ, Y: 140.0^\circ$)

### 2. Football: Manchester City vs Real Madrid (`MCI_RMA_UCL_2026`)
- **Venue**: Etihad Stadium, $105\text{m} \times 68\text{m} \times 32\text{m}$
- **Cameras (8 Perspectives)**:
  1. `CAM_MCI_RMA_MAIN` — Etihad Main Stand 4K ($P: -22.0^\circ, Y: 90.0^\circ$)
  2. `CAM_MCI_RMA_SKY` — Tactical 2D Pitch Matrix ($P: -90.0^\circ, Y: 0.0^\circ$)
  3. `CAM_MCI_RMA_POV_HAALAND` — Haaland Striker Head-Cam ($P: -3.5^\circ, Y: 0.0^\circ$)
  4. `CAM_MCI_RMA_FAN_ENDZONE` — South Stand Curva Endzone ($P: -10.5^\circ, Y: 0.0^\circ$)
  5. `CAM_MCI_RMA_VAR_OFFSIDE` — VAR 18-Yard Offside Optical ($P: -16.0^\circ, Y: 90.0^\circ$)
  6. `CAM_MCI_RMA_REFEREE_BODY` — UEFA Referee Chest Cam ($P: -2.0^\circ, Y: 45.0^\circ$)
  7. `CAM_MCI_RMA_SIDELINE_PEP` — Manager Tactical Dugout ($P: -3.0^\circ, Y: 90.0^\circ$)
  8. `CAM_MCI_RMA_AERIAL_DRONE` — Etihad Cable-Cam Aerial ($P: -42.0^\circ, Y: 75.0^\circ$)

### 3. Basketball: Lakers vs Warriors (`LAL_GSW_NBA_2026`)
- **Venue**: Crypto.com Arena, $28.65\text{m} \times 15.24\text{m} \times 12\text{m}$
- **Cameras (8 Perspectives)**:
  1. `CAM_LAL_GSW_MAIN` — Center Court 4K Broadcast ($P: -26.0^\circ, Y: 90.0^\circ$)
  2. `CAM_LAL_GSW_SKY` — Tactical Full Court 2D ($P: -90.0^\circ, Y: 0.0^\circ$)
  3. `CAM_LAL_GSW_POV_LEBRON` — LeBron James Headband POV ($P: -4.0^\circ, Y: 0.0^\circ$)
  4. `CAM_LAL_GSW_POV_CURRY` — Steph Curry Shooter Head-Cam ($P: 12.0^\circ, Y: 48.0^\circ$)
  5. `CAM_LAL_GSW_UNDER_RIM` — Baseline Under-the-Rim 360° ($P: 18.0^\circ, Y: 180.0^\circ$)
  6. `CAM_LAL_GSW_BACKBOARD_SLOW` — High-Angle Glass Slow-Mo 300fps ($P: -35.0^\circ, Y: 180.0^\circ$)
  7. `CAM_LAL_GSW_REFEREE_LEAD` — Lead Referee Baseline Cam ($P: 5.0^\circ, Y: 160.0^\circ$)
  8. `CAM_LAL_GSW_FLOOR_CELEB` — Courtside VIP Floor Seat ($P: 8.0^\circ, Y: 75.0^\circ$)

---

## 5. How to Run, Seed & Verify

### 1. Seed or Recreate the Database
```bash
python database/seed_angles_positions.py
```
This initializes `database/matches_telemetry.db`, applies `database/schema.sql`, and exports updated `database/fixtures/match_angles_positions.json` and `database/seed_data.sql`.

### 2. Run Comprehensive Database Verification
```bash
python database/verify_database.py
```
Executes 7 automated test suites verifying Foreign Key constraints, optical angle ranges, Hawkeye precision, player heading coordinates, and tactical moment camera linkage.

### 3. Run Async Backend Integration Tests
```bash
python database/run_tests.py
```
Executes 6 asynchronous tests validating database retrieval and telemetry ingestion methods via `app.core.telemetry_db`.

---

## 6. Backend REST API Endpoints

The database is integrated into the backend via `app/api/routers/camera_router.py`:

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/matches/{match_id}/cameras` | `GET` | List all camera angles with coordinates, Pitch/Yaw/Roll, FOV, and stream URLs |
| `/api/v1/matches/{match_id}/cameras/{camera_id}` | `GET` | Retrieve detailed configuration for a specific camera |
| `/api/v1/matches/{match_id}/positions` | `GET` | Frame-by-frame ball & player spatial coordinates and directional angles |
| `/api/v1/matches/{match_id}/hawkeye` | `GET` | Hawkeye 3D ball-tracking trajectory and pitch impact angles ($3.2^\circ$) |
| `/api/v1/matches/{match_id}/tactical-moments` | `GET` | Decisive match stoppage moments linked with primary camera perspectives |
| `/api/v1/matches/{match_id}/presets` | `GET` | Quick camera switching profiles customized per audience persona |
| `/api/v1/matches/telemetry/record-frame` | `POST` | Ingest and persist new 3D spatial frames into the database |

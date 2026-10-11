/**
 * SYNCRO PRIME - Dataset 1: Multi-Sport Optical & Sensor Telemetry Dataset
 * Sample Rate: 25 Hz - 50 Hz
 * Supports Cricket, Football, Basketball
 */

import { SportType } from '../config/index.js';

export interface BallState {
  x: number;
  y: number;
  z: number;
  speed_kmh: number;
  spin_rpm?: number;
  trajectory_pitch_point?: { x: number; y: number };
  shot_arc_probability?: number;
}

export interface PlayerCoordinate {
  player_id: string;
  name?: string;
  team: string;
  role?: string;
  x: number;
  y: number;
  speed_kmh: number;
  strike_position?: string;
  bat_speed_kmh?: number;
  release_speed_kmh?: number;
  run_up_velocity_ms?: number;
  heart_rate_bpm?: number;
  defensive_separation_m?: number;
}

export interface MultiSportTelemetryData {
  match_id: string;
  sport: SportType;
  timestamp_ms: number;
  frame_idx: number;
  ball: BallState;
  active_players: PlayerCoordinate[];
  tactical_metadata?: {
    formation?: string;
    defensive_line_height_m?: number;
    shot_clock_seconds?: number;
    drs_review_available?: boolean;
    xg_snapshot?: number;
  };
}

// Sample Seed Frames
export const SAMPLE_CRICKET_TELEMETRY: MultiSportTelemetryData = {
  match_id: 'IND_AUS_T20_2026',
  sport: 'CRICKET',
  timestamp_ms: 1775304001200,
  frame_idx: 84210,
  ball: {
    x: 18.2,
    y: 1.4,
    z: 0.35,
    speed_kmh: 144.2,
    spin_rpm: 2150,
    trajectory_pitch_point: { x: 16.8, y: 0.2 },
  },
  active_players: [
    {
      player_id: 'ind_18_kohli',
      name: 'Virat Kohli',
      team: 'IND',
      role: 'BATSMAN',
      strike_position: 'ON_STRIKE',
      x: 20.1,
      y: 0.0,
      speed_kmh: 22.4,
      bat_speed_kmh: 118.5,
      heart_rate_bpm: 152,
    },
    {
      player_id: 'aus_56_starc',
      name: 'Mitchell Starc',
      team: 'AUS',
      role: 'BOWLER',
      x: 0.5,
      y: 0.1,
      speed_kmh: 28.1,
      release_speed_kmh: 144.2,
      run_up_velocity_ms: 7.4,
      heart_rate_bpm: 168,
    },
  ],
  tactical_metadata: {
    drs_review_available: true,
  },
};

export const SAMPLE_FOOTBALL_TELEMETRY: MultiSportTelemetryData = {
  match_id: 'MCI_RMA_UCL_2026',
  sport: 'FOOTBALL',
  timestamp_ms: 1775304002400,
  frame_idx: 120440,
  ball: {
    x: 74.5,
    y: 32.1,
    z: 1.2,
    speed_kmh: 88.4,
    spin_rpm: 840,
  },
  active_players: [
    {
      player_id: 'mci_09_haaland',
      name: 'Erling Haaland',
      team: 'MCI',
      role: 'STRIKER',
      x: 82.3,
      y: 34.0,
      speed_kmh: 33.8,
      heart_rate_bpm: 174,
      defensive_separation_m: 1.4,
    },
    {
      player_id: 'rma_22_rudiger',
      name: 'Antonio Rüdiger',
      team: 'RMA',
      role: 'DEFENDER',
      x: 83.7,
      y: 34.5,
      speed_kmh: 32.6,
      heart_rate_bpm: 178,
      defensive_separation_m: 1.4,
    },
  ],
  tactical_metadata: {
    formation: '3-2-4-1 vs 4-4-2',
    defensive_line_height_m: 48.2,
    xg_snapshot: 0.74,
  },
};

export const SAMPLE_BASKETBALL_TELEMETRY: MultiSportTelemetryData = {
  match_id: 'LAL_GSW_NBA_2026',
  sport: 'BASKETBALL',
  timestamp_ms: 1775304003600,
  frame_idx: 99400,
  ball: {
    x: 22.4,
    y: 7.5,
    z: 3.8,
    speed_kmh: 34.2,
    shot_arc_probability: 0.68,
  },
  active_players: [
    {
      player_id: 'lal_23_james',
      name: 'LeBron James',
      team: 'LAL',
      role: 'FORWARD',
      x: 21.0,
      y: 7.2,
      speed_kmh: 18.5,
      heart_rate_bpm: 160,
      defensive_separation_m: 2.1,
    },
    {
      player_id: 'gsw_30_curry',
      name: 'Stephen Curry',
      team: 'GSW',
      role: 'GUARD',
      x: 18.4,
      y: 4.2,
      speed_kmh: 21.2,
      heart_rate_bpm: 165,
      defensive_separation_m: 3.4,
    },
  ],
  tactical_metadata: {
    shot_clock_seconds: 4.8,
    formation: 'Horns Flare Spread',
  },
};

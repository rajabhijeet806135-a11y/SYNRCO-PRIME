import { MultiSportTelemetryData } from '../../../datasets/dataset1_telemetry.js';

export interface CricketTacticalAnalysis {
  matchId: string;
  timestampMs: number;
  bowlerReleaseSpeedKmh: number;
  bowlerRunUpVelocityMs: number;
  batsmanBatSpeedKmh: number;
  pitchBouncePoint: { x: number; y: number };
  drsLbwAnalysis: {
    pitching: 'IN_LINE' | 'OUTSIDE_OFF' | 'OUTSIDE_LEG';
    impact: 'IN_LINE' | 'OUTSIDE';
    wickets: 'HITTING' | 'MISSING' | 'UMPIRES_CALL';
    xWicketProbability: number;
  };
  projectedOverRuns: number;
}

export class CricketAdapter {
  public static processFrame(data: MultiSportTelemetryData): CricketTacticalAnalysis {
    const bowler = data.active_players.find((p) => p.role === 'BOWLER');
    const batsman = data.active_players.find((p) => p.role === 'BATSMAN');

    const releaseSpeed = bowler?.release_speed_kmh || data.ball.speed_kmh || 140.0;
    const runUp = bowler?.run_up_velocity_ms || 7.2;
    const batSpeed = batsman?.bat_speed_kmh || 115.0;
    const pitchPoint = data.ball.trajectory_pitch_point || { x: 16.5, y: 0.1 };

    // DRS simulation logic
    const isHitting = Math.abs(pitchPoint.y) < 0.25;
    const xWicket = isHitting ? 0.72 : 0.18;

    return {
      matchId: data.match_id,
      timestampMs: data.timestamp_ms,
      bowlerReleaseSpeedKmh: releaseSpeed,
      bowlerRunUpVelocityMs: runUp,
      batsmanBatSpeedKmh: batSpeed,
      pitchBouncePoint: pitchPoint,
      drsLbwAnalysis: {
        pitching: Math.abs(pitchPoint.y) < 0.2 ? 'IN_LINE' : 'OUTSIDE_OFF',
        impact: 'IN_LINE',
        wickets: isHitting ? 'HITTING' : 'MISSING',
        xWicketProbability: xWicket,
      },
      projectedOverRuns: Math.round(releaseSpeed > 145 ? 6 : 9),
    };
  }
}

import { MultiSportTelemetryData } from '../../../datasets/dataset1_telemetry.js';

export interface BasketballTacticalAnalysis {
  matchId: string;
  timestampMs: number;
  shotClockSeconds: number;
  shotArcProbability: number;
  defensiveSeparationMeters: number;
  isClutchMoment: boolean;
  expectedPointValue: number;
}

export class BasketballAdapter {
  public static processFrame(data: MultiSportTelemetryData): BasketballTacticalAnalysis {
    const shotClock = data.tactical_metadata?.shot_clock_seconds ?? 14.0;
    const shooter = data.active_players.find((p) => p.role === 'GUARD' || p.role === 'FORWARD');
    const separation = shooter?.defensive_separation_m ?? 2.5;
    const arcProb = data.ball.shot_arc_probability ?? 0.55;

    const isClutch = shotClock < 5.0;
    const expectedPoints = parseFloat(((arcProb * (separation > 2.0 ? 3.0 : 2.0))).toFixed(2));

    return {
      matchId: data.match_id,
      timestampMs: data.timestamp_ms,
      shotClockSeconds: shotClock,
      shotArcProbability: arcProb,
      defensiveSeparationMeters: separation,
      isClutchMoment: isClutch,
      expectedPointValue: expectedPoints,
    };
  }
}

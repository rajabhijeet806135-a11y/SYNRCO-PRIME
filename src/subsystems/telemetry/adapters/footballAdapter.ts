import { MultiSportTelemetryData, PlayerCoordinate, BallState } from '../../../datasets/dataset1_telemetry.js';

export interface FootballTacticalAnalysis {
  matchId: string;
  timestampMs: number;
  ball: BallState;
  homeTeamPlayers: PlayerCoordinate[];
  awayTeamPlayers: PlayerCoordinate[];
  defensiveLineHeightMeters: number;
  pressingIntensityIndex: number;
  calculatedExpectedGoalXG: number;
  fastestSprintPlayer: { playerId: string; speedKmh: number };
}

export class FootballAdapter {
  /**
   * Calculates Expected Goals (xG) based on ball position and defensive separation
   */
  public static calculateXG(ballX: number, ballY: number, defensiveSeparation: number): number {
    // Goal center is at (105, 34) on a standard 105x68m pitch
    const dx = 105 - ballX;
    const dy = Math.abs(34 - ballY);
    const distanceToGoal = Math.sqrt(dx * dx + dy * dy);

    if (distanceToGoal > 35) return 0.02;

    // Shot angle
    const angleRad = Math.atan2(7.32 * dx, dx * dx + dy * dy - (7.32 / 2) * (7.32 / 2));
    const baseProb = Math.max(0.01, Math.min(0.95, (angleRad / Math.PI) * (15 / Math.max(1, distanceToGoal))));

    // Adjust for defender proximity
    const defenderBonus = Math.min(1.2, Math.max(0.5, defensiveSeparation / 2.0));
    return parseFloat((baseProb * defenderBonus).toFixed(3));
  }

  public static processFrame(data: MultiSportTelemetryData): FootballTacticalAnalysis {
    const homePlayers = data.active_players.filter((p) => p.team === 'MCI' || p.team === 'HOME');
    const awayPlayers = data.active_players.filter((p) => p.team === 'RMA' || p.team === 'AWAY');

    // Calculate defensive line height (average X coordinate of defenders)
    const defenders = data.active_players.filter((p) => p.role === 'DEFENDER');
    const avgDefX = defenders.length > 0
      ? defenders.reduce((sum, d) => sum + d.x, 0) / defenders.length
      : 45.0;

    // Find fastest sprint in frame
    let maxSpeed = 0;
    let fastestId = 'none';
    for (const p of data.active_players) {
      if (p.speed_kmh > maxSpeed) {
        maxSpeed = p.speed_kmh;
        fastestId = p.name || p.player_id;
      }
    }

    const striker = data.active_players.find((p) => p.role === 'STRIKER');
    const defSeparation = striker?.defensive_separation_m ?? 2.0;
    const xg = this.calculateXG(data.ball.x, data.ball.y, defSeparation);

    return {
      matchId: data.match_id,
      timestampMs: data.timestamp_ms,
      ball: data.ball,
      homeTeamPlayers: homePlayers,
      awayTeamPlayers: awayPlayers,
      defensiveLineHeightMeters: parseFloat(avgDefX.toFixed(1)),
      pressingIntensityIndex: parseFloat((maxSpeed / 30).toFixed(2)),
      calculatedExpectedGoalXG: xg,
      fastestSprintPlayer: {
        playerId: fastestId,
        speedKmh: maxSpeed,
      },
    };
  }
}

/**
 * SYNCRO PRIME - Dataset 4: Historical Multi-Sport Analytics & Head-to-Head Dataset
 * Deep historical stats for Hardcore/Stats persona & AI narrative enrichment
 */

export interface CricketHeadToHead {
  batsman_id: string;
  bowler_id: string;
  balls_faced: number;
  runs_scored: number;
  dismissals: number;
  strike_rate: number;
  dot_ball_percentage: number;
  boundary_percentage: number;
  average_exit_velocity_kmh: number;
}

export interface FootballPenaltyAnalysis {
  striker_id: string;
  goalkeeper_id: string;
  total_penalties: number;
  goals_scored: number;
  conversion_rate: number;
  preferred_target: 'BOTTOM_LEFT' | 'BOTTOM_RIGHT' | 'TOP_LEFT' | 'TOP_RIGHT' | 'CENTER';
  gk_dive_bias: 'LEFT' | 'RIGHT' | 'CENTER';
}

export interface BasketballClutchStats {
  player_id: string;
  clutch_possessions_last_2min: number;
  field_goal_percentage: number;
  three_point_percentage: number;
  win_probability_added: number;
  double_team_frequency: number;
}

export const HISTORICAL_CRICKET_H2H: Record<string, CricketHeadToHead> = {
  'ind_18_kohli_vs_aus_56_starc': {
    batsman_id: 'ind_18_kohli',
    bowler_id: 'aus_56_starc',
    balls_faced: 184,
    runs_scored: 236,
    dismissals: 4,
    strike_rate: 128.26,
    dot_ball_percentage: 42.4,
    boundary_percentage: 16.3,
    average_exit_velocity_kmh: 124.8,
  },
};

export const HISTORICAL_FOOTBALL_PENALTIES: Record<string, FootballPenaltyAnalysis> = {
  'mci_09_haaland_vs_rma_01_courtois': {
    striker_id: 'mci_09_haaland',
    goalkeeper_id: 'rma_01_courtois',
    total_penalties: 7,
    goals_scored: 6,
    conversion_rate: 0.857,
    preferred_target: 'BOTTOM_RIGHT',
    gk_dive_bias: 'RIGHT',
  },
};

export const HISTORICAL_BASKETBALL_CLUTCH: Record<string, BasketballClutchStats> = {
  'lal_23_james': {
    player_id: 'lal_23_james',
    clutch_possessions_last_2min: 342,
    field_goal_percentage: 48.6,
    three_point_percentage: 36.4,
    win_probability_added: 4.82,
    double_team_frequency: 0.78,
  },
};

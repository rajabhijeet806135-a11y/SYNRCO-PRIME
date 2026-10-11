export type SportType = 'CRICKET' | 'FOOTBALL' | 'BASKETBALL';

export type PersonaType = 
  | 'CASUAL' 
  | 'GEN_Z' 
  | 'HARDCORE' 
  | 'CLUB_MEMBER' 
  | 'STADIUM' 
  | 'BROADCASTER';

export type CameraAngle = 
  | 'MAIN_BROADCAST' 
  | 'SKY_TACTICAL' 
  | 'PLAYER_POV' 
  | 'FAN_ENDZONE';

export interface MatchInfo {
  id: string;
  sport: SportType;
  title: string;
  homeTeam: string;
  awayTeam: string;
  homeScore: string;
  awayScore: string;
  status: 'LIVE' | 'UPCOMING' | 'COMPLETED';
  gameClock: string;
  venue: string;
  winProbabilityHome: number; // 0 to 100
  momentumTeam: 'home' | 'away' | 'neutral';
  startTime?: string;
  metadata?: Record<string, any>;
}

export interface BallTelemetry {
  x: number;
  y: number;
  z: number;
  speedKmh: number;
  trajectoryAngle?: number;
  spinRpm?: number;
}

export interface PlayerTelemetry {
  id: string;
  name: string;
  team: 'home' | 'away';
  x: number;
  y: number;
  speedKmh: number;
  heartRate?: number;
  role?: string;
}

export interface MatchTelemetry {
  matchId: string;
  sport: SportType;
  timestampMs: number;
  ball: BallTelemetry;
  players: PlayerTelemetry[];
  tacticalAnalysis: {
    expectedMetricLabel: string; // "xG" | "xWicket" | "ShotQuality"
    expectedMetricValue: number;
    possessionHome: number;
    pitchZone: string;
    defensiveLineHeightMeters?: number;
    aiNarrative: string;
  };
}

export interface ContextualPrediction {
  id: string;
  matchId: string;
  sport: SportType;
  title: string;
  question: string;
  options: string[];
  odds: Record<string, number>;
  windowSeconds: number;
  expiresAt: number; // timestamp ms
  eventType: string; // "DRS_LBW_REVIEW" | "VAR_PENALTY_CHECK" | "CLUTCH_FREE_THROW" | "RAPID_PLAY"
  personaPrompts: Record<string, string>;
  correctOption?: string;
  settled?: boolean;
  userVote?: {
    option: string;
    stake: number;
    payout?: number;
    won?: boolean;
  };
}

export interface CrowdDecibelSnapshot {
  matchId: string;
  currentDecibels: number;
  peakDecibels: number;
  cheerCountTotal: number;
  hypeLevel: 'WARM' | 'HYPED' | 'ROARING' | 'SUPERNOVA';
  vibeHapticThreshold: boolean;
}

export interface ClanInfo {
  id: string;
  name: string;
  sport: SportType;
  badge: string;
  memberCount: number;
  totalXp: number;
  rank: number;
}

export interface ClanChatMessage {
  id: string;
  clanId: string;
  userId: string;
  username: string;
  message: string;
  timestamp: string;
  avatar?: string;
  badge?: string;
}

export interface LeaderboardUser {
  rank: number;
  userId: string;
  username: string;
  avatar: string;
  score: number;
  streak: number;
  persona: PersonaType;
  tier: 'Bronze' | 'Silver' | 'Gold' | 'Diamond';
  clanId?: string;
}

export interface UserProfile {
  userId: string;
  username: string;
  email: string;
  persona: PersonaType;
  syncTokens: number;
  xp: number;
  level: number;
  currentStreak: number;
  highestStreak: number;
  tier: 'Bronze' | 'Silver' | 'Gold' | 'Diamond';
  clanId?: string;
  sybilTrustScore: number;
}

export interface AiHighlightClip {
  clipId: string;
  matchId: string;
  title: string;
  timestampSec: number;
  thumbnailUrl: string;
  aiExplanation: string;
  crowdDecibelPeak: number;
  tags: string[];
}

export interface SponsoredMoment {
  campaignKey: string;
  sponsorName: string;
  sponsorLogo: string;
  tagline: string;
  challengeTitle: string;
  rewardBonusXp: number;
  rewardSyncTokens: number;
}

/**
 * SYNCRO PRIME - Dataset 3: Persona Profile & Gamification Ledger Dataset
 * Tracks user personas, confidence scores, Sybil trust, $SYNC fan tokens, and streaks
 */

import { PersonaType } from '../config/index.js';

export interface PersonaConfidenceScores {
  casual: number;
  genz: number;
  hardcore: number;
  club_member: number;
  stadium?: number;
  broadcaster?: number;
}

export interface GamificationState {
  xp_total: number;
  sync_tokens: number;
  prediction_streak: number;
  streak_multiplier: number;
  tier_badge: 'BRONZE_FAN' | 'SILVER_STRATEGIST' | 'GOLD_CHAMPION' | 'DIAMOND_ANALYST';
}

export interface ActiveSessionMetadata {
  match_id: string;
  client_platform: 'WEB' | 'MOBILE_PWA' | 'BROADCAST_SDK' | 'STADIUM_5G';
  stadium_location?: string;
  offline_queue_depth: number;
  last_active_timestamp: number;
}

export interface UserPersonaProfile {
  user_id: string;
  username: string;
  preferred_persona: PersonaType;
  persona_confidence_scores: PersonaConfidenceScores;
  account_verification: 'GUEST' | 'REGISTERED' | 'EMAIL_VERIFIED' | 'PHONE_VERIFIED';
  sybil_trust_score: number; // 0.0 to 1.0
  clan_id?: string;
  gamification_state: GamificationState;
  active_session?: ActiveSessionMetadata;
}

export const SAMPLE_USERS: UserPersonaProfile[] = [
  {
    user_id: 'usr_genz_7721',
    username: 'NeonStriker99',
    preferred_persona: 'GEN_Z',
    persona_confidence_scores: {
      casual: 0.12,
      genz: 0.81,
      hardcore: 0.44,
      club_member: 0.62,
    },
    account_verification: 'EMAIL_VERIFIED',
    sybil_trust_score: 0.94,
    clan_id: 'clan_mumbai_indians_elite',
    gamification_state: {
      xp_total: 4850,
      sync_tokens: 1280,
      prediction_streak: 5,
      streak_multiplier: 3.0,
      tier_badge: 'DIAMOND_ANALYST',
    },
    active_session: {
      match_id: 'IND_AUS_T20_2026',
      client_platform: 'MOBILE_PWA',
      stadium_location: 'SEC_114_ROW_G',
      offline_queue_depth: 0,
      last_active_timestamp: 1775304000000,
    },
  },
  {
    user_id: 'usr_hardcore_104',
    username: 'TacticalMastermind',
    preferred_persona: 'HARDCORE',
    persona_confidence_scores: {
      casual: 0.05,
      genz: 0.32,
      hardcore: 0.96,
      club_member: 0.55,
    },
    account_verification: 'PHONE_VERIFIED',
    sybil_trust_score: 0.99,
    clan_id: 'clan_cityzens_global',
    gamification_state: {
      xp_total: 12400,
      sync_tokens: 4350,
      prediction_streak: 8,
      streak_multiplier: 3.0,
      tier_badge: 'DIAMOND_ANALYST',
    },
  },
  {
    user_id: 'usr_casual_332',
    username: 'WeekendViewer',
    preferred_persona: 'CASUAL',
    persona_confidence_scores: {
      casual: 0.88,
      genz: 0.2,
      hardcore: 0.1,
      club_member: 0.15,
    },
    account_verification: 'REGISTERED',
    sybil_trust_score: 0.85,
    gamification_state: {
      xp_total: 620,
      sync_tokens: 250,
      prediction_streak: 2,
      streak_multiplier: 1.0,
      tier_badge: 'BRONZE_FAN',
    },
  },
];

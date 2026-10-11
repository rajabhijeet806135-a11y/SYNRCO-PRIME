/**
 * SYNCRO PRIME - Core Event Bus Topics
 * Standardized pub/sub message topics across all subsystems
 */

export const TOPICS = {
  // Telemetry Ingestion
  TELEMETRY_RAW: 'telemetry.raw',
  TELEMETRY_PROCESSED: 'telemetry.processed',
  
  // Shared VLM Inference & Context
  VLM_INFERENCE_REQUEST: 'vlm.inference.request',
  VLM_INFERENCE_RESULT: 'vlm.inference.result',
  CONTEXTUAL_EVENT: 'events.contextual',
  DEAD_TIME_DETECTED: 'events.dead_time',
  HIGHLIGHT_GENERATED: 'events.highlight',
  
  // Predictions & Settlement
  PREDICTION_CREATED: 'predictions.created',
  PREDICTION_LOCKED: 'predictions.locked',
  PREDICTION_CLOSED: 'predictions.closed',
  PREDICTION_SETTLED: 'predictions.settled',
  PREDICTION_VOTE_SUBMITTED: 'predictions.vote_submitted',
  
  // Crowd & Decibels
  CROWD_CHEER: 'crowd.cheer',
  CROWD_DECIBEL_UPDATE: 'crowd.decibel_update',
  HAPTIC_TRIGGER: 'crowd.haptic_trigger',
  
  // Clans & Communities
  CLAN_POINTS_AWARDED: 'clans.points_awarded',
  CLAN_WAR_UPDATE: 'clans.war_update',
  CLAN_MESSAGE: 'clans.message',
  
  // Security, Sybil & Bot Defense
  SYBIL_FLAGGED: 'sybil.flagged',
  PROOF_OF_WATCH_CHALLENGE: 'sybil.proof_challenge',
  
  // Offline & Synchronization
  OFFLINE_SYNC_BATCH: 'offline.sync_batch',
  
  // Leaderboards & CQRS
  LEADERBOARD_UPDATED: 'leaderboard.updated',
  AUDIT_LOG_ENTRY: 'audit.log_entry',
} as const;

export type TopicName = (typeof TOPICS)[keyof typeof TOPICS];

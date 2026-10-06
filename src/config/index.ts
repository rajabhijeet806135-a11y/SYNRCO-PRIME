import dotenv from 'dotenv';
dotenv.config();

export const CONFIG = {
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: parseInt(process.env.PORT || '8080', 10),
  HOST: process.env.HOST || '0.0.0.0',
  WS_PORT: parseInt(process.env.WS_PORT || '8080', 10),

  // Security & JWT
  JWT_SECRET: process.env.JWT_SECRET || 'syncro_prime_ultra_secure_jwt_secret_key_2026_!@#$',
  JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET || 'syncro_prime_refresh_token_secret_key_2026_!@#$',
  JWT_ACCESS_EXPIRY: '15m',
  JWT_REFRESH_EXPIRY: '30d',
  GUEST_TOKEN_EXPIRY: '24h',

  // Redis / In-Memory CQRS Config
  REDIS_URL: process.env.REDIS_URL || '',
  REDIS_SENTINEL_ENABLED: process.env.REDIS_SENTINEL_ENABLED === 'true',
  REDIS_FAILOVER_TIMEOUT_MS: 5000,
  VLM_CACHE_TTL_MS: 500, // 500ms TTL per architecture spec
  TELEMETRY_CACHE_TTL_MS: 200,

  // Settlement & Durability
  DB_FILE: process.env.DB_FILE || './syncro_prime_ledger.sqlite',
  SETTLEMENT_BATCH_INTERVAL_MS: 1000, // 1000ms background DB batch cycle
  SETTLEMENT_SLA_TARGET_MS: 100, // Sub-100ms UX settlement target

  // Sybil & Bot Defense Thresholds
  SYBIL: {
    FULL_REWARD_THRESHOLD: 0.75,
    SHADOW_LIMIT_THRESHOLD: 0.40,
    MIN_HUMAN_REACTION_MS: 150, // Sub-150ms is flagged as bot
    MAX_ACCOUNTS_PER_SUBNET: 5,
    NEW_ACCOUNT_HOURS_GATE: 24,
    NEW_ACCOUNT_REWARD_RATE: 0.10, // 10% rewards for unverified <24h accounts
  },

  // Token Buckets
  RATE_LIMIT: {
    BURST_CAPACITY: 100,
    REFILL_RATE_PER_SEC: 20,
    WS_BURST_CAPACITY: 50,
    WS_REFILL_RATE_PER_SEC: 10,
  },

  // Telemetry Ingestion
  TELEMETRY_FREQ_HZ: 25, // 25Hz - 50Hz optical tracking
  OFFLINE_TOLERANCE_SECONDS: 90,

  // Supported Sports
  SPORTS: ['FOOTBALL', 'CRICKET', 'BASKETBALL'] as const,

  // Personas
  PERSONAS: [
    'CASUAL',
    'GEN_Z',
    'HARDCORE',
    'CLUB_MEMBER',
    'STADIUM',
    'BROADCASTER'
  ] as const,
};

export type SportType = (typeof CONFIG.SPORTS)[number];
export type PersonaType = (typeof CONFIG.PERSONAS)[number];

-- SYNCRO PRIME - Master Relational Ledger Schema
-- Compatible with SQLite & PostgreSQL

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  username TEXT NOT NULL,
  password_hash TEXT,
  preferred_persona TEXT NOT NULL DEFAULT 'CASUAL',
  persona_scores_json TEXT NOT NULL DEFAULT '{"casual":1.0,"genz":0.0,"hardcore":0.0,"club_member":0.0,"stadium":0.0,"broadcaster":0.0}',
  account_verification TEXT NOT NULL DEFAULT 'GUEST', -- GUEST, REGISTERED, EMAIL_VERIFIED, PHONE_VERIFIED
  sybil_trust_score REAL NOT NULL DEFAULT 1.0,
  clan_id TEXT,
  xp_total INTEGER NOT NULL DEFAULT 0,
  sync_tokens INTEGER NOT NULL DEFAULT 100,
  prediction_streak INTEGER NOT NULL DEFAULT 0,
  streak_multiplier REAL NOT NULL DEFAULT 1.0,
  tier_badge TEXT NOT NULL DEFAULT 'BRONZE_FAN',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  device_fingerprint TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  subnet TEXT NOT NULL,
  user_agent TEXT,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS matches (
  id TEXT PRIMARY KEY,
  sport TEXT NOT NULL, -- FOOTBALL, CRICKET, BASKETBALL
  title TEXT NOT NULL,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'LIVE', -- SCHEDULED, LIVE, PAUSED, COMPLETED
  start_time INTEGER NOT NULL,
  end_time INTEGER,
  metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS predictions (
  id TEXT PRIMARY KEY,
  match_id TEXT NOT NULL,
  sport TEXT NOT NULL,
  title TEXT NOT NULL,
  question TEXT NOT NULL,
  options_json TEXT NOT NULL,
  correct_option TEXT,
  status TEXT NOT NULL DEFAULT 'OPEN', -- OPEN, LOCKED, CLOSED, SETTLED
  window_seconds INTEGER NOT NULL DEFAULT 30,
  odds_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  closed_at INTEGER,
  settled_at INTEGER,
  FOREIGN KEY(match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS user_predictions (
  id TEXT PRIMARY KEY,
  prediction_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  selected_option TEXT NOT NULL,
  stake_tokens INTEGER NOT NULL DEFAULT 0,
  points_won INTEGER NOT NULL DEFAULT 0,
  tokens_won INTEGER NOT NULL DEFAULT 0,
  is_settled INTEGER NOT NULL DEFAULT 0,
  client_event_id TEXT UNIQUE,
  sybil_score_at_vote REAL NOT NULL DEFAULT 1.0,
  submitted_at INTEGER NOT NULL,
  FOREIGN KEY(prediction_id) REFERENCES predictions(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS token_ledger (
  id TEXT PRIMARY KEY,
  settlement_id TEXT UNIQUE,
  user_id TEXT NOT NULL,
  match_id TEXT,
  transaction_type TEXT NOT NULL, -- PREDICTION_WIN, TRIVIA_WIN, CHEER_REWARD, CLAN_WAR_WIN, STREAK_BONUS
  token_amount INTEGER NOT NULL,
  xp_amount INTEGER NOT NULL,
  balance_after INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS clans (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  tag TEXT NOT NULL UNIQUE,
  description TEXT,
  avatar_url TEXT,
  total_points INTEGER NOT NULL DEFAULT 0,
  member_count INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS clan_members (
  clan_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'MEMBER', -- LEADER, ELITE, MEMBER
  joined_at INTEGER NOT NULL,
  PRIMARY KEY(clan_id, user_id),
  FOREIGN KEY(clan_id) REFERENCES clans(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_stream (
  id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  topic TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  timestamp INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS offline_sync_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  batch_size INTEGER NOT NULL,
  success_count INTEGER NOT NULL,
  replay_status TEXT NOT NULL,
  synced_at INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Indexes for high query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
CREATE INDEX IF NOT EXISTS idx_user_pred_user ON user_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_pred_client_id ON user_predictions(client_event_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_user ON token_ledger(user_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_settlement ON token_ledger(settlement_id);
CREATE INDEX IF NOT EXISTS idx_audit_stream_ts ON audit_stream(timestamp);

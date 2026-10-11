import aiosqlite
import asyncio
import json
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  username TEXT NOT NULL,
  password_hash TEXT,
  preferred_persona TEXT NOT NULL DEFAULT 'CASUAL',
  persona_scores_json TEXT NOT NULL DEFAULT '{"casual":1.0,"genz":0.0,"hardcore":0.0,"club_member":0.0,"stadium":0.0,"broadcaster":0.0}',
  account_verification TEXT NOT NULL DEFAULT 'GUEST',
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
  sport TEXT NOT NULL,
  title TEXT NOT NULL,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'LIVE',
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
  status TEXT NOT NULL DEFAULT 'OPEN',
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
  transaction_type TEXT NOT NULL,
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
  role TEXT NOT NULL DEFAULT 'MEMBER',
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

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
CREATE INDEX IF NOT EXISTS idx_user_pred_user ON user_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_pred_client_id ON user_predictions(client_event_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_user ON token_ledger(user_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_settlement ON token_ledger(settlement_id);
CREATE INDEX IF NOT EXISTS idx_audit_stream_ts ON audit_stream(timestamp);
"""

@dataclass
class BatchLedgerItem:
    id: str
    settlement_id: str
    user_id: str
    match_id: Optional[str]
    transaction_type: str
    token_amount: int
    xp_amount: int
    balance_after: int
    created_at: int

class RelationalLedger:
    _instance: Optional['RelationalLedger'] = None

    def __init__(self):
        self.db_path = settings.DB_FILE
        self._write_queue: List[BatchLedgerItem] = []
        self._flusher_task: Optional[asyncio.Task] = None
        self._is_running = True

    @classmethod
    def get_instance(cls) -> 'RelationalLedger':
        if cls._instance is None:
            cls._instance = RelationalLedger()
        return cls._instance

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode = WAL;")
            await db.execute("PRAGMA synchronous = NORMAL;")
            await db.executescript(SCHEMA_SQL)
            await db.commit()

        if self._flusher_task is None or self._flusher_task.done():
            self._flusher_task = asyncio.create_task(self._periodic_flusher())

    def queue_ledger_write(self, item: BatchLedgerItem):
        self._write_queue.append(item)

    async def _periodic_flusher(self):
        while self._is_running:
            await asyncio.sleep(settings.SETTLEMENT_BATCH_INTERVAL_MS / 1000.0)
            await self.flush_batch()

    async def flush_batch(self) -> int:
        if not self._write_queue:
            return 0

        batch = self._write_queue[:]
        self._write_queue.clear()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                now = int(time.time() * 1000)
                for item in batch:
                    await db.execute("""
                        INSERT OR IGNORE INTO token_ledger (
                            id, settlement_id, user_id, match_id, transaction_type,
                            token_amount, xp_amount, balance_after, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.id,
                        item.settlement_id,
                        item.user_id,
                        item.match_id,
                        item.transaction_type,
                        item.token_amount,
                        item.xp_amount,
                        item.balance_after,
                        item.created_at
                    ))

                    await db.execute("""
                        UPDATE users 
                        SET sync_tokens = sync_tokens + ?, 
                            xp_total = xp_total + ?, 
                            updated_at = ? 
                        WHERE id = ?
                    """, (
                        item.token_amount,
                        item.xp_amount,
                        now,
                        item.user_id
                    ))

                await db.commit()
            return len(batch)
        except Exception as e:
            print(f"[RelationalLedger] Error in flush_batch: {e}")
            # Re-queue on failure
            self._write_queue = batch + self._write_queue
            return 0

    async def append_audit_log(self, log_id: str, event_type: str, topic: str, payload: Any, timestamp: Optional[int] = None):
        ts = timestamp or int(time.time() * 1000)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO audit_stream (id, event_type, topic, payload_json, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (log_id, event_type, topic, json.dumps(payload), ts))
                await db.commit()
        except Exception as e:
            print(f"[RelationalLedger] Failed to write audit log: {e}")

    async def shutdown(self):
        self._is_running = False
        if self._flusher_task:
            self._flusher_task.cancel()
        await self.flush_batch()

db_ledger = RelationalLedger.get_instance()

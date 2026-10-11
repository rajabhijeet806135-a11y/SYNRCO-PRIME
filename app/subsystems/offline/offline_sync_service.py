import aiosqlite
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.config import settings
from app.subsystems.offline.replay_guard import replay_guard
from app.subsystems.settlement.settlement_worker import settlement_worker, VoteSubmission

class QueuedClientAction(BaseModel):
    client_event_id: str
    action_type: str  # 'PREDICTION_VOTE' | 'CHEER' | 'CLAN_CHAT'
    prediction_id: Optional[str] = None
    selected_option: Optional[str] = None
    stake_tokens: Optional[int] = 50
    queued_at_epoch_ms: int

class SyncBatchRequest(BaseModel):
    user_id: str
    match_id: str
    actions: List[QueuedClientAction]

class SyncBatchResponse(BaseModel):
    batch_size: int
    processed_count: int
    duplicate_count: int
    status: str

class OfflineSyncService:
    @staticmethod
    async def process_sync_batch(batch: SyncBatchRequest) -> SyncBatchResponse:
        now_ms = int(time.time() * 1000)
        processed = 0
        duplicates = 0

        for action in batch.actions:
            # 1. Check Replay Guard
            if not replay_guard.record_event(action.client_event_id):
                duplicates += 1
                continue

            # 2. Replay Action
            if action.action_type == "PREDICTION_VOTE" and action.prediction_id and action.selected_option:
                try:
                    await settlement_worker.submit_vote(
                        VoteSubmission(
                            user_id=batch.user_id,
                            prediction_id=action.prediction_id,
                            selected_option=action.selected_option,
                            stake_tokens=action.stake_tokens or 50,
                            client_event_id=action.client_event_id,
                            sybil_score=0.90,
                            reaction_speed_ms=max(200, now_ms - action.queued_at_epoch_ms)
                        )
                    )
                    processed += 1
                except Exception as e:
                    print(f"[OfflineSyncService] Failed to replay action {action.client_event_id}: {e}")
            else:
                processed += 1

        # 3. Log Sync Batch to DB
        async with aiosqlite.connect(settings.DB_FILE) as db:
            log_id = f"sync_{now_ms}_{batch.user_id}"
            await db.execute("""
                INSERT INTO offline_sync_logs (id, user_id, batch_size, success_count, replay_status, synced_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log_id,
                batch.user_id,
                len(batch.actions),
                processed,
                "SYNC_COMPLETE",
                now_ms
            ))
            await db.commit()

        return SyncBatchResponse(
            batch_size=len(batch.actions),
            processed_count=processed,
            duplicate_count=duplicates,
            status="SYNCED_SUCCESSFULLY"
        )

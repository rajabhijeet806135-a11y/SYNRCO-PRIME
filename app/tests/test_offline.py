import pytest
import time
from app.subsystems.offline.offline_sync_service import (
    OfflineSyncService,
    SyncBatchRequest,
    QueuedClientAction
)

@pytest.mark.asyncio
async def test_offline_batch_sync_and_deduplication():
    now_ms = int(time.time() * 1000)

    batch_request = SyncBatchRequest(
        user_id="usr_genz_7721",
        match_id="IND_AUS_T20_2026",
        actions=[
            QueuedClientAction(
                client_event_id=f"offline_evt_1_{now_ms}",
                action_type="CHEER",
                queued_at_epoch_ms=now_ms - 20000
            ),
            QueuedClientAction(
                client_event_id=f"offline_evt_2_{now_ms}",
                action_type="CHEER",
                queued_at_epoch_ms=now_ms - 15000
            ),
        ]
    )

    # 1. First sync -> Both processed
    res1 = await OfflineSyncService.process_sync_batch(batch_request)
    assert res1.batch_size == 2
    assert res1.processed_count == 2
    assert res1.duplicate_count == 0

    # 2. Replay duplicate sync -> Both rejected by Bloom filter Replay Guard!
    res2 = await OfflineSyncService.process_sync_batch(batch_request)
    assert res2.batch_size == 2
    assert res2.processed_count == 0
    assert res2.duplicate_count == 2

from fastapi import APIRouter
from app.subsystems.offline.offline_sync_service import (
    OfflineSyncService,
    SyncBatchRequest,
    SyncBatchResponse
)

router = APIRouter(prefix="/api/v1/offline", tags=["Offline & In-Stadium 5G Sync"])

@router.post("/sync", response_model=SyncBatchResponse)
async def sync_offline_actions(batch: SyncBatchRequest):
    return await OfflineSyncService.process_sync_batch(batch)

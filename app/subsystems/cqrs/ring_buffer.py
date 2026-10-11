import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.core.token_bucket import default_rate_limiter

class IngestItem(BaseModel):
    id: str
    key: str
    timestamp: float
    payload: Any

class RingBufferIngest:
    """
    Subsystem 4: High-Concurrency Ingestion with Ring Buffer & Token Bucket
    Absorbs thundering herds and mitigates DDOS / burst spikes
    """
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.buffer: List[Optional[IngestItem]] = [None] * capacity
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, key: str, payload: Any, cost: int = 1) -> Dict[str, Any]:
        # 1. Check Token-Bucket
        if not default_rate_limiter.check_limit(key, cost):
            return {"accepted": False, "queued": False, "reason": "RATE_LIMIT_EXCEEDED"}

        # 2. Ring buffer capacity check
        if self.count >= self.capacity:
            return {"accepted": False, "queued": False, "reason": "RING_BUFFER_FULL"}

        item = IngestItem(
            id=f"ring_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}",
            key=key,
            timestamp=time.time(),
            payload=payload
        )

        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        self.count += 1

        return {"accepted": True, "queued": True, "id": item.id}

    def drain(self, max_items: int = 500) -> List[IngestItem]:
        items = []
        drain_count = min(max_items, self.count)
        for _ in range(drain_count):
            item = self.buffer[self.head]
            if item is not None:
                items.append(item)
                self.buffer[self.head] = None
            self.head = (self.head + 1) % self.capacity
            self.count -= 1
        return items

    def pending_count(self) -> int:
        return self.count

edge_ingest_ring_buffer = RingBufferIngest()

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    match_id: str
    frame_idx: Optional[int] = None

class TTLBoundedCache:
    """
    Subsystem 3 Shared VLM & Telemetry TTL Cache
    Provides O(1) compute per match broadcast with 500ms TTL
    """
    def __init__(self, default_ttl_ms: int = 500):
        self.default_ttl_ms = default_ttl_ms
        self._cache: Dict[str, CacheEntry] = {}

    def set(self, key: str, value: Any, match_id: str, ttl_ms: Optional[int] = None, frame_idx: Optional[int] = None):
        ttl = ttl_ms if ttl_ms is not None else self.default_ttl_ms
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=time.time() + (ttl / 1000.0),
            match_id=match_id,
            frame_idx=frame_idx
        )

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.value

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)

shared_vlm_cache = TTLBoundedCache(default_ttl_ms=500)
shared_telemetry_cache = TTLBoundedCache(default_ttl_ms=200)

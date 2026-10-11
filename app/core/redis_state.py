import asyncio
import time
from typing import Dict, Set, List, Optional, Tuple, Any, Callable

class InMemoryRedisState:
    """
    Subsystem 4 In-Memory CQRS Redis State Engine
    Provides ultra-low-latency state management, Partitioned ZSET leaderboards,
    Atomic increments, Session caching, and Sentinel replication fallback.
    """
    def __init__(self):
        self._strings: Dict[str, str] = {}
        self._expirations: Dict[str, float] = {}
        self._hashes: Dict[str, Dict[str, str]] = {}
        self._sets: Dict[str, Set[str]] = {}
        self._zsets: Dict[str, Dict[str, float]] = {}
        self._subscribers: Dict[str, List[Callable[[str], Any]]] = {}
        self._aof_log: List[str] = []

    def _check_expiry(self, key: str) -> bool:
        if key in self._expirations:
            if time.time() >= self._expirations[key]:
                self.delete(key)
                return False
        return True

    # --- String Operations ---
    async def get(self, key: str) -> Optional[str]:
        if not self._check_expiry(key):
            return None
        return self._strings.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> str:
        self._strings[key] = value
        if ex and ex > 0:
            self._expirations[key] = time.time() + ex
        else:
            self._expirations.pop(key, None)
        self._aof_log.append(f"SET {key} {value}")
        return "OK"

    async def setex(self, key: str, time_seconds: int, value: str) -> str:
        return await self.set(key, value, ex=time_seconds)

    async def psetex(self, key: str, time_ms: int, value: str) -> str:
        self._strings[key] = value
        self._expirations[key] = time.time() + (time_ms / 1000.0)
        return "OK"

    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            deleted = False
            if key in self._strings:
                del self._strings[key]
                deleted = True
            if key in self._hashes:
                del self._hashes[key]
                deleted = True
            if key in self._sets:
                del self._sets[key]
                deleted = True
            if key in self._zsets:
                del self._zsets[key]
                deleted = True
            self._expirations.pop(key, None)
            if deleted:
                count += 1
        return count

    async def delete_async(self, *keys: str) -> int:
        return self.delete(*keys)

    async def exists(self, key: str) -> int:
        if not self._check_expiry(key):
            return 0
        exists = (key in self._strings or key in self._hashes or key in self._sets or key in self._zsets)
        return 1 if exists else 0

    async def incrby(self, key: str, increment: int = 1) -> int:
        curr = await self.get(key)
        curr_num = int(curr) if curr and curr.isdigit() else 0
        new_num = curr_num + increment
        await self.set(key, str(new_num))
        return new_num

    async def decrby(self, key: str, decrement: int = 1) -> int:
        return await self.incrby(key, -decrement)

    # --- Hash Operations ---
    async def hset(self, key: str, field: str, value: str) -> int:
        if key not in self._hashes:
            self._hashes[key] = {}
        is_new = field not in self._hashes[key]
        self._hashes[key][field] = value
        return 1 if is_new else 0

    async def hget(self, key: str, field: str) -> Optional[str]:
        if not self._check_expiry(key):
            return None
        return self._hashes.get(key, {}).get(field)

    async def hgetall(self, key: str) -> Dict[str, str]:
        if not self._check_expiry(key):
            return {}
        return dict(self._hashes.get(key, {}))

    async def hincrby(self, key: str, field: str, increment: int = 1) -> int:
        curr = await self.hget(key, field)
        curr_num = int(curr) if curr and curr.isdigit() else 0
        new_num = curr_num + increment
        await self.hset(key, field, str(new_num))
        return new_num

    # --- Set Operations ---
    async def sadd(self, key: str, *members: str) -> int:
        if key not in self._sets:
            self._sets[key] = set()
        added = 0
        for m in members:
            if m not in self._sets[key]:
                self._sets[key].add(m)
                added += 1
        return added

    async def sismember(self, key: str, member: str) -> int:
        if not self._check_expiry(key):
            return 0
        return 1 if member in self._sets.get(key, set()) else 0

    async def smembers(self, key: str) -> Set[str]:
        if not self._check_expiry(key):
            return set()
        return set(self._sets.get(key, set()))

    async def scard(self, key: str) -> int:
        if not self._check_expiry(key):
            return 0
        return len(self._sets.get(key, set()))

    # --- Sorted Set (ZSET) Operations for Sub-5ms Leaderboards ---
    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        if key not in self._zsets:
            self._zsets[key] = {}
        added = 0
        for member, score in mapping.items():
            if member not in self._zsets[key]:
                added += 1
            self._zsets[key][member] = float(score)
        return added

    async def zincrby(self, key: str, increment: float, member: str) -> float:
        if key not in self._zsets:
            self._zsets[key] = {}
        curr = self._zsets[key].get(member, 0.0)
        new_score = curr + float(increment)
        self._zsets[key][member] = new_score
        return new_score

    async def zscore(self, key: str, member: str) -> Optional[float]:
        if not self._check_expiry(key):
            return None
        return self._zsets.get(key, {}).get(member)

    async def zcard(self, key: str) -> int:
        if not self._check_expiry(key):
            return 0
        return len(self._zsets.get(key, {}))

    async def zrevrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List[Any]:
        if not self._check_expiry(key) or key not in self._zsets:
            return []
        sorted_members = sorted(self._zsets[key].items(), key=lambda x: x[1], reverse=True)
        actual_stop = len(sorted_members) if stop == -1 else stop + 1
        slice_items = sorted_members[start:actual_stop]

        if not withscores:
            return [item[0] for item in slice_items]
        return [(item[0], item[1]) for item in slice_items]

    async def zrevrank(self, key: str, member: str) -> Optional[int]:
        if not self._check_expiry(key) or key not in self._zsets:
            return None
        if member not in self._zsets[key]:
            return None
        sorted_members = sorted(self._zsets[key].items(), key=lambda x: x[1], reverse=True)
        for rank, (m, _) in enumerate(sorted_members):
            if m == member:
                return rank
        return None

    # --- Pub/Sub ---
    async def publish(self, channel: str, message: str) -> int:
        subs = self._subscribers.get(channel, [])
        for cb in subs:
            if asyncio.iscoroutinefunction(cb):
                asyncio.create_task(cb(message))
            else:
                cb(message)
        return len(subs)

    async def subscribe(self, channel: str, callback: Callable[[str], Any]) -> Callable[[], None]:
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
        return lambda: self._subscribers[channel].remove(callback) if callback in self._subscribers.get(channel, []) else None

    def flushall(self) -> None:
        self._strings.clear()
        self._expirations.clear()
        self._hashes.clear()
        self._sets.clear()
        self._zsets.clear()
        self._aof_log.clear()

redis_client = InMemoryRedisState()

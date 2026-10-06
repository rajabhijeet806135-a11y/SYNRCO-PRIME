import time
from typing import Dict, Optional

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

    def consume(self, count: int = 1) -> bool:
        self._refill()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    def available_tokens(self) -> int:
        self._refill()
        return int(self.tokens)

class RateLimiterManager:
    def __init__(self, default_capacity: int = 100, default_refill_rate: float = 20.0):
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate
        self.buckets: Dict[str, TokenBucket] = {}

    def check_limit(self, key: str, cost: int = 1, capacity: Optional[int] = None, refill_rate: Optional[float] = None) -> bool:
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(
                capacity=capacity or self.default_capacity,
                refill_rate_per_sec=refill_rate or self.default_refill_rate
            )
        return self.buckets[key].consume(cost)

    def get_bucket(self, key: str) -> Optional[TokenBucket]:
        return self.buckets.get(key)

default_rate_limiter = RateLimiterManager()

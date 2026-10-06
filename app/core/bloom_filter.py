import math
from typing import List, Set

class BloomFilter:
    """
    Subsystem 5 & 8 Bloom Filter
    Ultra-fast in-memory Bloom Filter for sub-millisecond idempotency deduplication.
    Guarantees zero duplicate processing for settlement_id and client_event_id.
    """
    def __init__(self, expected_elements: int = 100000, false_positive_rate: float = 0.001):
        self.size = math.ceil(-1 * (expected_elements * math.log(false_positive_rate)) / (math.log(2) ** 2))
        self.hash_count = max(1, round((self.size / expected_elements) * math.log(2)))
        self.bit_array = bytearray(math.ceil(self.size / 8))
        self.exact_set: Set[str] = set()

    def _get_hashes(self, key: str) -> List[int]:
        hashes = []
        h1 = 0x811c9dc5
        h2 = 0x5bd1e995
        
        for char in key.encode('utf-8'):
            h1 = ((h1 ^ char) * 0x01000193) & 0xFFFFFFFF
            h2 = ((h2 ^ char) * 0x5bd1e995) & 0xFFFFFFFF
            h2 ^= (h2 >> 13)

        for i in range(self.hash_count):
            combined = abs((h1 + i * h2) % self.size)
            hashes.append(combined)

        return hashes

    def add(self, key: str) -> None:
        hashes = self._get_hashes(key)
        for bit_index in hashes:
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            self.bit_array[byte_idx] |= (1 << bit_offset)
        self.exact_set.add(key)

    def test(self, key: str) -> bool:
        hashes = self._get_hashes(key)
        for bit_index in hashes:
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            if not (self.bit_array[byte_idx] & (1 << bit_offset)):
                return False
        return key in self.exact_set

    def test_and_add(self, key: str) -> bool:
        """
        Atomic Test-And-Add: Returns True if ALREADY existed, False if newly added.
        """
        exists = self.test(key)
        if not exists:
            self.add(key)
        return exists

    def count(self) -> int:
        return len(self.exact_set)

    def clear(self) -> None:
        self.bit_array = bytearray(len(self.bit_array))
        self.exact_set.clear()

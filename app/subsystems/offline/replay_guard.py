from app.core.bloom_filter import BloomFilter

class ReplayGuard:
    """
    Subsystem 8: Idempotent Replay Guard (Flaw 6 Fix)
    Ensures that reconnected PWA clients syncing offline queues never double-count actions
    """
    _instance = None

    def __init__(self):
        self.bloom_filter = BloomFilter(expected_elements=500000)

    @classmethod
    def get_instance(cls) -> 'ReplayGuard':
        if cls._instance is None:
            cls._instance = ReplayGuard()
        return cls._instance

    def is_duplicate(self, client_event_id: str) -> bool:
        return self.bloom_filter.test(client_event_id)

    def record_event(self, client_event_id: str) -> bool:
        """
        Returns True if newly recorded, False if already processed
        """
        return not self.bloom_filter.test_and_add(client_event_id)

replay_guard = ReplayGuard.get_instance()

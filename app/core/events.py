import asyncio
import time
from typing import Callable, Dict, List, Any, Optional, Awaitable
from dataclasses import dataclass, field

class Topics:
    # Telemetry Ingestion
    TELEMETRY_RAW = "telemetry.raw"
    TELEMETRY_PROCESSED = "telemetry.processed"
    
    # Shared VLM Inference & Context
    VLM_INFERENCE_REQUEST = "vlm.inference.request"
    VLM_INFERENCE_RESULT = "vlm.inference.result"
    CONTEXTUAL_EVENT = "events.contextual"
    DEAD_TIME_DETECTED = "events.dead_time"
    HIGHLIGHT_GENERATED = "events.highlight"
    
    # Predictions & Settlement
    PREDICTION_CREATED = "predictions.created"
    PREDICTION_LOCKED = "predictions.locked"
    PREDICTION_CLOSED = "predictions.closed"
    PREDICTION_SETTLED = "predictions.settled"
    PREDICTION_VOTE_SUBMITTED = "predictions.vote_submitted"
    
    # Crowd & Decibels
    CROWD_CHEER = "crowd.cheer"
    CROWD_DECIBEL_UPDATE = "crowd.decibel_update"
    HAPTIC_TRIGGER = "crowd.haptic_trigger"
    
    # Clans & Communities
    CLAN_POINTS_AWARDED = "clans.points_awarded"
    CLAN_WAR_UPDATE = "clans.war_update"
    CLAN_MESSAGE = "clans.message"
    
    # Security, Sybil & Bot Defense
    SYBIL_FLAGGED = "sybil.flagged"
    PROOF_OF_WATCH_CHALLENGE = "sybil.proof_challenge"
    
    # Offline & Synchronization
    OFFLINE_SYNC_BATCH = "offline.sync_batch"
    
    # Leaderboards & CQRS
    LEADERBOARD_UPDATED = "leaderboard.updated"
    AUDIT_LOG_ENTRY = "audit.log_entry"

@dataclass
class EventEnvelope:
    id: str
    topic: str
    timestamp: float
    source: str
    payload: Any
    correlation_id: Optional[str] = None

EventHandler = Callable[[EventEnvelope], Awaitable[None]]

class AsyncEventBus:
    _instance: Optional['AsyncEventBus'] = None

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._wildcard_subscribers: List[EventHandler] = []
        self._counters: Dict[str, int] = {}
        self._is_running = True

    @classmethod
    def get_instance(cls) -> 'AsyncEventBus':
        if cls._instance is None:
            cls._instance = AsyncEventBus()
        return cls._instance

    async def publish(self, topic: str, payload: Any, source: str = "system", correlation_id: Optional[str] = None) -> EventEnvelope:
        envelope = EventEnvelope(
            id=f"evt_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}",
            topic=topic,
            timestamp=time.time(),
            source=source,
            payload=payload,
            correlation_id=correlation_id
        )

        self._counters[topic] = self._counters.get(topic, 0) + 1

        handlers = list(self._subscribers.get(topic, []))
        wildcards = list(self._wildcard_subscribers)

        # Non-blocking async dispatch
        asyncio.create_task(self._dispatch(handlers, wildcards, envelope))
        return envelope

    async def _dispatch(self, handlers: List[EventHandler], wildcards: List[EventHandler], envelope: EventEnvelope):
        for handler in handlers:
            try:
                await handler(envelope)
            except Exception as e:
                print(f"[AsyncEventBus] Handler error on topic {envelope.topic}: {e}")

        for handler in wildcards:
            try:
                await handler(envelope)
            except Exception as e:
                print(f"[AsyncEventBus] Wildcard handler error: {e}")

    def subscribe(self, topic: str, handler: EventHandler) -> Callable[[], None]:
        if topic == "*":
            self._wildcard_subscribers.append(handler)
            return lambda: self._wildcard_subscribers.remove(handler) if handler in self._wildcard_subscribers else None

        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

        return lambda: self._subscribers[topic].remove(handler) if handler in self._subscribers.get(topic, []) else None

    def get_metrics(self) -> Dict[str, int]:
        return dict(self._counters)

    def reset_metrics(self) -> None:
        self._counters.clear()

event_bus = AsyncEventBus.get_instance()

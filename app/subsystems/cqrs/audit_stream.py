import aiosqlite
import json
import time
from typing import Dict, Any, List, Optional
from app.config import settings
from app.core.database import db_ledger
from app.core.events import event_bus, EventEnvelope

class AuditStream:
    _instance: Optional['AuditStream'] = None

    def __init__(self):
        self._subscribe_all()

    @classmethod
    def get_instance(cls) -> 'AuditStream':
        if cls._instance is None:
            cls._instance = AuditStream()
        return cls._instance

    def _subscribe_all(self):
        event_bus.subscribe("*", self._handle_event)

    async def _handle_event(self, envelope: EventEnvelope):
        await self.log_event(
            topic=envelope.topic,
            event_type=envelope.source,
            payload=envelope.payload
        )

    async def log_event(self, topic: str, event_type: str, payload: Any):
        log_id = f"audit_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
        await db_ledger.append_audit_log(
            log_id=log_id,
            event_type=event_type,
            topic=topic,
            payload=payload,
            timestamp=int(time.time() * 1000)
        )

    async def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM audit_stream ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "eventType": r["event_type"],
                    "topic": r["topic"],
                    "payload": json.loads(r["payload_json"]),
                    "timestamp": r["timestamp"]
                }
                for r in rows
            ]

audit_stream = AuditStream.get_instance()

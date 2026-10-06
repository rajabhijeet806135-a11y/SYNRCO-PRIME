import json
from fastapi import WebSocket
from typing import Dict, Set, Any, Optional
from app.core.events import event_bus, EventEnvelope, Topics
from app.subsystems.persona.persona_router import PersonaRouter

class ConnectionManager:
    _instance: Optional['ConnectionManager'] = None

    def __init__(self):
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {}
        self._subscribe_event_bus()

    @classmethod
    def get_instance(cls) -> 'ConnectionManager':
        if cls._instance is None:
            cls._instance = ConnectionManager()
        return cls._instance

    async def connect(self, websocket: WebSocket, metadata: Optional[Dict[str, Any]] = None):
        await websocket.accept()
        self.active_connections[websocket] = metadata or {
            "userId": "anonymous",
            "persona": "CASUAL",
            "channels": set()
        }

    def disconnect(self, websocket: WebSocket):
        meta = self.active_connections.pop(websocket, None)
        if meta and "channels" in meta:
            for ch in meta["channels"]:
                if ch in self.channel_subscriptions:
                    self.channel_subscriptions[ch].discard(websocket)

    def subscribe_channel(self, websocket: WebSocket, channel: str):
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)

        if websocket in self.active_connections:
            if "channels" not in self.active_connections[websocket]:
                self.active_connections[websocket]["channels"] = set()
            self.active_connections[websocket]["channels"].add(channel)

    def unsubscribe_channel(self, websocket: WebSocket, channel: str):
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
        if websocket in self.active_connections and "channels" in self.active_connections[websocket]:
            self.active_connections[websocket]["channels"].discard(channel)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        subscribers = list(self.channel_subscriptions.get(channel, set()))
        if not subscribers:
            return

        text = json.dumps(message)
        for ws in subscribers:
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(ws)

    def _subscribe_event_bus(self):
        event_bus.subscribe("*", self._fanout_event)

    async def _fanout_event(self, envelope: EventEnvelope):
        topic = envelope.topic
        payload = envelope.payload

        if topic == Topics.TELEMETRY_PROCESSED:
            match_id = payload.get("matchId") or payload.get("match_id")
            if match_id:
                await self.broadcast_to_channel(f"telemetry:{match_id}", {
                    "type": "TELEMETRY_UPDATE",
                    "data": payload
                })

        elif topic == Topics.CONTEXTUAL_EVENT:
            match_id = payload.get("match_id")
            if match_id:
                # Fan out to standard predictions & custom persona channels
                await self.broadcast_to_channel(f"predictions:{match_id}", {
                    "type": "CONTEXTUAL_EVENT",
                    "data": payload
                })

        elif topic == Topics.CROWD_DECIBEL_UPDATE:
            match_id = payload.get("match_id")
            if match_id:
                await self.broadcast_to_channel(f"crowd:{match_id}", {
                    "type": "CROWD_DECIBELS",
                    "data": payload
                })

        elif topic == Topics.LEADERBOARD_UPDATED:
            match_id = payload.get("matchId")
            if match_id:
                await self.broadcast_to_channel(f"leaderboard:{match_id}", {
                    "type": "LEADERBOARD_UPDATE",
                    "data": payload
                })

        elif topic == Topics.CLAN_MESSAGE:
            clan_id = payload.get("clan_id")
            if clan_id:
                await self.broadcast_to_channel(f"clan:{clan_id}", {
                    "type": "CLAN_CHAT",
                    "data": payload
                })

ws_manager = ConnectionManager.get_instance()

import json
import time
from fastapi import WebSocket, WebSocketDisconnect
from app.api.ws.connection_manager import ws_manager
from app.subsystems.auth.jwt_manager import JwtManager
from app.subsystems.persona.persona_engine import PersonaEngine
from app.subsystems.crowd.decibel_engine import crowd_decibel_engine
from app.subsystems.settlement.settlement_worker import settlement_worker, VoteSubmission

async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                msg = json.loads(text)
            except Exception:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                continue

            action = msg.get("action")

            if action == "AUTH":
                token = msg.get("token")
                if token:
                    payload = JwtManager.verify_access_token(token)
                    if payload:
                        ws_manager.active_connections[websocket]["userId"] = payload.get("userId")
                        ws_manager.active_connections[websocket]["persona"] = payload.get("persona")
                        ws_manager.active_connections[websocket]["clanId"] = payload.get("clanId")
                        await websocket.send_text(json.dumps({
                            "type": "AUTH_SUCCESS",
                            "user": payload
                        }))
                    else:
                        await websocket.send_text(json.dumps({"type": "AUTH_ERROR", "message": "Invalid token"}))

            elif action == "SUBSCRIBE":
                channel = msg.get("channel")
                if channel:
                    ws_manager.subscribe_channel(websocket, channel)
                    await websocket.send_text(json.dumps({
                        "type": "SUBSCRIBED",
                        "channel": channel
                    }))

            elif action == "UNSUBSCRIBE":
                channel = msg.get("channel")
                if channel:
                    ws_manager.unsubscribe_channel(websocket, channel)
                    await websocket.send_text(json.dumps({
                        "type": "UNSUBSCRIBED",
                        "channel": channel
                    }))

            elif action == "CHEER":
                match_id = msg.get("matchId")
                user_id = ws_manager.active_connections.get(websocket, {}).get("userId", "anonymous")
                if match_id:
                    snapshot = await crowd_decibel_engine.record_cheer(match_id, user_id, intensity=msg.get("intensity", 1.0))
                    await websocket.send_text(json.dumps({
                        "type": "CHEER_ACK",
                        "snapshot": snapshot.model_dump() if hasattr(snapshot, 'model_dump') else snapshot.dict()
                    }))

            elif action == "VOTE":
                user_id = ws_manager.active_connections.get(websocket, {}).get("userId", "anonymous")
                vote = VoteSubmission(
                    user_id=user_id,
                    prediction_id=msg.get("predictionId", ""),
                    selected_option=msg.get("selectedOption", ""),
                    stake_tokens=msg.get("stakeTokens", 50),
                    client_event_id=msg.get("clientEventId", f"evt_{int(time.time()*1000)}"),
                    clan_id=ws_manager.active_connections.get(websocket, {}).get("clanId")
                )
                res = await settlement_worker.submit_vote(vote)
                await websocket.send_text(json.dumps({
                    "type": "VOTE_RESULT",
                    "result": res
                }))

            elif action == "SWITCH_PERSONA":
                new_persona = msg.get("persona")
                user_id = ws_manager.active_connections.get(websocket, {}).get("userId")
                if user_id and new_persona:
                    await PersonaEngine.manual_override_persona(user_id, new_persona)
                    ws_manager.active_connections[websocket]["persona"] = new_persona
                    await websocket.send_text(json.dumps({
                        "type": "PERSONA_SWITCHED",
                        "newPersona": new_persona
                    }))

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Handler error: {e}")
        ws_manager.disconnect(websocket)

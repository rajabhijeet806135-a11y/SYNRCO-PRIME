import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import db_ledger
from app.datasets.seed_data import seed_database
from app.simulator.match_simulator import match_simulator
from app.api.ws.ws_handler import websocket_endpoint

# Import Routers
from app.api.routers.auth_router import router as auth_router
from app.api.routers.persona_router import router as persona_router
from app.api.routers.telemetry_router import router as telemetry_router
from app.api.routers.prediction_router import router as prediction_router
from app.api.routers.leaderboard_router import router as leaderboard_router
from app.api.routers.broadcaster_router import router as broadcaster_router
from app.api.routers.offline_router import router as offline_router
from app.api.routers.clan_router import router as clan_router
from app.api.routers.match_router import router as match_router
from app.api.routers.historical_router import router as historical_router
from app.api.routers.camera_router import router as camera_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    print("[SYNCRO PRIME] Initializing high-concurrency backend architecture...")
    await db_ledger.initialize()
    await seed_database()
    match_simulator.start()
    print("[SYNCRO PRIME] All subsystems online & live simulation running.")
    yield
    # Shutdown:
    print("[SYNCRO PRIME] Shutting down...")
    match_simulator.stop()
    await db_ledger.shutdown()

app = FastAPI(
    title="SYNCRO PRIME: AI-Powered Sports Fan Companion Backend",
    description="Ultra-Low-Latency, High-Concurrency AI Backend supporting 6 Personas, Multi-Sport Telemetry, and Real-Time Settlement",
    version="2.4.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router)
app.include_router(persona_router)
app.include_router(telemetry_router)
app.include_router(prediction_router)
app.include_router(leaderboard_router)
app.include_router(broadcaster_router)
app.include_router(offline_router)
app.include_router(clan_router)
app.include_router(match_router)
app.include_router(historical_router)
app.include_router(camera_router)

# WebSocket Real-Time Gateway
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)

@app.get("/health", tags=["Health & Status"])
async def health_check():
    return {
        "status": "HEALTHY",
        "service": "syncro-prime-backend",
        "version": "2.4.0",
        "timestamp": int(time.time() * 1000),
        "supportedSports": settings.SPORTS,
        "supportedPersonas": settings.PERSONAS,
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "title": "SYNCRO PRIME Backend API",
        "docs": "/docs",
        "status": "ONLINE",
        "engine": "FastAPI + Asyncio + CQRS Memory Bus"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

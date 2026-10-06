import aiosqlite
import json
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.config import settings, SportType
from app.core.events import event_bus, Topics

class PredictionModel(BaseModel):
    id: str
    match_id: str
    sport: SportType
    title: str
    question: str
    options: List[str]
    correct_option: Optional[str] = None
    status: str = "OPEN"  # 'OPEN' | 'LOCKED' | 'CLOSED' | 'SETTLED'
    window_seconds: int = 30
    odds: Dict[str, float]
    created_at: int
    closed_at: Optional[int] = None
    settled_at: Optional[int] = None

class PredictionManager:
    _instance: Optional['PredictionManager'] = None

    @classmethod
    def get_instance(cls) -> 'PredictionManager':
        if cls._instance is None:
            cls._instance = PredictionManager()
        return cls._instance

    async def create_prediction(
        self,
        match_id: str,
        sport: SportType,
        title: str,
        question: str,
        options: List[str],
        window_seconds: int = 30,
        odds: Optional[Dict[str, float]] = None,
        correct_option: Optional[str] = None
    ) -> PredictionModel:
        now = int(time.time() * 1000)
        pred_id = f"pred_{int(time.time())}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
        calculated_odds = odds or {opt: 2.0 for opt in options}

        pred = PredictionModel(
            id=pred_id,
            match_id=match_id,
            sport=sport,
            title=title,
            question=question,
            options=options,
            correct_option=correct_option,
            status="OPEN",
            window_seconds=window_seconds,
            odds=calculated_odds,
            created_at=now
        )

        async with aiosqlite.connect(settings.DB_FILE) as db:
            await db.execute("""
                INSERT INTO predictions (
                    id, match_id, sport, title, question, options_json, correct_option,
                    status, window_seconds, odds_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pred.id,
                pred.match_id,
                pred.sport,
                pred.title,
                pred.question,
                json.dumps(pred.options),
                pred.correct_option,
                pred.status,
                pred.window_seconds,
                json.dumps(pred.odds),
                pred.created_at
            ))
            await db.commit()

        dumped = pred.model_dump() if hasattr(pred, 'model_dump') else pred.dict()
        await event_bus.publish(Topics.PREDICTION_CREATED, dumped, source="prediction_manager")
        return pred

    async def get_active_predictions(self, match_id: str) -> List[PredictionModel]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM predictions WHERE match_id = ? AND status IN ('OPEN', 'LOCKED') ORDER BY created_at DESC",
                (match_id,)
            )
            rows = await cursor.fetchall()
            return [
                PredictionModel(
                    id=r["id"],
                    match_id=r["match_id"],
                    sport=r["sport"],
                    title=r["title"],
                    question=r["question"],
                    options=json.loads(r["options_json"]),
                    correct_option=r["correct_option"],
                    status=r["status"],
                    window_seconds=r["window_seconds"],
                    odds=json.loads(r["odds_json"]),
                    created_at=r["created_at"],
                    closed_at=r["closed_at"],
                    settled_at=r["settled_at"]
                )
                for r in rows
            ]

    async def get_prediction(self, prediction_id: str) -> Optional[PredictionModel]:
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
            r = await cursor.fetchone()
            if not r:
                return None
            return PredictionModel(
                id=r["id"],
                match_id=r["match_id"],
                sport=r["sport"],
                title=r["title"],
                question=r["question"],
                options=json.loads(r["options_json"]),
                correct_option=r["correct_option"],
                status=r["status"],
                window_seconds=r["window_seconds"],
                odds=json.loads(r["odds_json"]),
                created_at=r["created_at"],
                closed_at=r["closed_at"],
                settled_at=r["settled_at"]
            )

prediction_manager = PredictionManager.get_instance()

import aiosqlite
import json
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.config import settings
from app.core.bloom_filter import BloomFilter
from app.core.redis_state import redis_client
from app.core.database import db_ledger, BatchLedgerItem
from app.core.events import event_bus, Topics
from app.subsystems.settlement.reward_ledger import RewardLedger
from app.subsystems.cqrs.cqrs_engine import cqrs_state_engine

class VoteSubmission(BaseModel):
    user_id: str
    prediction_id: str
    selected_option: str
    stake_tokens: int = 50
    client_event_id: str
    sybil_score: float = 1.0
    clan_id: Optional[str] = None
    reaction_speed_ms: Optional[int] = 2500

class SettlementResult(BaseModel):
    settlement_id: str
    prediction_id: str
    correct_option: str
    winners_count: int
    total_tokens_distributed: int
    total_xp_distributed: int
    settlement_duration_ms: int

class SettlementWorker:
    """
    Subsystem 5: Real-Time Prediction Settlement Engine (Flaw 7 Fix)
    Decoupled two-phase settlement:
    - Phase 1: Instant UX settlement via Redis (<100ms SLA target)
    - Phase 2: Async durable write to SQLite/PostgreSQL (1000ms cycle)
    - Bloom filter idempotency guard prevents double payouts
    """
    _instance: Optional['SettlementWorker'] = None

    def __init__(self):
        self.bloom_filter = BloomFilter(expected_elements=200000)
        self.client_event_bloom = BloomFilter(expected_elements=500000)

    @classmethod
    def get_instance(cls) -> 'SettlementWorker':
        if cls._instance is None:
            cls._instance = SettlementWorker()
        return cls._instance

    async def submit_vote(self, vote: VoteSubmission) -> Dict[str, Any]:
        # 1. Idempotency Check via Bloom Filter on client_event_id
        if self.client_event_bloom.test_and_add(vote.client_event_id):
            return {
                "accepted": False,
                "reason": "DUPLICATE_CLIENT_EVENT_ID",
                "client_event_id": vote.client_event_id
            }

        now = int(time.time() * 1000)
        async with aiosqlite.connect(settings.DB_FILE) as db:
            vote_id = f"v_{int(time.time()*1000)}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
            await db.execute("""
                INSERT INTO user_predictions (
                    id, prediction_id, user_id, selected_option, stake_tokens,
                    points_won, tokens_won, is_settled, client_event_id, sybil_score_at_vote, submitted_at
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?)
            """, (
                vote_id,
                vote.prediction_id,
                vote.user_id,
                vote.selected_option,
                vote.stake_tokens,
                vote.client_event_id,
                vote.sybil_score,
                now
            ))
            await db.commit()

        # Cache vote in Redis prediction pool set
        await redis_client.sadd(f"pred:{vote.prediction_id}:voters", vote.user_id)
        await redis_client.set(
            f"pred:{vote.prediction_id}:vote:{vote.user_id}",
            json.dumps({
                "option": vote.selected_option,
                "stake": vote.stake_tokens,
                "sybilScore": vote.sybil_score,
                "clanId": vote.clan_id
            }),
            ex=3600
        )

        dumped = vote.model_dump() if hasattr(vote, 'model_dump') else vote.dict()
        await event_bus.publish(Topics.PREDICTION_VOTE_SUBMITTED, dumped, source="settlement_worker")

        return {
            "accepted": True,
            "vote_id": vote_id,
            "prediction_id": vote.prediction_id,
            "selected_option": vote.selected_option,
            "stake_tokens": vote.stake_tokens
        }

    async def settle_prediction(self, prediction_id: str, correct_option: str) -> SettlementResult:
        start_time = time.time()
        settlement_id = f"stl_{prediction_id}"

        # Idempotency Guard: Ensure settlement runs exactly once per prediction
        if self.bloom_filter.test_and_add(f"settle_pred_{prediction_id}"):
            raise ValueError(f"Settlement for prediction {prediction_id} already processed!")

        # 1. Update prediction status in DB
        async with aiosqlite.connect(settings.DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
            pred = await cursor.fetchone()
            if not pred:
                raise ValueError(f"Prediction {prediction_id} not found")

            if pred["status"] == "SETTLED":
                raise ValueError(f"Prediction {prediction_id} is already settled!")

            odds = json.loads(pred["odds_json"])
            chosen_odd = odds.get(correct_option, 2.0)
            now = int(time.time() * 1000)

            await db.execute("""
                UPDATE predictions SET status = 'SETTLED', correct_option = ?, settled_at = ? WHERE id = ?
            """, (correct_option, now, prediction_id))

            # Fetch all user votes for this prediction
            cursor = await db.execute(
                "SELECT * FROM user_predictions WHERE prediction_id = ? AND is_settled = 0",
                (prediction_id,)
            )
            votes = await cursor.fetchall()
            await db.commit()

        winners_count = 0
        total_tokens = 0
        total_xp = 0

        # Phase 1: Fast Redis-first UX Settlement (<100ms)
        for v in votes:
            user_id = v["user_id"]
            selected_option = v["selected_option"]
            stake = v["stake_tokens"]
            sybil_score = v["sybil_score_at_vote"]

            if selected_option == correct_option:
                winners_count += 1
                streak_raw = await redis_client.get(f"user:{user_id}:streak")
                current_streak = (int(streak_raw) if streak_raw and streak_raw.isdigit() else 0) + 1
                multiplier = RewardLedger.calculate_streak_multiplier(current_streak)

                # Sybil reward gating
                reward_rate = 1.0
                if sybil_score < settings.SYBIL_SHADOW_LIMIT_THRESHOLD:
                    reward_rate = 0.0  # Bot flagged
                elif sybil_score < settings.SYBIL_FULL_REWARD_THRESHOLD:
                    reward_rate = 0.5  # Shadow limited

                tokens_won = int(stake * chosen_odd * multiplier * reward_rate)
                xp_won = int(100 * multiplier * reward_rate)

                total_tokens += tokens_won
                total_xp += xp_won

                # Atomic updates in Redis
                await redis_client.incrby(f"user:{user_id}:tokens", tokens_won)
                await redis_client.incrby(f"user:{user_id}:xp", xp_won)
                await redis_client.set(f"user:{user_id}:streak", str(current_streak))

                # Update live leaderboard
                await cqrs_state_engine.record_points(
                    match_id=pred["match_id"],
                    user_id=user_id,
                    points=float(xp_won)
                )

                # Phase 2: Queue for 1000ms async durability batch write
                db_ledger.queue_ledger_write(
                    BatchLedgerItem(
                        id=f"tx_{int(time.time()*1000)}_{user_id}",
                        settlement_id=settlement_id,
                        user_id=user_id,
                        match_id=pred["match_id"],
                        transaction_type="PREDICTION_WIN",
                        token_amount=tokens_won,
                        xp_amount=xp_won,
                        balance_after=tokens_won,
                        created_at=now
                    )
                )
            else:
                # Reset streak on loss
                await redis_client.set(f"user:{user_id}:streak", "0")

        duration_ms = int((time.time() - start_time) * 1000)

        result = SettlementResult(
            settlement_id=settlement_id,
            prediction_id=prediction_id,
            correct_option=correct_option,
            winners_count=winners_count,
            total_tokens_distributed=total_tokens,
            total_xp_distributed=total_xp,
            settlement_duration_ms=duration_ms
        )

        dumped = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        await event_bus.publish(Topics.PREDICTION_SETTLED, dumped, source="settlement_worker")

        return result

settlement_worker = SettlementWorker.get_instance()

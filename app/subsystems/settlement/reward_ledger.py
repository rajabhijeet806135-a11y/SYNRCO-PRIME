from typing import Dict, Any, Optional
from app.core.redis_state import redis_client

class RewardLedger:
    @staticmethod
    def calculate_streak_multiplier(streak: int) -> float:
        if streak >= 5:
            return 3.0
        elif streak >= 3:
            return 2.0
        elif streak >= 1:
            return 1.5
        return 1.0

    @staticmethod
    async def get_user_balance(user_id: str) -> Dict[str, Any]:
        tokens_raw = await redis_client.get(f"user:{user_id}:tokens")
        xp_raw = await redis_client.get(f"user:{user_id}:xp")
        streak_raw = await redis_client.get(f"user:{user_id}:streak")

        tokens = int(tokens_raw) if tokens_raw and tokens_raw.isdigit() else 250
        xp = int(xp_raw) if xp_raw and xp_raw.isdigit() else 0
        streak = int(streak_raw) if streak_raw and streak_raw.isdigit() else 0

        return {
            "userId": user_id,
            "syncTokens": tokens,
            "xpTotal": xp,
            "predictionStreak": streak,
            "streakMultiplier": RewardLedger.calculate_streak_multiplier(streak)
        }

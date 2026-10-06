import time
import random
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.core.redis_state import redis_client

class ProofChallenge(BaseModel):
    challenge_id: str
    user_id: str
    target_element: str
    timeout_seconds: int
    expected_response_token: str
    expires_at_ms: int

class ProofOfWatch:
    @staticmethod
    async def generate_challenge(user_id: str) -> ProofChallenge:
        now_ms = int(time.time() * 1000)
        challenge_id = f"pow_{int(time.time())}_{hex(int(time.time()*1000000) % 0xFFFFF)[2:]}"
        token = hex(random.getrandbits(64))[2:]
        expires_at = now_ms + 4000  # 4-second human reaction window

        challenge = ProofChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            target_element="FLASHING_BALL_TOP_RIGHT",
            timeout_seconds=4,
            expected_response_token=token,
            expires_at_ms=expires_at
        )

        await redis_client.set(f"challenge:{challenge_id}", token, ex=5)
        return challenge

    @staticmethod
    async def verify_challenge(challenge_id: str, submitted_token: str) -> bool:
        expected = await redis_client.get(f"challenge:{challenge_id}")
        if not expected:
            return False
        is_valid = (expected == submitted_token)
        if is_valid:
            await redis_client.delete_async(f"challenge:{challenge_id}")
        return is_valid

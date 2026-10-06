import os
from typing import List, Literal

class Config:
    NODE_ENV: str = os.getenv("NODE_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Security & JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "syncro_prime_ultra_secure_jwt_secret_key_2026_!@#$")
    JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "syncro_prime_refresh_token_secret_key_2026_!@#$")
    JWT_ACCESS_EXPIRY_MINUTES: int = 15
    JWT_REFRESH_EXPIRY_DAYS: int = 30
    GUEST_TOKEN_EXPIRY_HOURS: int = 24

    # Redis / In-Memory CQRS
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    REDIS_SENTINEL_ENABLED: bool = os.getenv("REDIS_SENTINEL_ENABLED", "false").lower() == "true"
    REDIS_FAILOVER_TIMEOUT_MS: int = 5000
    VLM_CACHE_TTL_MS: int = 500  # 500ms TTL per architecture spec
    TELEMETRY_CACHE_TTL_MS: int = 200

    # Settlement & Durability
    DB_FILE: str = os.getenv("DB_FILE", "./syncro_prime_ledger.sqlite")
    SETTLEMENT_BATCH_INTERVAL_MS: int = 1000  # 1000ms background DB batch cycle
    SETTLEMENT_SLA_TARGET_MS: int = 100  # Sub-100ms UX settlement target

    # Sybil & Bot Defense Thresholds
    SYBIL_FULL_REWARD_THRESHOLD: float = 0.75
    SYBIL_SHADOW_LIMIT_THRESHOLD: float = 0.40
    SYBIL_MIN_HUMAN_REACTION_MS: int = 150  # Sub-150ms is flagged as bot
    SYBIL_MAX_ACCOUNTS_PER_SUBNET: int = 5
    SYBIL_NEW_ACCOUNT_HOURS_GATE: int = 24
    SYBIL_NEW_ACCOUNT_REWARD_RATE: float = 0.10  # 10% rewards for unverified <24h accounts

    # Token Buckets Rate Limiting
    BURST_CAPACITY: int = 100
    REFILL_RATE_PER_SEC: int = 20
    WS_BURST_CAPACITY: int = 50
    WS_REFILL_RATE_PER_SEC: int = 10

    # Telemetry Ingestion
    TELEMETRY_FREQ_HZ: int = 25  # 25Hz - 50Hz optical tracking
    OFFLINE_TOLERANCE_SECONDS: int = 90

    # Supported Domains
    SPORTS: List[str] = ["FOOTBALL", "CRICKET", "BASKETBALL"]
    PERSONAS: List[str] = [
        "CASUAL",
        "GEN_Z",
        "HARDCORE",
        "CLUB_MEMBER",
        "STADIUM",
        "BROADCASTER"
    ]

settings = Config()

SportType = Literal["FOOTBALL", "CRICKET", "BASKETBALL"]
PersonaType = Literal["CASUAL", "GEN_Z", "HARDCORE", "CLUB_MEMBER", "STADIUM", "BROADCASTER"]

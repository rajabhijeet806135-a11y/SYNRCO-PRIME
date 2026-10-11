import aiosqlite
import json
import time
from app.config import settings
from app.core.redis_state import redis_client
from app.datasets.dataset3_gamification import SAMPLE_USERS
from app.datasets.dataset2_events import SAMPLE_CONTEXTUAL_EVENTS

async def seed_database():
    now = int(time.time() * 1000)
    async with aiosqlite.connect(settings.DB_FILE) as db:
        # 1. Seed Clans
        clans = [
            ("clan_mumbai_indians_elite", "Mumbai Paltan Elite", "MUM", "Official Mumbai Indians Global Fan Clan", "https://assets.syncroprime.io/clans/mum.png", 124500, 1420, now),
            ("clan_cityzens_global", "Cityzens Global", "MCI", "Manchester City Global Supporters Club", "https://assets.syncroprime.io/clans/mci.png", 98200, 980, now),
            ("clan_madridistas_ny", "Madridistas New York", "RMA", "Real Madrid Official NYC Fan Club", "https://assets.syncroprime.io/clans/rma.png", 110400, 1150, now),
            ("clan_lakers_nation", "Lakers Nation Worldwide", "LAL", "Los Angeles Lakers Championship Squad", "https://assets.syncroprime.io/clans/lal.png", 89300, 860, now),
        ]
        for c in clans:
            await db.execute("""
                INSERT OR IGNORE INTO clans (id, name, tag, description, avatar_url, total_points, member_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, c)

        # 2. Seed Users
        for user in SAMPLE_USERS:
            dumped = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
            scores_dump = user.persona_confidence_scores.model_dump() if hasattr(user.persona_confidence_scores, 'model_dump') else user.persona_confidence_scores.dict()
            await db.execute("""
                INSERT OR IGNORE INTO users (
                    id, email, username, password_hash, preferred_persona, persona_scores_json,
                    account_verification, sybil_trust_score, clan_id, xp_total, sync_tokens,
                    prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id,
                f"{user.username.lower()}@syncroprime.io",
                user.username,
                "$2a$10$SyncroPrimeHashPlaceHolder1234567890abcdef",
                user.preferred_persona,
                json.dumps(scores_dump),
                user.account_verification,
                user.sybil_trust_score,
                user.clan_id,
                user.gamification_state.xp_total,
                user.gamification_state.sync_tokens,
                user.gamification_state.prediction_streak,
                user.gamification_state.streak_multiplier,
                user.gamification_state.tier_badge,
                now - 86400000 * 10,
                now
            ))

            await redis_client.set(
                f"user:{user.user_id}:profile",
                json.dumps(dumped)
            )

        # 3. Seed Matches
        matches = [
            ("IND_AUS_T20_2026", "CRICKET", "India vs Australia - 3rd T20 International", "India (IND)", "Australia (AUS)", "LIVE", now - 3600000, json.dumps({"stadium": "Melbourne Cricket Ground"})),
            ("MCI_RMA_UCL_2026", "FOOTBALL", "Manchester City vs Real Madrid - UCL Semi-Final", "Manchester City (MCI)", "Real Madrid (RMA)", "LIVE", now - 1800000, json.dumps({"stadium": "Etihad Stadium"})),
            ("LAL_GSW_NBA_2026", "BASKETBALL", "Los Angeles Lakers vs Golden State Warriors - Game 7", "Los Angeles Lakers (LAL)", "Golden State Warriors (GSW)", "LIVE", now - 2700000, json.dumps({"arena": "Crypto.com Arena"}))
        ]
        for m in matches:
            await db.execute("""
                INSERT OR IGNORE INTO matches (id, sport, title, home_team, away_team, status, start_time, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, m)

        # 4. Seed Predictions
        for evt in SAMPLE_CONTEXTUAL_EVENTS:
            if evt.prediction_options and evt.odds:
                await db.execute("""
                    INSERT OR IGNORE INTO predictions (
                        id, match_id, sport, title, question, options_json, correct_option,
                        status, window_seconds, odds_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"pred_{evt.event_id}",
                    evt.match_id,
                    evt.sport,
                    evt.event_type.replace("_", " "),
                    evt.prompts_generated.genz,
                    json.dumps(evt.prediction_options),
                    evt.correct_option,
                    "OPEN",
                    evt.estimated_dead_time_seconds,
                    json.dumps(evt.odds),
                    now
                ))

        await db.commit()
    print("[SeedData] Python database and Redis state successfully initialized.")

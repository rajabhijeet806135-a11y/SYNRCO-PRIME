import { dbLedger } from '../core/database/db.js';
import { redisClient } from '../core/redis/redisClient.js';
import { SAMPLE_USERS } from './dataset3_gamification.js';
import { SAMPLE_CONTEXTUAL_EVENTS } from './dataset2_events.js';

export async function seedDatabase(): Promise<void> {
  const db = dbLedger.getRawDb();
  const now = Date.now();

  // 1. Seed Clans
  const insertClan = db.prepare(`
    INSERT OR IGNORE INTO clans (id, name, tag, description, avatar_url, total_points, member_count, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  insertClan.run(
    'clan_mumbai_indians_elite',
    'Mumbai Paltan Elite',
    'MUM',
    'Official Mumbai Indians Global Fan Clan',
    'https://assets.syncroprime.io/clans/mum.png',
    124500,
    1420,
    now
  );

  insertClan.run(
    'clan_cityzens_global',
    'Cityzens Global',
    'MCI',
    'Manchester City Global Supporters Club',
    'https://assets.syncroprime.io/clans/mci.png',
    98200,
    980,
    now
  );

  insertClan.run(
    'clan_madridistas_ny',
    'Madridistas New York',
    'RMA',
    'Real Madrid Official NYC Fan Club',
    'https://assets.syncroprime.io/clans/rma.png',
    110400,
    1150,
    now
  );

  insertClan.run(
    'clan_lakers_nation',
    'Lakers Nation Worldwide',
    'LAL',
    'Los Angeles Lakers Championship Squad',
    'https://assets.syncroprime.io/clans/lal.png',
    89300,
    860,
    now
  );

  // 2. Seed Users
  const insertUser = db.prepare(`
    INSERT OR IGNORE INTO users (
      id, email, username, password_hash, preferred_persona, persona_scores_json,
      account_verification, sybil_trust_score, clan_id, xp_total, sync_tokens,
      prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  for (const user of SAMPLE_USERS) {
    insertUser.run(
      user.user_id,
      `${user.username.toLowerCase()}@syncroprime.io`,
      user.username,
      '$2a$10$SyncroPrimeHashPlaceHolder1234567890abcdef', // Mock bcrypt hash
      user.preferred_persona,
      JSON.stringify(user.persona_confidence_scores),
      user.account_verification,
      user.sybil_trust_score,
      user.clan_id || null,
      user.gamification_state.xp_total,
      user.gamification_state.sync_tokens,
      user.gamification_state.prediction_streak,
      user.gamification_state.streak_multiplier,
      user.gamification_state.tier_badge,
      now - 86400000 * 10,
      now
    );

    // Also populate in Redis session / leaderboard
    await redisClient.set(
      `user:${user.user_id}:profile`,
      JSON.stringify(user)
    );
  }

  // 3. Seed Matches
  const insertMatch = db.prepare(`
    INSERT OR IGNORE INTO matches (id, sport, title, home_team, away_team, status, start_time, metadata_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  insertMatch.run(
    'IND_AUS_T20_2026',
    'CRICKET',
    'India vs Australia - 3rd T20 International',
    'India (IND)',
    'Australia (AUS)',
    'LIVE',
    now - 3600000,
    JSON.stringify({ stadium: 'Melbourne Cricket Ground', pitch_condition: 'Dry / Bouncy' })
  );

  insertMatch.run(
    'MCI_RMA_UCL_2026',
    'FOOTBALL',
    'Manchester City vs Real Madrid - UCL Semi-Final',
    'Manchester City (MCI)',
    'Real Madrid (RMA)',
    'LIVE',
    now - 1800000,
    JSON.stringify({ stadium: 'Etihad Stadium', weather: '14°C Light Rain' })
  );

  insertMatch.run(
    'LAL_GSW_NBA_2026',
    'BASKETBALL',
    'Los Angeles Lakers vs Golden State Warriors - Game 7',
    'Los Angeles Lakers (LAL)',
    'Golden State Warriors (GSW)',
    'LIVE',
    now - 2700000,
    JSON.stringify({ arena: 'Crypto.com Arena', quarter: 'Q4 0:04.8' })
  );

  // 4. Seed Predictions
  const insertPrediction = db.prepare(`
    INSERT OR IGNORE INTO predictions (
      id, match_id, sport, title, question, options_json, correct_option,
      status, window_seconds, odds_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  for (const evt of SAMPLE_CONTEXTUAL_EVENTS) {
    if (evt.prediction_options && evt.odds) {
      insertPrediction.run(
        `pred_${evt.event_id}`,
        evt.match_id,
        evt.sport,
        evt.event_type.replace(/_/g, ' '),
        evt.prompts_generated.genz,
        JSON.stringify(evt.prediction_options),
        evt.correct_option || null,
        'OPEN',
        evt.estimated_dead_time_seconds,
        JSON.stringify(evt.odds),
        now
      );
    }
  }

  console.log('[SeedData] Initial database and Redis state successfully seeded.');
}

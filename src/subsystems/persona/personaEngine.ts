import { redisClient } from '../../core/redis/redisClient.js';
import { dbLedger } from '../../core/database/db.js';
import { PersonaType } from '../../config/index.js';
import { PersonaConfidenceScores } from '../../datasets/dataset3_gamification.js';
import { BehavioralClassifier, UserSessionTelemetry } from './behavioralClassifier.js';
import { SessionStore } from '../auth/sessionStore.js';

export interface QuizAnswers {
  q1_viewing_style: 'quick_highlights' | 'deep_stats' | 'social_clan' | 'relaxed_fun';
  q2_sports_knowledge: 'beginner' | 'intermediate' | 'expert';
  q3_primary_device: 'mobile' | 'smart_tv' | 'in_stadium';
}

export class PersonaEngine {
  /**
   * Layer 1: Onboarding Quiz processor
   */
  public static processOnboardingQuiz(userId: string, answers: QuizAnswers): {
    recommendedPersona: PersonaType;
    confidenceScores: PersonaConfidenceScores;
  } {
    let casual = 0.2;
    let genz = 0.2;
    let hardcore = 0.2;
    let club = 0.2;
    let stadium = 0.0;

    // Q1 Analysis
    if (answers.q1_viewing_style === 'relaxed_fun') casual += 0.5;
    if (answers.q1_viewing_style === 'quick_highlights') genz += 0.5;
    if (answers.q1_viewing_style === 'deep_stats') hardcore += 0.5;
    if (answers.q1_viewing_style === 'social_clan') club += 0.5;

    // Q2 Analysis
    if (answers.q2_sports_knowledge === 'beginner') casual += 0.4;
    if (answers.q2_sports_knowledge === 'expert') hardcore += 0.4;

    // Q3 Analysis
    if (answers.q3_primary_device === 'mobile') genz += 0.2;
    if (answers.q3_primary_device === 'in_stadium') stadium = 0.9;

    const scores: PersonaConfidenceScores = {
      casual: parseFloat(casual.toFixed(2)),
      genz: parseFloat(genz.toFixed(2)),
      hardcore: parseFloat(hardcore.toFixed(2)),
      club_member: parseFloat(club.toFixed(2)),
      stadium: parseFloat(stadium.toFixed(2)),
    };

    // Determine top persona
    let maxScore = -1;
    let bestPersona: PersonaType = 'CASUAL';

    if (stadium > 0.8) {
      bestPersona = 'STADIUM';
    } else {
      if (scores.casual > maxScore) { maxScore = scores.casual; bestPersona = 'CASUAL'; }
      if (scores.genz > maxScore) { maxScore = scores.genz; bestPersona = 'GEN_Z'; }
      if (scores.hardcore > maxScore) { maxScore = scores.hardcore; bestPersona = 'HARDCORE'; }
      if (scores.club_member > maxScore) { maxScore = scores.club_member; bestPersona = 'CLUB_MEMBER'; }
    }

    return {
      recommendedPersona: bestPersona,
      confidenceScores: scores,
    };
  }

  /**
   * Layer 2: Behavioral Inference update (Run during match session)
   */
  public static async updateBehavioralPersona(
    userId: string,
    telemetry: UserSessionTelemetry
  ): Promise<PersonaConfidenceScores> {
    const db = dbLedger.getRawDb();
    const userRow = db.prepare(`SELECT persona_scores_json, preferred_persona FROM users WHERE id = ?`).get(userId) as any;

    const currentScores: PersonaConfidenceScores = userRow?.persona_scores_json
      ? JSON.parse(userRow.persona_scores_json)
      : { casual: 0.5, genz: 0.5, hardcore: 0.2, club_member: 0.2 };

    const updatedScores = BehavioralClassifier.classify(telemetry, currentScores);

    // Save to DB
    const updateStmt = db.prepare(`
      UPDATE users SET persona_scores_json = ?, updated_at = ? WHERE id = ?
    `);
    updateStmt.run(JSON.stringify(updatedScores), Date.now(), userId);

    // Cache in Redis for live session
    await redisClient.set(`user:${userId}:persona_scores`, JSON.stringify(updatedScores), 3600);

    return updatedScores;
  }

  /**
   * Layer 3: Manual Override (User toggles mode via profile without losing XP or tokens)
   */
  public static async manualOverridePersona(
    userId: string,
    newPersona: PersonaType,
    sessionId?: string
  ): Promise<{ success: boolean; activePersona: PersonaType }> {
    const db = dbLedger.getRawDb();
    const update = db.prepare(`
      UPDATE users SET preferred_persona = ?, updated_at = ? WHERE id = ?
    `);
    update.run(newPersona, Date.now(), userId);

    // Update Redis session if active
    if (sessionId) {
      await SessionStore.updateSessionPersona(sessionId, newPersona);
    }

    const activeSessionId = await redisClient.get(`user:${userId}:active_session`);
    if (activeSessionId) {
      await SessionStore.updateSessionPersona(activeSessionId, newPersona);
    }

    return {
      success: true,
      activePersona: newPersona,
    };
  }
}

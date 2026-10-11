import { PersonaConfidenceScores } from '../../datasets/dataset3_gamification.js';

export interface UserSessionTelemetry {
  statOverlayOpens: number;
  tacticalViewDurationSeconds: number;
  predictionReactionSpeedMs: number[];
  chatMessagesSent: number;
  emotesSent: number;
  clanLoungesVisited: number;
  plainEnglishHelpRequested: number;
  inStadium5GConnected: boolean;
  totalInteractions: number;
}

/**
 * High-performance behavioral inference classifier
 * Emulates the multi-dimensional XGBoost scoring weights (0.0 to 1.0)
 */
export class BehavioralClassifier {
  public static classify(telemetry: UserSessionTelemetry, currentScores: PersonaConfidenceScores): PersonaConfidenceScores {
    let casualWeight = currentScores.casual;
    let genzWeight = currentScores.genz;
    let hardcoreWeight = currentScores.hardcore;
    let clubWeight = currentScores.club_member;
    let stadiumWeight = currentScores.stadium || 0;

    // 1. Hardcore Signals: High stat overlay opens, high tactical view duration
    if (telemetry.statOverlayOpens > 5 || telemetry.tacticalViewDurationSeconds > 60) {
      hardcoreWeight = Math.min(1.0, hardcoreWeight + 0.25);
      casualWeight = Math.max(0.0, casualWeight - 0.15);
    }

    // 2. Gen-Z Signals: High emote volume, rapid prediction reactions (< 5000ms), fast interactions
    const avgReactionSpeed = telemetry.predictionReactionSpeedMs.length > 0
      ? telemetry.predictionReactionSpeedMs.reduce((a, b) => a + b, 0) / telemetry.predictionReactionSpeedMs.length
      : 8000;

    if (telemetry.emotesSent > 3 || (avgReactionSpeed < 4000 && avgReactionSpeed > 200)) {
      genzWeight = Math.min(1.0, genzWeight + 0.30);
    }

    // 3. Casual Signals: Low telemetry interactions, high plain-English help requests
    if (telemetry.plainEnglishHelpRequested > 2 || (telemetry.totalInteractions < 5 && telemetry.statOverlayOpens === 0)) {
      casualWeight = Math.min(1.0, casualWeight + 0.25);
      hardcoreWeight = Math.max(0.0, hardcoreWeight - 0.2);
    }

    // 4. Club Member Signals: Clan lounge visits, clan chat participation
    if (telemetry.clanLoungesVisited > 0 || telemetry.chatMessagesSent > 4) {
      clubWeight = Math.min(1.0, clubWeight + 0.35);
    }

    // 5. In-Stadium 5G signal
    if (telemetry.inStadium5GConnected) {
      stadiumWeight = 0.95;
    }

    // Normalize confidence scores
    const sum = casualWeight + genzWeight + hardcoreWeight + clubWeight + (stadiumWeight > 0.5 ? stadiumWeight : 0);
    if (sum > 0) {
      casualWeight = parseFloat((casualWeight / sum).toFixed(2));
      genzWeight = parseFloat((genzWeight / sum).toFixed(2));
      hardcoreWeight = parseFloat((hardcoreWeight / sum).toFixed(2));
      clubWeight = parseFloat((clubWeight / sum).toFixed(2));
      if (stadiumWeight > 0.5) stadiumWeight = parseFloat((stadiumWeight / sum).toFixed(2));
    }

    return {
      casual: Math.max(0.05, Math.min(1.0, casualWeight)),
      genz: Math.max(0.05, Math.min(1.0, genzWeight)),
      hardcore: Math.max(0.05, Math.min(1.0, hardcoreWeight)),
      club_member: Math.max(0.05, Math.min(1.0, clubWeight)),
      stadium: stadiumWeight,
    };
  }
}

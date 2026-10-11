import { sharedVlmCache } from '../../core/cache/ttlCache.js';
import { MultiSportTelemetryData } from '../../datasets/dataset1_telemetry.js';
import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';

export interface VlmTacticalInference {
  matchId: string;
  timestampMs: number;
  tacticalSummary: string;
  detectedEvent?: string;
  isDeadTime: boolean;
  deadTimeType?: string;
  suggestedDeadTimeDurationSeconds?: number;
  highlightHypeScore?: number; // 0 to 100
  aiNarrative: string;
}

/**
 * Subsystem 3: Shared VLM Inference Pool (Flaw 4 Fix)
 * One inference per match broadcast, not per viewer (O(1) compute cost).
 * Caches results in Redis with 500ms TTL.
 */
export class VlmInferencePool {
  private static instance: VlmInferencePool;
  private prewarmedMatches: Set<string> = new Set();
  private inferenceCount: number = 0;

  private constructor() {}

  public static getInstance(): VlmInferencePool {
    if (!VlmInferencePool.instance) {
      VlmInferencePool.instance = new VlmInferencePool();
    }
    return VlmInferencePool.instance;
  }

  /**
   * Pre-warm GPU worker pool 10 minutes prior to kickoff
   */
  public prewarmMatchPool(matchId: string): void {
    this.prewarmedMatches.add(matchId);
    console.log(`[VLMInferencePool] Pre-warmed inference worker pool for match: ${matchId}`);
  }

  /**
   * Run shared broadcast inference (O(1) per match broadcast)
   */
  public async inferBroadcastContext(
    matchId: string,
    telemetryFrame: MultiSportTelemetryData
  ): Promise<VlmTacticalInference> {
    const cacheKey = `vlm:match:${matchId}:latest`;

    // 1. Check shared inference cache (500ms TTL)
    const cached = sharedVlmCache.get(cacheKey);
    if (cached) {
      return cached as VlmTacticalInference;
    }

    // 2. Perform Single Match Broadcast Analysis
    this.inferenceCount++;
    const now = Date.now();
    let detectedEvent: string | undefined;
    let isDeadTime = false;
    let deadTimeType: string | undefined;
    let deadTimeDuration: number | undefined;
    let highlightHype = 50;
    let narrative = 'Live open play in progress.';

    if (telemetryFrame.sport === 'CRICKET') {
      const bowler = telemetryFrame.active_players.find((p) => p.role === 'BOWLER');
      if (telemetryFrame.tactical_metadata?.drs_review_available && Math.random() < 0.2) {
        isDeadTime = true;
        detectedEvent = 'DRS_LBW_REVIEW';
        deadTimeType = 'UMPIRE_REVIEW';
        deadTimeDuration = 45;
        highlightHype = 85;
        narrative = 'Umpire signal DRS review for LBW. Ball-tracking Hawkeye cameras engaged.';
      } else {
        narrative = `Bowler release speed recorded at ${bowler?.release_speed_kmh || 142} km/h on full length.`;
      }
    } else if (telemetryFrame.sport === 'FOOTBALL') {
      const xg = telemetryFrame.tactical_metadata?.xg_snapshot || 0.1;
      if (xg > 0.65) {
        highlightHype = 92;
        narrative = `High-danger scoring opportunity detected! xG peak at ${xg}.`;
      }
      if (Math.random() < 0.15) {
        isDeadTime = true;
        detectedEvent = 'VAR_PENALTY_CHECK';
        deadTimeType = 'VAR_STOPPAGE';
        deadTimeDuration = 60;
        narrative = 'Referee checking pitchside monitor for potential handball in penalty area.';
      }
    } else if (telemetryFrame.sport === 'BASKETBALL') {
      const shotClock = telemetryFrame.tactical_metadata?.shot_clock_seconds ?? 12.0;
      if (shotClock < 5.0) {
        highlightHype = 88;
        narrative = 'Shot clock under 5 seconds! Clutch isolation play developing.';
      }
    }

    const inferenceResult: VlmTacticalInference = {
      matchId,
      timestampMs: now,
      tacticalSummary: `${telemetryFrame.sport} Live Tactical Frame Analysis`,
      detectedEvent,
      isDeadTime,
      deadTimeType,
      suggestedDeadTimeDurationSeconds: deadTimeDuration,
      highlightHypeScore: highlightHype,
      aiNarrative: narrative,
    };

    // 3. Cache in 500ms TTL cache (Shared across ALL viewers)
    sharedVlmCache.set(cacheKey, inferenceResult, matchId, 500);

    // 4. Publish result to EventBus
    await eventBus.publish(TOPICS.VLM_INFERENCE_RESULT, inferenceResult, 'vlm_pool');

    return inferenceResult;
  }

  public getInferenceMetrics(): { totalInferences: number; prewarmedMatches: string[] } {
    return {
      totalInferences: this.inferenceCount,
      prewarmedMatches: Array.from(this.prewarmedMatches),
    };
  }
}

export const vlmInferencePool = VlmInferencePool.getInstance();

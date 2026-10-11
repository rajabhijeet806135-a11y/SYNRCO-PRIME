import { MultiSportTelemetryData } from '../../datasets/dataset1_telemetry.js';
import { FootballAdapter } from './adapters/footballAdapter.js';
import { CricketAdapter } from './adapters/cricketAdapter.js';
import { BasketballAdapter } from './adapters/basketballAdapter.js';
import { TimedMetadataInjector } from './timedMetadata.js';
import { sharedTelemetryCache } from '../../core/cache/ttlCache.js';
import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';

export interface ProcessedTelemetryFrame {
  matchId: string;
  sport: string;
  timestampMs: number;
  frameIdx: number;
  tacticalAnalysis: any;
  timedMetadata: any;
}

export class TelemetryPipeline {
  private static instance: TelemetryPipeline;

  private constructor() {}

  public static getInstance(): TelemetryPipeline {
    if (!TelemetryPipeline.instance) {
      TelemetryPipeline.instance = new TelemetryPipeline();
    }
    return TelemetryPipeline.instance;
  }

  /**
   * Ingests a raw optical/sensor telemetry frame (25Hz - 50Hz)
   */
  public async ingestFrame(rawFrame: MultiSportTelemetryData): Promise<ProcessedTelemetryFrame> {
    let tacticalAnalysis: any;

    switch (rawFrame.sport) {
      case 'FOOTBALL':
        tacticalAnalysis = FootballAdapter.processFrame(rawFrame);
        break;
      case 'CRICKET':
        tacticalAnalysis = CricketAdapter.processFrame(rawFrame);
        break;
      case 'BASKETBALL':
        tacticalAnalysis = BasketballAdapter.processFrame(rawFrame);
        break;
      default:
        tacticalAnalysis = { raw: rawFrame };
    }

    const timedMetadata = TimedMetadataInjector.createTrack(
      { sport: rawFrame.sport, frameIdx: rawFrame.frame_idx, analysis: tacticalAnalysis },
      rawFrame.timestamp_ms
    );

    const processed: ProcessedTelemetryFrame = {
      matchId: rawFrame.match_id,
      sport: rawFrame.sport,
      timestampMs: rawFrame.timestamp_ms,
      frameIdx: rawFrame.frame_idx,
      tacticalAnalysis,
      timedMetadata,
    };

    // Cache latest frame in 200ms TTL cache
    sharedTelemetryCache.set(
      `telemetry:latest:${rawFrame.match_id}`,
      processed,
      rawFrame.match_id,
      200,
      rawFrame.frame_idx
    );

    // Publish to EventBus
    await eventBus.publish(TOPICS.TELEMETRY_PROCESSED, processed, 'telemetry_pipeline');

    return processed;
  }

  public getLatestTelemetry(matchId: string): ProcessedTelemetryFrame | null {
    return sharedTelemetryCache.get(`telemetry:latest:${matchId}`);
  }
}

export const telemetryPipeline = TelemetryPipeline.getInstance();

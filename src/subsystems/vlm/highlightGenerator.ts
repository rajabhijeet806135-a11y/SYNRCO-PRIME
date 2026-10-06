import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';

export interface AiHighlightClip {
  clipId: string;
  matchId: string;
  timestampEpochMs: number;
  durationSeconds: number;
  hypeRating: number; // 0 - 100
  title: string;
  aiDescription: string;
  thumbnailUrl: string;
  videoClipUrl: string;
  crowdDecibelPeak: number;
  tags: string[];
}

export class HighlightGenerator {
  private static instance: HighlightGenerator;
  private highlightsByMatch: Map<string, AiHighlightClip[]> = new Map();

  private constructor() {}

  public static getInstance(): HighlightGenerator {
    if (!HighlightGenerator.instance) {
      HighlightGenerator.instance = new HighlightGenerator();
    }
    return HighlightGenerator.instance;
  }

  /**
   * Generates a real-time AI highlight clip triggered by high excitement / decibels
   */
  public async generateHighlight(
    matchId: string,
    title: string,
    narrative: string,
    hypeScore: number = 85,
    crowdDb: number = 104.5,
    tags: string[] = ['AI_CLIP', 'KEY_PLAY']
  ): Promise<AiHighlightClip> {
    const clipId = `hl_${matchId}_${Date.now()}`;
    const clip: AiHighlightClip = {
      clipId,
      matchId,
      timestampEpochMs: Date.now(),
      durationSeconds: 15,
      hypeRating: Math.min(100, Math.max(0, hypeScore)),
      title,
      aiDescription: narrative,
      thumbnailUrl: `https://assets.syncroprime.io/highlights/${clipId}_thumb.jpg`,
      videoClipUrl: `https://stream.syncroprime.io/clips/${clipId}.mp4`,
      crowdDecibelPeak: crowdDb,
      tags,
    };

    let list = this.highlightsByMatch.get(matchId);
    if (!list) {
      list = [];
      this.highlightsByMatch.set(matchId, list);
    }
    list.unshift(clip); // Prepend latest clip

    // Keep top 25 highlights per match
    if (list.length > 25) list.pop();

    await eventBus.publish(TOPICS.HIGHLIGHT_GENERATED, clip, 'highlight_generator');

    return clip;
  }

  public getHighlights(matchId: string): AiHighlightClip[] {
    return this.highlightsByMatch.get(matchId) || [];
  }
}

export const highlightGenerator = HighlightGenerator.getInstance();

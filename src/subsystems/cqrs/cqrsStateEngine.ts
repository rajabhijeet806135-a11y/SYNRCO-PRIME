import { leaderboardEngine, LeaderboardEntry } from '../../core/redis/zsetLeaderboard.js';
import { redisClient } from '../../core/redis/redisClient.js';
import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';

export class CQRSStateEngine {
  private static instance: CQRSStateEngine;

  private constructor() {}

  public static getInstance(): CQRSStateEngine {
    if (!CQRSStateEngine.instance) {
      CQRSStateEngine.instance = new CQRSStateEngine();
    }
    return CQRSStateEngine.instance;
  }

  // --- Read Operations (In-Memory CQRS Path - 1M+ reads/sec) ---
  public async getMatchLeaderboard(matchId: string, limit: number = 50): Promise<LeaderboardEntry[]> {
    return await leaderboardEngine.getTopUsers(matchId, limit);
  }

  public async getClanLeaderboard(matchId: string, limit: number = 10): Promise<Array<{ rank: number; clanId: string; score: number }>> {
    return await leaderboardEngine.getTopClans(matchId, limit);
  }

  public async getUserRank(matchId: string, userId: string): Promise<{ rank: number; score: number } | null> {
    return await leaderboardEngine.getUserRank(matchId, userId);
  }

  public async getFriendsLeaderboard(matchId: string, friendIds: string[]): Promise<LeaderboardEntry[]> {
    return await leaderboardEngine.getFriendsLeaderboard(matchId, friendIds);
  }

  public async getUserLiveState(userId: string): Promise<any> {
    const raw = await redisClient.get(`user:${userId}:profile`);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  // --- Write Operations (Atomic In-Memory CQRS Path) ---
  public async recordPoints(matchId: string, userId: string, points: number, clanId?: string): Promise<{ userScore: number; clanScore?: number }> {
    const userScore = await leaderboardEngine.addScore(matchId, userId, points);
    let clanScore: number | undefined;

    if (clanId) {
      clanScore = await leaderboardEngine.addClanScore(matchId, clanId, points);
      await eventBus.publish(TOPICS.CLAN_POINTS_AWARDED, { matchId, clanId, points, userId }, 'cqrs_engine');
    }

    await eventBus.publish(TOPICS.LEADERBOARD_UPDATED, { matchId, userId, userScore, clanScore }, 'cqrs_engine');

    return { userScore, clanScore };
  }
}

export const cqrsStateEngine = CQRSStateEngine.getInstance();

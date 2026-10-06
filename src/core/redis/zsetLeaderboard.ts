import { redisClient } from './redisClient.js';

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  score: number;
  username?: string;
  avatarUrl?: string;
  clanId?: string;
  tierBadge?: string;
}

export class ZSetLeaderboard {
  /**
   * Update or increment a user's score in a match leaderboard
   */
  public async addScore(matchId: string, userId: string, points: number): Promise<number> {
    const key = `match:${matchId}:leaderboard`;
    const newScore = await redisClient.zincrby(key, points, userId);
    return newScore;
  }

  /**
   * Add score to a clan's tally
   */
  public async addClanScore(matchId: string, clanId: string, points: number): Promise<number> {
    const key = `match:${matchId}:clans:leaderboard`;
    return await redisClient.zincrby(key, points, clanId);
  }

  /**
   * Get Top N Users for a match (Sub-5ms response time)
   */
  public async getTopUsers(matchId: string, limit: number = 50): Promise<LeaderboardEntry[]> {
    const key = `match:${matchId}:leaderboard`;
    const membersWithScores = await redisClient.zrevrange(key, 0, limit - 1, true);
    
    const entries: LeaderboardEntry[] = [];
    let rank = 1;
    for (let i = 0; i < membersWithScores.length; i += 2) {
      const userId = membersWithScores[i];
      const score = parseFloat(membersWithScores[i + 1]) || 0;
      entries.push({
        rank: rank++,
        userId,
        score,
      });
    }

    return entries;
  }

  /**
   * Get Top Clans for a match
   */
  public async getTopClans(matchId: string, limit: number = 10): Promise<Array<{ rank: number; clanId: string; score: number }>> {
    const key = `match:${matchId}:clans:leaderboard`;
    const data = await redisClient.zrevrange(key, 0, limit - 1, true);
    
    const entries: Array<{ rank: number; clanId: string; score: number }> = [];
    let rank = 1;
    for (let i = 0; i < data.length; i += 2) {
      const clanId = data[i];
      const score = parseFloat(data[i + 1]) || 0;
      entries.push({
        rank: rank++,
        clanId,
        score,
      });
    }

    return entries;
  }

  /**
   * Get a specific user's rank and score
   */
  public async getUserRank(matchId: string, userId: string): Promise<{ rank: number; score: number } | null> {
    const key = `match:${matchId}:leaderboard`;
    const rank = await redisClient.zrevrank(key, userId);
    const score = await redisClient.zscore(key, userId);

    if (rank === null || score === null) {
      return null;
    }

    return {
      rank: rank + 1, // 1-indexed rank
      score,
    };
  }

  /**
   * Get friends leaderboard for a user
   */
  public async getFriendsLeaderboard(matchId: string, friendUserIds: string[]): Promise<LeaderboardEntry[]> {
    const key = `match:${matchId}:leaderboard`;
    const entries: LeaderboardEntry[] = [];

    for (const friendId of friendUserIds) {
      const score = (await redisClient.zscore(key, friendId)) || 0;
      const rank = (await redisClient.zrevrank(key, friendId)) ?? 999999;
      entries.push({
        rank: rank + 1,
        userId: friendId,
        score,
      });
    }

    return entries.sort((a, b) => b.score - a.score);
  }
}

export const leaderboardEngine = new ZSetLeaderboard();

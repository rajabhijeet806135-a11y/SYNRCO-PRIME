import { InMemoryRedis } from './redisClient.js';

export interface RedisNode {
  id: string;
  role: 'PRIMARY' | 'REPLICA';
  region: string;
  isHealthy: boolean;
  instance: InMemoryRedis;
}

export class SentinelPool {
  private primaryNodeId: string = 'node-primary-us-east';
  private nodes: Map<string, RedisNode> = new Map();
  private sentinelNodes: string[] = ['sentinel-1', 'sentinel-2', 'sentinel-3'];
  private failoverListeners: Array<(newPrimaryId: string) => void> = [];

  constructor() {
    this.initializeCluster();
  }

  private initializeCluster(): void {
    // Primary Write Node
    this.nodes.set(this.primaryNodeId, {
      id: this.primaryNodeId,
      role: 'PRIMARY',
      region: 'us-east',
      isHealthy: true,
      instance: new InMemoryRedis(),
    });

    // 3 Hot-Standby Cross-Region Read Replicas
    this.nodes.set('replica-1-eu-west', {
      id: 'replica-1-eu-west',
      role: 'REPLICA',
      region: 'eu-west',
      isHealthy: true,
      instance: new InMemoryRedis(),
    });

    this.nodes.set('replica-2-ap-south', {
      id: 'replica-2-ap-south',
      role: 'REPLICA',
      region: 'ap-south',
      isHealthy: true,
      instance: new InMemoryRedis(),
    });

    this.nodes.set('replica-3-us-west', {
      id: 'replica-3-us-west',
      role: 'REPLICA',
      region: 'us-west',
      isHealthy: true,
      instance: new InMemoryRedis(),
    });
  }

  public getPrimary(): RedisNode {
    const node = this.nodes.get(this.primaryNodeId);
    if (!node || !node.isHealthy) {
      throw new Error(`[SentinelPool] No healthy Redis primary found! Failover required.`);
    }
    return node;
  }

  public getReadReplica(preferredRegion?: string): RedisNode {
    const replicas = Array.from(this.nodes.values()).filter(
      (n) => n.role === 'REPLICA' && n.isHealthy
    );

    if (replicas.length === 0) {
      // Fallback to primary if replicas are down
      return this.getPrimary();
    }

    if (preferredRegion) {
      const match = replicas.find((r) => r.region === preferredRegion);
      if (match) return match;
    }

    // Round-robin / random selection among healthy replicas
    const idx = Math.floor(Math.random() * replicas.length);
    return replicas[idx];
  }

  /**
   * Simulate Primary Node Crash and Automatic Sentinel Failover (< 5 sec SLA)
   */
  public async triggerFailover(reason: string = 'Simulated Hardware Failure'): Promise<{
    oldPrimary: string;
    newPrimary: string;
    failoverDurationMs: number;
    quorumSentinels: string[];
  }> {
    const startTime = Date.now();
    const oldPrimaryId = this.primaryNodeId;
    const oldPrimary = this.nodes.get(oldPrimaryId);

    if (oldPrimary) {
      oldPrimary.isHealthy = false;
      console.warn(`[SentinelPool] Primary ${oldPrimaryId} failed! (${reason}). Sentinels initiating quorum election...`);
    }

    // Sentinel Quorum vote (requires 2 of 3 sentinels)
    const quorum = this.sentinelNodes.slice(0, 2);

    // Find next available healthy replica
    const candidates = Array.from(this.nodes.values()).filter(
      (n) => n.id !== oldPrimaryId && n.isHealthy
    );

    if (candidates.length === 0) {
      throw new Error('[SentinelPool] Split-brain critical: No healthy replicas available for promotion!');
    }

    const promoted = candidates[0];
    promoted.role = 'PRIMARY';
    this.primaryNodeId = promoted.id;

    const durationMs = Date.now() - startTime + 120; // Simulate 120ms quorum communication

    console.log(
      `[SentinelPool] Failover complete! ${promoted.id} (${promoted.region}) promoted to PRIMARY in ${durationMs}ms.`
    );

    for (const listener of this.failoverListeners) {
      listener(promoted.id);
    }

    return {
      oldPrimary: oldPrimaryId,
      newPrimary: promoted.id,
      failoverDurationMs: durationMs,
      quorumSentinels: quorum,
    };
  }

  public onFailover(callback: (newPrimaryId: string) => void): void {
    this.failoverListeners.push(callback);
  }

  public getTopology(): Array<{ id: string; role: string; region: string; isHealthy: boolean }> {
    return Array.from(this.nodes.values()).map((n) => ({
      id: n.id,
      role: n.role,
      region: n.region,
      isHealthy: n.isHealthy,
    }));
  }
}

export const sentinelPool = new SentinelPool();

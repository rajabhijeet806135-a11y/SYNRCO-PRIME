/**
 * SYNCRO PRIME - Subsystem 4 Token Bucket Rate Limiter
 * Edge Ring-Buffer Token Bucket for Thundering Herd Protection
 * Limits burst ingestion and enforces smooth throughput
 */

export interface TokenBucketOptions {
  capacity: number;
  refillRatePerSec: number;
}

export class TokenBucket {
  private capacity: number;
  private refillRatePerSec: number;
  private tokens: number;
  private lastRefillTimestamp: number;

  constructor(options: TokenBucketOptions) {
    this.capacity = options.capacity;
    this.refillRatePerSec = options.refillRatePerSec;
    this.tokens = options.capacity;
    this.lastRefillTimestamp = Date.now();
  }

  private refill(): void {
    const now = Date.now();
    const elapsedSeconds = (now - this.lastRefillTimestamp) / 1000;
    if (elapsedSeconds > 0) {
      const addedTokens = elapsedSeconds * this.refillRatePerSec;
      this.tokens = Math.min(this.capacity, this.tokens + addedTokens);
      this.lastRefillTimestamp = now;
    }
  }

  /**
   * Attempt to consume N tokens. Returns true if granted, false if rate limited.
   */
  public consume(count: number = 1): boolean {
    this.refill();
    if (this.tokens >= count) {
      this.tokens -= count;
      return true;
    }
    return false;
  }

  public getAvailableTokens(): number {
    this.refill();
    return Math.floor(this.tokens);
  }
}

/**
 * Multi-Key Rate Limiter Store (per-IP, per-User, per-Device)
 */
export class RateLimiterManager {
  private buckets: Map<string, TokenBucket> = new Map();
  private defaultCapacity: number;
  private defaultRefillRate: number;
  private cleanupInterval: NodeJS.Timeout;

  constructor(capacity: number = 100, refillRatePerSec: number = 20) {
    this.defaultCapacity = capacity;
    this.defaultRefillRate = refillRatePerSec;

    // Periodic cleanup of idle buckets every 5 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 5 * 60 * 1000);
  }

  public checkLimit(key: string, cost: number = 1, customCapacity?: number, customRefillRate?: number): boolean {
    let bucket = this.buckets.get(key);
    if (!bucket) {
      bucket = new TokenBucket({
        capacity: customCapacity ?? this.defaultCapacity,
        refillRatePerSec: customRefillRate ?? this.defaultRefillRate,
      });
      this.buckets.set(key, bucket);
    }
    return bucket.consume(cost);
  }

  public getBucket(key: string): TokenBucket | undefined {
    return this.buckets.get(key);
  }

  private cleanup(): void {
    // Drop buckets that are full and untouched
    for (const [key, bucket] of this.buckets.entries()) {
      if (bucket.getAvailableTokens() >= this.defaultCapacity) {
        this.buckets.delete(key);
      }
    }
  }

  public destroy(): void {
    clearInterval(this.cleanupInterval);
    this.buckets.clear();
  }
}

export const defaultRateLimiter = new RateLimiterManager();

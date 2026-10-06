/**
 * SYNCRO PRIME - Subsystem 3 Shared VLM & Telemetry TTL Cache
 * High-speed in-memory TTL cache with O(1) read/write
 * Used for 500ms TTL tactical broadcast inference results
 */

export interface CacheEntry<T> {
  value: T;
  expiresAt: number;
  matchId: string;
  frameIdx?: number;
}

export class TTLBoundedCache<T = any> {
  private cache: Map<string, CacheEntry<T>> = new Map();
  private defaultTtlMs: number;

  constructor(defaultTtlMs: number = 500) {
    this.defaultTtlMs = defaultTtlMs;
  }

  public set(key: string, value: T, matchId: string, ttlMs?: number, frameIdx?: number): void {
    const ttl = ttlMs ?? this.defaultTtlMs;
    this.cache.set(key, {
      value,
      expiresAt: Date.now() + ttl,
      matchId,
      frameIdx,
    });
  }

  public get(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    return entry.value;
  }

  public has(key: string): boolean {
    return this.get(key) !== null;
  }

  public delete(key: string): boolean {
    return this.cache.delete(key);
  }

  public clear(): void {
    this.cache.clear();
  }

  public size(): number {
    return this.cache.size;
  }
}

export const sharedVlmCache = new TTLBoundedCache(500); // 500ms TTL
export const sharedTelemetryCache = new TTLBoundedCache(200); // 200ms TTL

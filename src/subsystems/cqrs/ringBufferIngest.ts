import { defaultRateLimiter } from '../../core/security/tokenBucket.js';

export interface IngestItem<T = any> {
  id: string;
  key: string; // User ID or IP
  timestamp: number;
  payload: T;
}

/**
 * Ring-Buffer Ingest Node with Token-Bucket Thundering Herd Defense
 */
export class RingBufferIngest<T = any> {
  private buffer: IngestItem<T>[] = [];
  private capacity: number;
  private head: number = 0;
  private tail: number = 0;
  private count: number = 0;

  constructor(capacity: number = 10000) {
    this.capacity = capacity;
    this.buffer = new Array<IngestItem<T>>(capacity);
  }

  /**
   * Enqueue an incoming write request subject to token bucket rate limit
   */
  public push(key: string, payload: T, cost: number = 1): { accepted: boolean; queued: boolean; reason?: string } {
    // 1. Check Token-Bucket Rate Limiter
    const allowed = defaultRateLimiter.checkLimit(key, cost);
    if (!allowed) {
      return { accepted: false, queued: false, reason: 'RATE_LIMIT_EXCEEDED' };
    }

    // 2. Add to Ring Buffer
    if (this.count >= this.capacity) {
      return { accepted: false, queued: false, reason: 'RING_BUFFER_FULL' };
    }

    const item: IngestItem<T> = {
      id: `ring_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      key,
      timestamp: Date.now(),
      payload,
    };

    this.buffer[this.tail] = item;
    this.tail = (this.tail + 1) % this.capacity;
    this.count++;

    return { accepted: true, queued: true };
  }

  /**
   * Drain up to maxItems from ring buffer for processing
   */
  public drain(maxItems: number = 500): IngestItem<T>[] {
    const items: IngestItem<T>[] = [];
    const drainCount = Math.min(maxItems, this.count);

    for (let i = 0; i < drainCount; i++) {
      const item = this.buffer[this.head];
      items.push(item);
      this.head = (this.head + 1) % this.capacity;
      this.count--;
    }

    return items;
  }

  public getPendingCount(): number {
    return this.count;
  }
}

export const edgeIngestRingBuffer = new RingBufferIngest();

/**
 * SYNCRO PRIME - Subsystem 5 & 8 Bloom Filter
 * Ultra-fast in-memory Bloom Filter for sub-millisecond idempotency deduplication
 * Guarantees zero duplicate processing for settlement_id and client_event_id
 */

export class BloomFilter {
  private size: number;
  private hashCount: number;
  private bitArray: Uint8Array;
  private exactSet: Set<string>; // Hybrid set for 100% precision testing & debug

  /**
   * @param expectedElements Expected number of elements (default: 100,000)
   * @param falsePositiveRate Target false positive rate (default: 0.001 = 0.1%)
   */
  constructor(expectedElements: number = 100000, falsePositiveRate: number = 0.001) {
    // Optimal bit array size m = - (n * ln(p)) / (ln(2)^2)
    this.size = Math.ceil(-1 * (expectedElements * Math.log(falsePositiveRate)) / Math.pow(Math.log(2), 2));
    // Optimal number of hash functions k = (m / n) * ln(2)
    this.hashCount = Math.max(1, Math.round((this.size / expectedElements) * Math.log(2)));
    
    // Allocate bit array (byte array where each byte has 8 bits)
    this.bitArray = new Uint8Array(Math.ceil(this.size / 8));
    this.exactSet = new Set<string>();
  }

  /**
   * Simple multi-hash simulation using FNV-1a variations
   */
  private getHashes(key: string): number[] {
    const hashes: number[] = [];
    let h1 = 0x811c9dc5; // 32-bit FNV offset basis
    let h2 = 0x5bd1e995; // Murmur constant base

    for (let i = 0; i < key.length; i++) {
      const char = key.charCodeAt(i);
      h1 = Math.imul(h1 ^ char, 0x01000193);
      h2 = Math.imul(h2 ^ char, 0x5bd1e995);
      h2 ^= h2 >>> 13;
    }

    for (let i = 0; i < this.hashCount; i++) {
      // Double hashing technique: gi(x) = (h1(x) + i * h2(x)) mod m
      const combined = Math.abs((h1 + i * h2) % this.size);
      hashes.push(combined);
    }

    return hashes;
  }

  /**
   * Add a key to the Bloom filter
   */
  public add(key: string): void {
    const hashes = this.getHashes(key);
    for (const bitIndex of hashes) {
      const byteIndex = Math.floor(bitIndex / 8);
      const bitOffset = bitIndex % 8;
      this.bitArray[byteIndex] |= 1 << bitOffset;
    }
    this.exactSet.add(key);
  }

  /**
   * Test if a key might be in the Bloom filter
   * Returns false if DEFINITELY NOT in the set.
   * Returns true if PROBABLY in the set.
   */
  public test(key: string): boolean {
    const hashes = this.getHashes(key);
    for (const bitIndex of hashes) {
      const byteIndex = Math.floor(bitIndex / 8);
      const bitOffset = bitIndex % 8;
      if ((this.bitArray[byteIndex] & (1 << bitOffset)) === 0) {
        return false; // Definitely not present
      }
    }
    // Cross-verify with exact set for safety
    return this.exactSet.has(key);
  }

  /**
   * Atomic Test-And-Add: Returns true if ALREADY existed, false if newly added
   */
  public testAndAdd(key: string): boolean {
    const exists = this.test(key);
    if (!exists) {
      this.add(key);
    }
    return exists;
  }

  public sizeCount(): number {
    return this.exactSet.size;
  }

  public clear(): void {
    this.bitArray.fill(0);
    this.exactSet.clear();
  }
}

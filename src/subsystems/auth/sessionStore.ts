import { redisClient } from '../../core/redis/redisClient.js';
import { dbLedger } from '../../core/database/db.js';
import { DeviceFingerprinter, DeviceMetadata } from '../../core/security/deviceFingerprint.js';
import { PersonaType } from '../../config/index.js';

export interface CachedSession {
  sessionId: string;
  userId: string;
  username: string;
  persona: PersonaType;
  accountVerification: 'GUEST' | 'REGISTERED' | 'EMAIL_VERIFIED' | 'PHONE_VERIFIED';
  sybilScore: number;
  fingerprintHash: string;
  subnet: string;
  clanId?: string;
  createdAt: number;
  expiresAt: number;
}

export class SessionStore {
  /**
   * Create or update session in Redis session store and SQL durability table
   */
  public static async createSession(
    userId: string,
    username: string,
    persona: PersonaType,
    verification: 'GUEST' | 'REGISTERED' | 'EMAIL_VERIFIED' | 'PHONE_VERIFIED',
    sybilScore: number,
    deviceMeta: DeviceMetadata,
    clanId?: string
  ): Promise<CachedSession> {
    const sessionId = `sess_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const fingerprintHash = DeviceFingerprinter.generateFingerprint(deviceMeta);
    const subnet = DeviceFingerprinter.extractSubnet(deviceMeta.ip);
    const now = Date.now();
    const expiresAt = now + 30 * 24 * 60 * 60 * 1000; // 30 days

    const sessionData: CachedSession = {
      sessionId,
      userId,
      username,
      persona,
      accountVerification: verification,
      sybilScore,
      fingerprintHash,
      subnet,
      clanId,
      createdAt: now,
      expiresAt,
    };

    // 1. Cache in Redis (TTL = 30 days) - Primary validation source (0 DB hits)
    await redisClient.set(
      `session:${sessionId}`,
      JSON.stringify(sessionData),
      30 * 24 * 3600
    );

    // Map user to active session
    await redisClient.set(`user:${userId}:active_session`, sessionId, 30 * 24 * 3600);

    // Track subnet clustering
    await redisClient.sadd(`subnet:${subnet}:users`, userId);

    // 2. Persist to SQL durability store in background
    try {
      const db = dbLedger.getRawDb();
      const insert = db.prepare(`
        INSERT OR REPLACE INTO sessions (
          id, user_id, device_fingerprint, ip_address, subnet, user_agent, created_at, expires_at, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
      `);
      insert.run(
        sessionId,
        userId,
        fingerprintHash,
        deviceMeta.ip || '127.0.0.1',
        subnet,
        deviceMeta.userAgent || 'unknown',
        now,
        expiresAt
      );
    } catch (err) {
      console.error('[SessionStore] Error persisting session to DB:', err);
    }

    return sessionData;
  }

  /**
   * Fast Redis-based session validation (Sub-1ms check)
   */
  public static async getSession(sessionId: string): Promise<CachedSession | null> {
    const data = await redisClient.get(`session:${sessionId}`);
    if (!data) return null;
    try {
      return JSON.parse(data) as CachedSession;
    } catch {
      return null;
    }
  }

  /**
   * Update active persona in Redis session without DB overhead
   */
  public static async updateSessionPersona(sessionId: string, newPersona: PersonaType): Promise<boolean> {
    const session = await this.getSession(sessionId);
    if (!session) return false;

    session.persona = newPersona;
    await redisClient.set(`session:${sessionId}`, JSON.stringify(session), 30 * 24 * 3600);
    return true;
  }

  /**
   * Revoke session
   */
  public static async revokeSession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    if (session) {
      await redisClient.del(`session:${sessionId}`);
      await redisClient.del(`user:${session.userId}:active_session`);
    }
  }
}

import jwt from 'jsonwebtoken';
import { CONFIG, PersonaType } from '../../config/index.js';

export interface TokenPayload {
  userId: string;
  username: string;
  persona: PersonaType;
  accountVerification: 'GUEST' | 'REGISTERED' | 'EMAIL_VERIFIED' | 'PHONE_VERIFIED';
  isGuest: boolean;
  fingerprintHash: string;
  clanId?: string;
}

export class JwtManager {
  /**
   * Generates short-lived Access Token (15 min expiry per architecture spec)
   */
  public static generateAccessToken(payload: TokenPayload): string {
    return jwt.sign(payload, CONFIG.JWT_SECRET, {
      expiresIn: '15m',
    });
  }

  /**
   * Generates rolling Refresh Token (30 days expiry per architecture spec)
   */
  public static generateRefreshToken(userId: string, fingerprintHash: string): string {
    return jwt.sign(
      { userId, fingerprintHash, type: 'refresh' },
      CONFIG.JWT_REFRESH_SECRET,
      { expiresIn: '30d' }
    );
  }

  /**
   * Generates signed Ephemeral Guest Token (Read-only polls & leaderboards, 0 initial $SYNC earn)
   */
  public static generateGuestToken(fingerprintHash: string): { token: string; guestId: string } {
    const guestId = `guest_${Math.random().toString(36).substring(2, 10)}`;
    const payload: TokenPayload = {
      userId: guestId,
      username: `Guest_${guestId.substring(6)}`,
      persona: 'CASUAL',
      accountVerification: 'GUEST',
      isGuest: true,
      fingerprintHash,
    };

    const token = jwt.sign(payload, CONFIG.JWT_SECRET, {
      expiresIn: '24h',
    });

    return { token, guestId };
  }

  /**
   * Verifies Access Token
   */
  public static verifyAccessToken(token: string): TokenPayload | null {
    try {
      const decoded = jwt.verify(token, CONFIG.JWT_SECRET) as TokenPayload;
      return decoded;
    } catch {
      return null;
    }
  }

  /**
   * Verifies Refresh Token
   */
  public static verifyRefreshToken(token: string): { userId: string; fingerprintHash: string } | null {
    try {
      const decoded = jwt.verify(token, CONFIG.JWT_REFRESH_SECRET) as any;
      if (decoded.type !== 'refresh') return null;
      return { userId: decoded.userId, fingerprintHash: decoded.fingerprintHash };
    } catch {
      return null;
    }
  }
}

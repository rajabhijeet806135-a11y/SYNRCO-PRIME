import bcrypt from 'bcryptjs';
import { dbLedger } from '../../core/database/db.js';
import { JwtManager } from './jwtManager.js';
import { SessionStore, CachedSession } from './sessionStore.js';
import { DeviceFingerprinter, DeviceMetadata } from '../../core/security/deviceFingerprint.js';
import { PersonaType } from '../../config/index.js';

export interface AuthResponse {
  user: {
    id: string;
    email: string;
    username: string;
    persona: PersonaType;
    accountVerification: string;
    sybilScore: number;
    clanId?: string;
    tokens: number;
    xp: number;
    streak: number;
    multiplier: number;
    tierBadge: string;
  };
  accessToken: string;
  refreshToken: string;
  sessionId: string;
}

export class AuthService {
  /**
   * Register a new user with device fingerprinting and default persona
   */
  public static async register(
    email: string,
    username: string,
    passwordPlain: string,
    preferredPersona: PersonaType = 'CASUAL',
    deviceMeta: DeviceMetadata,
    clanId?: string
  ): Promise<AuthResponse> {
    const db = dbLedger.getRawDb();
    const userId = `usr_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const passwordHash = await bcrypt.hash(passwordPlain, 10);
    const now = Date.now();

    const insertUser = db.prepare(`
      INSERT INTO users (
        id, email, username, password_hash, preferred_persona, persona_scores_json,
        account_verification, sybil_trust_score, clan_id, xp_total, sync_tokens,
        prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const initialScores = {
      casual: preferredPersona === 'CASUAL' ? 1.0 : 0.2,
      genz: preferredPersona === 'GEN_Z' ? 1.0 : 0.2,
      hardcore: preferredPersona === 'HARDCORE' ? 1.0 : 0.2,
      club_member: preferredPersona === 'CLUB_MEMBER' ? 1.0 : 0.2,
      stadium: preferredPersona === 'STADIUM' ? 1.0 : 0.0,
      broadcaster: preferredPersona === 'BROADCASTER' ? 1.0 : 0.0,
    };

    insertUser.run(
      userId,
      email.toLowerCase(),
      username,
      passwordHash,
      preferredPersona,
      JSON.stringify(initialScores),
      'EMAIL_VERIFIED', // Standard registered
      0.95, // High initial trust score for registered user
      clanId || null,
      0,
      250, // 250 starter $SYNC tokens
      0,
      1.0,
      'BRONZE_FAN',
      now,
      now
    );

    const session = await SessionStore.createSession(
      userId,
      username,
      preferredPersona,
      'EMAIL_VERIFIED',
      0.95,
      deviceMeta,
      clanId
    );

    const fingerprintHash = DeviceFingerprinter.generateFingerprint(deviceMeta);
    const accessToken = JwtManager.generateAccessToken({
      userId,
      username,
      persona: preferredPersona,
      accountVerification: 'EMAIL_VERIFIED',
      isGuest: false,
      fingerprintHash,
      clanId,
    });

    const refreshToken = JwtManager.generateRefreshToken(userId, fingerprintHash);

    return {
      user: {
        id: userId,
        email: email.toLowerCase(),
        username,
        persona: preferredPersona,
        accountVerification: 'EMAIL_VERIFIED',
        sybilScore: 0.95,
        clanId,
        tokens: 250,
        xp: 0,
        streak: 0,
        multiplier: 1.0,
        tierBadge: 'BRONZE_FAN',
      },
      accessToken,
      refreshToken,
      sessionId: session.sessionId,
    };
  }

  /**
   * Login with email and password
   */
  public static async login(
    email: string,
    passwordPlain: string,
    deviceMeta: DeviceMetadata
  ): Promise<AuthResponse> {
    const db = dbLedger.getRawDb();
    const userRow = db.prepare(`SELECT * FROM users WHERE email = ?`).get(email.toLowerCase()) as any;

    if (!userRow) {
      throw new Error('Invalid email or password');
    }

    if (userRow.password_hash) {
      const match = await bcrypt.compare(passwordPlain, userRow.password_hash);
      if (!match) {
        throw new Error('Invalid email or password');
      }
    }

    const session = await SessionStore.createSession(
      userRow.id,
      userRow.username,
      userRow.preferred_persona as PersonaType,
      userRow.account_verification,
      userRow.sybil_trust_score,
      deviceMeta,
      userRow.clan_id || undefined
    );

    const fingerprintHash = DeviceFingerprinter.generateFingerprint(deviceMeta);
    const accessToken = JwtManager.generateAccessToken({
      userId: userRow.id,
      username: userRow.username,
      persona: userRow.preferred_persona as PersonaType,
      accountVerification: userRow.account_verification,
      isGuest: userRow.account_verification === 'GUEST',
      fingerprintHash,
      clanId: userRow.clan_id || undefined,
    });

    const refreshToken = JwtManager.generateRefreshToken(userRow.id, fingerprintHash);

    return {
      user: {
        id: userRow.id,
        email: userRow.email,
        username: userRow.username,
        persona: userRow.preferred_persona as PersonaType,
        accountVerification: userRow.account_verification,
        sybilScore: userRow.sybil_trust_score,
        clanId: userRow.clan_id || undefined,
        tokens: userRow.sync_tokens,
        xp: userRow.xp_total,
        streak: userRow.prediction_streak,
        multiplier: userRow.streak_multiplier,
        tierBadge: userRow.tier_badge,
      },
      accessToken,
      refreshToken,
      sessionId: session.sessionId,
    };
  }

  /**
   * OAuth2 Gateway login / register (Google / Apple / Facebook)
   */
  public static async oauthLogin(
    provider: 'google' | 'apple' | 'facebook',
    oauthId: string,
    email: string,
    name: string,
    deviceMeta: DeviceMetadata
  ): Promise<AuthResponse> {
    const db = dbLedger.getRawDb();
    let userRow = db.prepare(`SELECT * FROM users WHERE email = ?`).get(email.toLowerCase()) as any;

    if (!userRow) {
      // Auto-register OAuth user
      const userId = `usr_oauth_${provider}_${Date.now()}`;
      const now = Date.now();
      const insert = db.prepare(`
        INSERT INTO users (
          id, email, username, preferred_persona, persona_scores_json,
          account_verification, sybil_trust_score, xp_total, sync_tokens,
          prediction_streak, streak_multiplier, tier_badge, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      insert.run(
        userId,
        email.toLowerCase(),
        name,
        'GEN_Z',
        JSON.stringify({ casual: 0.3, genz: 0.9, hardcore: 0.3, club_member: 0.4 }),
        'EMAIL_VERIFIED',
        0.98,
        0,
        300,
        0,
        1.0,
        'BRONZE_FAN',
        now,
        now
      );
      userRow = db.prepare(`SELECT * FROM users WHERE id = ?`).get(userId);
    }

    const session = await SessionStore.createSession(
      userRow.id,
      userRow.username,
      userRow.preferred_persona as PersonaType,
      userRow.account_verification,
      userRow.sybil_trust_score,
      deviceMeta,
      userRow.clan_id || undefined
    );

    const fingerprintHash = DeviceFingerprinter.generateFingerprint(deviceMeta);
    const accessToken = JwtManager.generateAccessToken({
      userId: userRow.id,
      username: userRow.username,
      persona: userRow.preferred_persona as PersonaType,
      accountVerification: userRow.account_verification,
      isGuest: false,
      fingerprintHash,
      clanId: userRow.clan_id || undefined,
    });

    const refreshToken = JwtManager.generateRefreshToken(userRow.id, fingerprintHash);

    return {
      user: {
        id: userRow.id,
        email: userRow.email,
        username: userRow.username,
        persona: userRow.preferred_persona as PersonaType,
        accountVerification: userRow.account_verification,
        sybilScore: userRow.sybil_trust_score,
        clanId: userRow.clan_id || undefined,
        tokens: userRow.sync_tokens,
        xp: userRow.xp_total,
        streak: userRow.prediction_streak,
        multiplier: userRow.streak_multiplier,
        tierBadge: userRow.tier_badge,
      },
      accessToken,
      refreshToken,
      sessionId: session.sessionId,
    };
  }

  /**
   * Ephemeral Guest Authentication (Read-only polls & leaderboards)
   */
  public static async guestLogin(deviceMeta: DeviceMetadata): Promise<AuthResponse> {
    const fingerprintHash = DeviceFingerprinter.generateFingerprint(deviceMeta);
    const { token, guestId } = JwtManager.generateGuestToken(fingerprintHash);
    const username = `Guest_${guestId.substring(6)}`;

    const session = await SessionStore.createSession(
      guestId,
      username,
      'CASUAL',
      'GUEST',
      0.65, // Lower baseline trust score for anonymous guests
      deviceMeta
    );

    const refreshToken = JwtManager.generateRefreshToken(guestId, fingerprintHash);

    return {
      user: {
        id: guestId,
        email: `${guestId}@guest.syncroprime.io`,
        username,
        persona: 'CASUAL',
        accountVerification: 'GUEST',
        sybilScore: 0.65,
        tokens: 0,
        xp: 0,
        streak: 0,
        multiplier: 1.0,
        tierBadge: 'BRONZE_FAN',
      },
      accessToken: token,
      refreshToken,
      sessionId: session.sessionId,
    };
  }
}

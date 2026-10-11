import crypto from 'crypto';

export interface DeviceMetadata {
  userAgent?: string;
  ip?: string;
  screenResolution?: string;
  platform?: string;
  language?: string;
  timezoneOffset?: number;
  canvasFingerprint?: string;
}

export class DeviceFingerprinter {
  /**
   * Generates a deterministic, cryptographically secure hash for client device identification
   */
  public static generateFingerprint(meta: DeviceMetadata): string {
    const raw = [
      meta.userAgent || 'unknown_ua',
      meta.screenResolution || '1920x1080',
      meta.platform || 'web',
      meta.language || 'en-US',
      meta.timezoneOffset?.toString() || '0',
      meta.canvasFingerprint || 'standard_canvas',
    ].join('|');

    return crypto.createHash('sha256').update(raw).digest('hex');
  }

  /**
   * Extracts the /24 IPv4 subnet (or /48 IPv6 prefix) for cluster detection
   */
  public static extractSubnet(ip: string | undefined): string {
    if (!ip || ip === '127.0.0.1' || ip === '::1' || ip.includes('localhost')) {
      return '127.0.0.0/24';
    }

    // IPv4 check
    if (ip.includes('.')) {
      const parts = ip.split('.');
      if (parts.length >= 3) {
        return `${parts[0]}.${parts[1]}.${parts[2]}.0/24`;
      }
    }

    // IPv6 fallback
    if (ip.includes(':')) {
      const parts = ip.split(':');
      if (parts.length >= 3) {
        return `${parts[0]}:${parts[1]}:${parts[2]}::/48`;
      }
    }

    return ip;
  }
}

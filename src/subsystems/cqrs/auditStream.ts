import { dbLedger } from '../../core/database/db.js';
import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';

export interface AuditStreamRecord {
  id: string;
  eventType: string;
  topic: string;
  payload: any;
  timestamp: number;
}

export class AuditStream {
  private static instance: AuditStream;

  private constructor() {
    this.initSubscriber();
  }

  public static getInstance(): AuditStream {
    if (!AuditStream.instance) {
      AuditStream.instance = new AuditStream();
    }
    return AuditStream.instance;
  }

  private initSubscriber(): void {
    // Listen to all events and log audit trail
    eventBus.subscribe('*', (envelope) => {
      this.logEvent(envelope.topic, envelope.source, envelope.payload);
    });
  }

  public logEvent(topic: string, eventType: string, payload: any): void {
    const id = `audit_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
    dbLedger.appendAuditLog(id, eventType, topic, payload, Date.now());
  }

  public getRecentLogs(limit: number = 50): AuditStreamRecord[] {
    const db = dbLedger.getRawDb();
    const rows = db.prepare(`SELECT * FROM audit_stream ORDER BY timestamp DESC LIMIT ?`).all(limit) as any[];
    return rows.map((r) => ({
      id: r.id,
      eventType: r.event_type,
      topic: r.topic,
      payload: JSON.parse(r.payload_json),
      timestamp: r.timestamp,
    }));
  }
}

export const auditStream = AuditStream.getInstance();

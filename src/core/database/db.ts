import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { CONFIG } from '../../config/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface BatchLedgerItem {
  id: string;
  settlementId: string;
  userId: string;
  matchId?: string;
  transactionType: string;
  tokenAmount: number;
  xpAmount: number;
  balanceAfter: number;
  createdAt: number;
}

export class RelationalLedger {
  private static instance: RelationalLedger;
  private db: Database.Database;
  private writeQueue: BatchLedgerItem[] = [];
  private batchTimer: NodeJS.Timeout | null = null;
  private isProcessingBatch: boolean = false;

  private constructor() {
    const dbPath = path.resolve(process.cwd(), CONFIG.DB_FILE);
    this.db = new Database(dbPath);

    // High performance WAL mode & pragmas
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('synchronous = NORMAL');
    this.db.pragma('temp_store = MEMORY');

    this.initSchema();
    this.startBatchFlusher();
  }

  public static getInstance(): RelationalLedger {
    if (!RelationalLedger.instance) {
      RelationalLedger.instance = new RelationalLedger();
    }
    return RelationalLedger.instance;
  }

  private initSchema(): void {
    const schemaPath = path.join(__dirname, 'schema.sql');
    if (fs.existsSync(schemaPath)) {
      const sql = fs.readFileSync(schemaPath, 'utf8');
      this.db.exec(sql);
    }
  }

  public getRawDb(): Database.Database {
    return this.db;
  }

  /**
   * Queue a ledger entry for the 1000ms async background durable write cycle
   */
  public queueLedgerWrite(item: BatchLedgerItem): void {
    this.writeQueue.push(item);
  }

  private startBatchFlusher(): void {
    this.batchTimer = setInterval(() => {
      this.flushBatch();
    }, CONFIG.SETTLEMENT_BATCH_INTERVAL_MS);
  }

  public flushBatch(): number {
    if (this.writeQueue.length === 0 || this.isProcessingBatch) {
      return 0;
    }

    this.isProcessingBatch = true;
    const batch = this.writeQueue.splice(0, this.writeQueue.length);

    try {
      const insertLedger = this.db.prepare(`
        INSERT OR IGNORE INTO token_ledger (
          id, settlement_id, user_id, match_id, transaction_type,
          token_amount, xp_amount, balance_after, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      const updateUserBalance = this.db.prepare(`
        UPDATE users 
        SET sync_tokens = sync_tokens + ?, 
            xp_total = xp_total + ?, 
            updated_at = ? 
        WHERE id = ?
      `);

      const transaction = this.db.transaction((items: BatchLedgerItem[]) => {
        const now = Date.now();
        for (const item of items) {
          insertLedger.run(
            item.id,
            item.settlementId,
            item.userId,
            item.matchId || null,
            item.transactionType,
            item.tokenAmount,
            item.xpAmount,
            item.balanceAfter,
            item.createdAt
          );

          updateUserBalance.run(
            item.tokenAmount,
            item.xpAmount,
            now,
            item.userId
          );
        }
      });

      transaction(batch);
      return batch.length;
    } catch (err) {
      console.error('[RelationalLedger] Error flushing batch ledger writes:', err);
      // Re-queue unwritten items
      this.writeQueue.unshift(...batch);
      return 0;
    } finally {
      this.isProcessingBatch = false;
    }
  }

  /**
   * Append directly to immutable Kafka-like audit stream table
   */
  public appendAuditLog(id: string, eventType: string, topic: string, payload: any, timestamp: number = Date.now()): void {
    try {
      const stmt = this.db.prepare(`
        INSERT INTO audit_stream (id, event_type, topic, payload_json, timestamp)
        VALUES (?, ?, ?, ?, ?)
      `);
      stmt.run(id, eventType, topic, JSON.stringify(payload), timestamp);
    } catch (err) {
      console.error('[RelationalLedger] Failed to append audit log:', err);
    }
  }

  public shutdown(): void {
    if (this.batchTimer) {
      clearInterval(this.batchTimer);
    }
    this.flushBatch();
    this.db.close();
  }
}

export const dbLedger = RelationalLedger.getInstance();

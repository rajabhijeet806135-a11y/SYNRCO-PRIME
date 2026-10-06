import { EventEmitter } from 'events';
import { TopicName } from './topics.js';

export interface EventEnvelope<T = any> {
  id: string;
  topic: TopicName | string;
  timestamp: number;
  source: string;
  payload: T;
  correlationId?: string;
}

export type EventHandler<T = any> = (envelope: EventEnvelope<T>) => Promise<void> | void;

export class EventBus {
  private static instance: EventBus;
  private emitter: EventEmitter;
  private messageCounters: Map<string, number> = new Map();
  private isShuttingDown: boolean = false;

  private constructor() {
    this.emitter = new EventEmitter();
    this.emitter.setMaxListeners(500); // Support high fanout
  }

  public static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  /**
   * Publish an event to the message bus
   */
  public async publish<T = any>(
    topic: TopicName | string,
    payload: T,
    source: string = 'system',
    correlationId?: string
  ): Promise<EventEnvelope<T>> {
    if (this.isShuttingDown) {
      throw new Error(`EventBus is shutting down, cannot publish to ${topic}`);
    }

    const envelope: EventEnvelope<T> = {
      id: `evt_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      topic,
      timestamp: Date.now(),
      source,
      payload,
      correlationId,
    };

    // Update message counters for metrics
    const currentCount = this.messageCounters.get(topic) || 0;
    this.messageCounters.set(topic, currentCount + 1);

    // Asynchronous non-blocking dispatch
    setImmediate(() => {
      this.emitter.emit(topic, envelope);
      this.emitter.emit('*', envelope); // Wildcard subscriber support
    });

    return envelope;
  }

  /**
   * Subscribe to a specific topic
   */
  public subscribe<T = any>(
    topic: TopicName | string,
    handler: EventHandler<T>
  ): () => void {
    const safeHandler = async (envelope: EventEnvelope<T>) => {
      try {
        await handler(envelope);
      } catch (err) {
        console.error(`[EventBus] Error handling event on topic ${topic}:`, err);
      }
    };

    this.emitter.on(topic, safeHandler);

    // Return unsubscribe callback
    return () => {
      this.emitter.off(topic, safeHandler);
    };
  }

  /**
   * Get topic throughput statistics
   */
  public getMetrics(): Record<string, number> {
    const metrics: Record<string, number> = {};
    for (const [topic, count] of this.messageCounters.entries()) {
      metrics[topic] = count;
    }
    return metrics;
  }

  public resetMetrics(): void {
    this.messageCounters.clear();
  }

  public shutdown(): void {
    this.isShuttingDown = true;
    this.emitter.removeAllListeners();
  }
}

export const eventBus = EventBus.getInstance();

/**
 * In-memory store for pending intention contracts awaiting user confirmation
 */

import { IntentionContract, PreviewResponse } from './types.js';

export interface PendingIntent {
  id: string;
  contract: IntentionContract;
  preview: PreviewResponse['preview'];
  createdAt: Date;
  expiresAt: Date;
}

const DEFAULT_TTL_MS = 5 * 60 * 1000; // 5 minutes

class PendingIntentStore {
  private pending: Map<string, PendingIntent> = new Map();
  private ttlMs: number;

  constructor(ttlMs: number = DEFAULT_TTL_MS) {
    this.ttlMs = ttlMs;
  }

  private generateId(): string {
    return `pending-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
  }

  private cleanup(): void {
    const now = new Date();
    for (const [id, intent] of this.pending) {
      if (intent.expiresAt < now) {
        this.pending.delete(id);
      }
    }
  }

  add(contract: IntentionContract, preview: PreviewResponse['preview']): PendingIntent {
    this.cleanup();

    const now = new Date();
    const pending: PendingIntent = {
      id: this.generateId(),
      contract,
      preview,
      createdAt: now,
      expiresAt: new Date(now.getTime() + this.ttlMs),
    };

    this.pending.set(pending.id, pending);
    return pending;
  }

  get(id: string): PendingIntent | undefined {
    this.cleanup();
    const pending = this.pending.get(id);
    if (pending && pending.expiresAt < new Date()) {
      this.pending.delete(id);
      return undefined;
    }
    return pending;
  }

  remove(id: string): boolean {
    return this.pending.delete(id);
  }

  list(): PendingIntent[] {
    this.cleanup();
    return Array.from(this.pending.values());
  }

  clear(): void {
    this.pending.clear();
  }
}

// Singleton instance
export const pendingStore = new PendingIntentStore();

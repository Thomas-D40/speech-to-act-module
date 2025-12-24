/**
 * In-memory store for pending intention contracts awaiting user confirmation
 */
const DEFAULT_TTL_MS = 5 * 60 * 1000; // 5 minutes
class PendingIntentStore {
    pending = new Map();
    ttlMs;
    constructor(ttlMs = DEFAULT_TTL_MS) {
        this.ttlMs = ttlMs;
    }
    generateId() {
        return `pending-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
    }
    cleanup() {
        const now = new Date();
        for (const [id, intent] of this.pending) {
            if (intent.expiresAt < now) {
                this.pending.delete(id);
            }
        }
    }
    add(contract, preview) {
        this.cleanup();
        const now = new Date();
        const pending = {
            id: this.generateId(),
            contract,
            preview,
            createdAt: now,
            expiresAt: new Date(now.getTime() + this.ttlMs),
        };
        this.pending.set(pending.id, pending);
        return pending;
    }
    get(id) {
        this.cleanup();
        const pending = this.pending.get(id);
        if (pending && pending.expiresAt < new Date()) {
            this.pending.delete(id);
            return undefined;
        }
        return pending;
    }
    remove(id) {
        return this.pending.delete(id);
    }
    list() {
        this.cleanup();
        return Array.from(this.pending.values());
    }
    clear() {
        this.pending.clear();
    }
}
// Singleton instance
export const pendingStore = new PendingIntentStore();

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
declare class PendingIntentStore {
    private pending;
    private ttlMs;
    constructor(ttlMs?: number);
    private generateId;
    private cleanup;
    add(contract: IntentionContract, preview: PreviewResponse['preview']): PendingIntent;
    get(id: string): PendingIntent | undefined;
    remove(id: string): boolean;
    list(): PendingIntent[];
    clear(): void;
}
export declare const pendingStore: PendingIntentStore;
export {};
//# sourceMappingURL=pending-store.d.ts.map
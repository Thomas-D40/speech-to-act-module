/**
 * Backend API client for communicating with the mock backend
 */
import { IntentionContract, PreviewResponse, CommitResponse } from './types.js';
export declare class BackendClient {
    private readonly baseUrl;
    constructor(baseUrl?: string);
    preview(contract: IntentionContract): Promise<PreviewResponse>;
    commit(contract: IntentionContract): Promise<CommitResponse>;
    healthCheck(): Promise<boolean>;
}
//# sourceMappingURL=backend-client.d.ts.map
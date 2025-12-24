/**
 * Client for communicating with the Intent Gateway
 */
import { GatewayPreviewResponse, GatewayCommitResponse } from './types.js';
export declare class GatewayClient {
    private readonly baseUrl;
    constructor(baseUrl?: string);
    preview(contract: unknown): Promise<GatewayPreviewResponse>;
    commit(contract: unknown): Promise<GatewayCommitResponse>;
    confirm(pendingId: string): Promise<GatewayCommitResponse>;
    reject(pendingId: string): Promise<{
        success: boolean;
        message: string;
    }>;
    healthCheck(): Promise<boolean>;
}
//# sourceMappingURL=gateway-client.d.ts.map
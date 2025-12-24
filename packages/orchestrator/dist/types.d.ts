/**
 * Types for the Orchestrator service
 */
export interface ProcessRequest {
    facts: Array<{
        dimension: string;
        value: string;
        confidence: number;
    }>;
    targets: string[];
    workflow?: 'safe' | 'fast';
}
export interface GatewayPreviewResponse {
    success: boolean;
    stage: string;
    pending_id?: string;
    expires_at?: string;
    preview?: {
        affectedEntities: unknown[];
        description: string;
        warnings?: string[];
    };
    errors?: Array<{
        field: string;
        message: string;
        code: string;
    }>;
    error?: string;
}
export interface GatewayCommitResponse {
    success: boolean;
    stage: string;
    message?: string;
    mock_id?: string;
    timestamp?: string;
    contract?: {
        domain: string;
        type: string;
        targets: string[];
    };
    errors?: Array<{
        field: string;
        message: string;
        code: string;
    }>;
    error?: string;
}
//# sourceMappingURL=types.d.ts.map
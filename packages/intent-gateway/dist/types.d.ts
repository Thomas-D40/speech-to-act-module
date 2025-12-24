/**
 * Type definitions for MCP Server
 */
export declare const DOMAINS: {
    readonly MEAL: "MEAL";
    readonly SLEEP: "SLEEP";
    readonly DIAPER: "DIAPER";
    readonly ACTIVITY: "ACTIVITY";
    readonly HEALTH: "HEALTH";
    readonly BEHAVIOR: "BEHAVIOR";
    readonly MEDICATION: "MEDICATION";
};
export type Domain = typeof DOMAINS[keyof typeof DOMAINS];
export interface IntentionContract {
    domain: Domain;
    type: string;
    targets: string[];
    attributes: Record<string, unknown>;
    metadata?: {
        timestamp?: string;
        confidence?: number;
        source?: string;
    };
}
export interface ValidationError {
    field: string;
    message: string;
    code: string;
}
export interface PreviewResponse {
    success: boolean;
    preview: {
        affectedEntities: AffectedEntity[];
        description: string;
        warnings?: string[];
    };
    errors?: ValidationError[];
}
export interface CommitResponse {
    success: boolean;
    message: string;
    mockId?: string;
    timestamp?: string;
    errors?: ValidationError[];
}
export interface AffectedEntity {
    entityType: string;
    entityId?: string;
    targets: string[];
    operation: 'CREATE' | 'UPDATE' | 'DELETE';
    changes?: Record<string, unknown>;
}
//# sourceMappingURL=types.d.ts.map
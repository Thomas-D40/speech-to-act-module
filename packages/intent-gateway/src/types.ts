/**
 * Type definitions for MCP Server
 */

export const DOMAINS = {
  MEAL: 'MEAL',
  SLEEP: 'SLEEP',
  DIAPER: 'DIAPER',
  ACTIVITY: 'ACTIVITY',
  HEALTH: 'HEALTH',
  BEHAVIOR: 'BEHAVIOR',
  MEDICATION: 'MEDICATION',
} as const;

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

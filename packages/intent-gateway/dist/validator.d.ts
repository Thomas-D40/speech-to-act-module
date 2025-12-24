/**
 * IntentionContract validation
 */
import { ValidationError } from './types.js';
export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
}
export declare function validateIntentionContract(contract: unknown): ValidationResult;
//# sourceMappingURL=validator.d.ts.map
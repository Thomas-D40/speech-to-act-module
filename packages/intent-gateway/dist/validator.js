/**
 * IntentionContract validation
 */
import { DOMAINS } from './types.js';
const VALID_DOMAINS = Object.values(DOMAINS);
export function validateIntentionContract(contract) {
    const errors = [];
    if (!contract || typeof contract !== 'object') {
        errors.push({
            field: 'contract',
            message: 'Contract must be an object',
            code: 'INVALID_TYPE',
        });
        return { isValid: false, errors };
    }
    const c = contract;
    // Validate domain
    if (!c.domain) {
        errors.push({
            field: 'domain',
            message: 'Domain is required',
            code: 'REQUIRED_FIELD',
        });
    }
    else if (!VALID_DOMAINS.includes(c.domain)) {
        errors.push({
            field: 'domain',
            message: `Invalid domain. Must be one of: ${VALID_DOMAINS.join(', ')}`,
            code: 'INVALID_VALUE',
        });
    }
    // Validate type
    if (!c.type) {
        errors.push({
            field: 'type',
            message: 'Type is required',
            code: 'REQUIRED_FIELD',
        });
    }
    else if (typeof c.type !== 'string') {
        errors.push({
            field: 'type',
            message: 'Type must be a string',
            code: 'INVALID_TYPE',
        });
    }
    // Validate targets
    if (!c.targets) {
        errors.push({
            field: 'targets',
            message: 'Targets is required',
            code: 'REQUIRED_FIELD',
        });
    }
    else if (!Array.isArray(c.targets)) {
        errors.push({
            field: 'targets',
            message: 'Targets must be an array',
            code: 'INVALID_TYPE',
        });
    }
    else if (c.targets.length === 0) {
        errors.push({
            field: 'targets',
            message: 'Targets cannot be empty',
            code: 'EMPTY_ARRAY',
        });
    }
    else if (!c.targets.every((t) => typeof t === 'string')) {
        errors.push({
            field: 'targets',
            message: 'All targets must be strings',
            code: 'INVALID_TYPE',
        });
    }
    // Validate attributes
    if (!c.attributes) {
        errors.push({
            field: 'attributes',
            message: 'Attributes is required',
            code: 'REQUIRED_FIELD',
        });
    }
    else if (typeof c.attributes !== 'object' || Array.isArray(c.attributes)) {
        errors.push({
            field: 'attributes',
            message: 'Attributes must be an object',
            code: 'INVALID_TYPE',
        });
    }
    // Validate metadata (optional)
    if (c.metadata !== undefined) {
        if (typeof c.metadata !== 'object' || Array.isArray(c.metadata)) {
            errors.push({
                field: 'metadata',
                message: 'Metadata must be an object',
                code: 'INVALID_TYPE',
            });
        }
        else {
            const meta = c.metadata;
            if (meta.confidence !== undefined) {
                if (typeof meta.confidence !== 'number' || meta.confidence < 0 || meta.confidence > 1) {
                    errors.push({
                        field: 'metadata.confidence',
                        message: 'Confidence must be a number between 0 and 1',
                        code: 'INVALID_VALUE',
                    });
                }
            }
        }
    }
    return {
        isValid: errors.length === 0,
        errors,
    };
}

"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateIntentionContract = validateIntentionContract;
const types_1 = require("./types");
function validateIntentionContract(contract) {
    const errors = [];
    if (!contract) {
        errors.push({ field: 'contract', message: 'Contract is required', code: 'MISSING_CONTRACT' });
        return { isValid: false, errors };
    }
    if (!contract.domain) {
        errors.push({ field: 'domain', message: 'Domain is required', code: 'MISSING_DOMAIN' });
    }
    else if (!Object.values(types_1.DOMAINS).includes(contract.domain)) {
        errors.push({
            field: 'domain',
            message: `Invalid domain. Must be one of: ${Object.values(types_1.DOMAINS).join(', ')}`,
            code: 'INVALID_DOMAIN'
        });
    }
    if (!contract.type) {
        errors.push({ field: 'type', message: 'Type is required', code: 'MISSING_TYPE' });
    }
    if (!contract.targets) {
        errors.push({ field: 'targets', message: 'Targets are required', code: 'MISSING_TARGETS' });
    }
    else if (!Array.isArray(contract.targets)) {
        errors.push({ field: 'targets', message: 'Targets must be an array', code: 'INVALID_TARGETS_FORMAT' });
    }
    else if (contract.targets.length === 0) {
        errors.push({ field: 'targets', message: 'At least one target is required', code: 'EMPTY_TARGETS' });
    }
    if (!contract.attributes) {
        errors.push({ field: 'attributes', message: 'Attributes are required', code: 'MISSING_ATTRIBUTES' });
    }
    else if (typeof contract.attributes !== 'object' || Array.isArray(contract.attributes)) {
        errors.push({ field: 'attributes', message: 'Attributes must be an object', code: 'INVALID_ATTRIBUTES_FORMAT' });
    }
    if (contract.metadata?.confidence !== undefined) {
        if (typeof contract.metadata.confidence !== 'number' ||
            contract.metadata.confidence < 0 ||
            contract.metadata.confidence > 1) {
            errors.push({
                field: 'metadata.confidence',
                message: 'Confidence must be a number between 0 and 1',
                code: 'INVALID_CONFIDENCE'
            });
        }
    }
    return { isValid: errors.length === 0, errors };
}
//# sourceMappingURL=validators.js.map
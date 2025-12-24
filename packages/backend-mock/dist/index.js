"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const types_1 = require("./types");
const validators_1 = require("./validators");
const app = (0, express_1.default)();
const PORT = process.env.PORT || 3001;
app.use((0, cors_1.default)());
app.use(express_1.default.json());
app.use((req, _, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});
/**
 * POST /api/intents/preview - Dry-run preview of intention
 */
app.post('/api/intents/preview', (req, res) => {
    const validation = (0, validators_1.validateIntentionContract)(req.body);
    if (!validation.isValid) {
        const response = {
            success: false,
            preview: { affectedEntities: [], description: 'Validation failed' },
            errors: validation.errors,
        };
        return res.status(400).json(response);
    }
    const contract = req.body;
    const preview = generatePreview(contract);
    const response = { success: true, preview };
    res.json(response);
});
/**
 * POST /api/intents/commit - Mock commit (no persistence)
 */
app.post('/api/intents/commit', (req, res) => {
    const validation = (0, validators_1.validateIntentionContract)(req.body);
    if (!validation.isValid) {
        const response = {
            success: false,
            message: 'Validation failed',
            errors: validation.errors,
        };
        return res.status(400).json(response);
    }
    const contract = req.body;
    const mockId = `mock-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    const response = {
        success: true,
        message: `Mock commit successful for ${contract.targets.join(', ')} - ${contract.domain}/${contract.type}`,
        mockId,
        timestamp: new Date().toISOString(),
    };
    res.json(response);
});
app.get('/health', (_, res) => {
    res.json({ status: 'ok', service: 'backend-mock', timestamp: new Date().toISOString() });
});
app.get('/', (_, res) => {
    res.json({
        service: 'Speech-to-Act Mock Backend API',
        version: '1.0.0',
        endpoints: {
            preview: 'POST /api/intents/preview',
            commit: 'POST /api/intents/commit',
            health: 'GET /health',
        },
    });
});
function generatePreview(contract) {
    const warnings = [];
    const entity = {
        entityType: getEntityType(contract.domain),
        targets: contract.targets,
        operation: 'CREATE',
        changes: {
            ...contract.attributes,
            timestamp: contract.metadata?.timestamp || new Date().toISOString(),
        },
    };
    const description = `Would create ${entity.entityType} for ${contract.targets.join(', ')}`;
    if (contract.metadata?.confidence && contract.metadata.confidence < 0.7) {
        warnings.push('Low confidence score - consider manual verification');
    }
    if (contract.domain === types_1.DOMAINS.MEDICATION) {
        warnings.push('Medication administration requires verification');
    }
    return {
        affectedEntities: [entity],
        description,
        ...(warnings.length > 0 && { warnings }),
    };
}
function getEntityType(domain) {
    const mapping = {
        MEAL: 'MealRecord',
        SLEEP: 'SleepRecord',
        DIAPER: 'DiaperChangeRecord',
        ACTIVITY: 'ActivityRecord',
        HEALTH: 'HealthObservation',
        BEHAVIOR: 'BehaviorLog',
        MEDICATION: 'MedicationRecord',
    };
    return mapping[domain] || 'Record';
}
app.listen(PORT, () => {
    console.log('='.repeat(50));
    console.log('Speech-to-Act Mock Backend API');
    console.log(`Server running on http://localhost:${PORT}`);
    console.log('NOTE: This is a MOCK server - no data is persisted');
    console.log('='.repeat(50));
});
//# sourceMappingURL=index.js.map
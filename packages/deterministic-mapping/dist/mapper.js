"use strict";
/**
 * DeterministicMapper - Pure TypeScript, NO AI/LLM
 * Transforms CanonicalFacts into IntentionContracts deterministically
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeterministicMapper = void 0;
const mappings_1 = require("./mappings");
class DeterministicMapper {
    mappingFunctions;
    constructor() {
        this.mappingFunctions = [
            mappings_1.mapMealFacts,
            mappings_1.mapSleepFacts,
            mappings_1.mapDiaperFacts,
            mappings_1.mapActivityFacts,
            mappings_1.mapHealthFacts,
            mappings_1.mapBehaviorFacts,
            mappings_1.mapMedicationFacts,
        ];
    }
    /**
     * Maps canonical facts to an intention contract
     * This is 100% deterministic - same input ALWAYS produces same output
     */
    map(input) {
        const { facts, targets } = input;
        if (!facts || facts.length === 0) {
            throw new Error('Cannot map empty facts array');
        }
        if (!targets || targets.length === 0) {
            throw new Error('Cannot map without targets (child names)');
        }
        for (const mappingFn of this.mappingFunctions) {
            const result = mappingFn(facts);
            if (result) {
                return {
                    domain: result.domain,
                    type: result.type,
                    targets,
                    attributes: result.attributes,
                    metadata: {
                        timestamp: new Date().toISOString(),
                        confidence: result.confidence,
                        source: 'deterministic-mapping',
                    },
                };
            }
        }
        const dimensions = facts.map((f) => f.dimension).join(', ');
        throw new Error(`No mapping found for dimensions: ${dimensions}`);
    }
    /**
     * Validates that all facts have valid structure
     */
    validateFacts(facts) {
        return facts.every((fact) => fact.dimension &&
            fact.value &&
            typeof fact.confidence === 'number' &&
            fact.confidence >= 0 &&
            fact.confidence <= 1);
    }
}
exports.DeterministicMapper = DeterministicMapper;
//# sourceMappingURL=mapper.js.map
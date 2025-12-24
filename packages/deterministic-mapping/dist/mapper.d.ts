/**
 * DeterministicMapper - Pure TypeScript, NO AI/LLM
 * Transforms CanonicalFacts into IntentionContracts deterministically
 */
import { IntentionContract, CanonicalFact, MappingInput } from './types';
export declare class DeterministicMapper {
    private readonly mappingFunctions;
    constructor();
    /**
     * Maps canonical facts to an intention contract
     * This is 100% deterministic - same input ALWAYS produces same output
     */
    map(input: MappingInput): IntentionContract;
    /**
     * Validates that all facts have valid structure
     */
    validateFacts(facts: CanonicalFact[]): boolean;
}
//# sourceMappingURL=mapper.d.ts.map
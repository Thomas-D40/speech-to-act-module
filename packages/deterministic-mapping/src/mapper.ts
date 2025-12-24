/**
 * DeterministicMapper - Pure TypeScript, NO AI/LLM
 * Transforms CanonicalFacts into IntentionContracts deterministically
 */

import { IntentionContract, CanonicalFact, MappingFunction, MappingInput } from './types';
import {
  mapMealFacts,
  mapSleepFacts,
  mapDiaperFacts,
  mapActivityFacts,
  mapHealthFacts,
  mapBehaviorFacts,
  mapMedicationFacts,
} from './mappings';

export class DeterministicMapper {
  private readonly mappingFunctions: MappingFunction[];

  constructor() {
    this.mappingFunctions = [
      mapMealFacts,
      mapSleepFacts,
      mapDiaperFacts,
      mapActivityFacts,
      mapHealthFacts,
      mapBehaviorFacts,
      mapMedicationFacts,
    ];
  }

  /**
   * Maps canonical facts to an intention contract
   * This is 100% deterministic - same input ALWAYS produces same output
   */
  map(input: MappingInput): IntentionContract {
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
  validateFacts(facts: CanonicalFact[]): boolean {
    return facts.every(
      (fact) =>
        fact.dimension &&
        fact.value &&
        typeof fact.confidence === 'number' &&
        fact.confidence >= 0 &&
        fact.confidence <= 1
    );
  }
}

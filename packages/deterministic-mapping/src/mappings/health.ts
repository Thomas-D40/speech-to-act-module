import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapHealthFacts(facts: CanonicalFact[]): MappingResult | null {
  const healthFact = facts.find((f) => f.dimension === DIMENSIONS.HEALTH_STATUS);
  if (!healthFact) return null;

  return {
    domain: DOMAINS.HEALTH,
    type: INTENTION_TYPES.HEALTH_OBSERVATION,
    attributes: { status: healthFact.value },
    confidence: healthFact.confidence,
  };
}

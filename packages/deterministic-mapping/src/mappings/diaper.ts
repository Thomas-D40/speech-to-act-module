import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapDiaperFacts(facts: CanonicalFact[]): MappingResult | null {
  const diaperFact = facts.find((f) => f.dimension === DIMENSIONS.DIAPER_CHANGE_TYPE);
  if (!diaperFact) return null;

  return {
    domain: DOMAINS.DIAPER,
    type: INTENTION_TYPES.DIAPER_CHANGE,
    attributes: { changeType: diaperFact.value },
    confidence: diaperFact.confidence,
  };
}

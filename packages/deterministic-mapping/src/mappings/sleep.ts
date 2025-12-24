import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapSleepFacts(facts: CanonicalFact[]): MappingResult | null {
  const sleepFact = facts.find((f) => f.dimension === DIMENSIONS.SLEEP_STATE);
  if (!sleepFact) return null;

  return {
    domain: DOMAINS.SLEEP,
    type: INTENTION_TYPES.SLEEP_LOG,
    attributes: { state: sleepFact.value },
    confidence: sleepFact.confidence,
  };
}

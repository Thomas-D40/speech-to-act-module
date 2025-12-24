import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapActivityFacts(facts: CanonicalFact[]): MappingResult | null {
  const activityFact = facts.find((f) => f.dimension === DIMENSIONS.ACTIVITY_TYPE);
  if (!activityFact) return null;

  return {
    domain: DOMAINS.ACTIVITY,
    type: INTENTION_TYPES.ACTIVITY_LOG,
    attributes: { activityType: activityFact.value },
    confidence: activityFact.confidence,
  };
}

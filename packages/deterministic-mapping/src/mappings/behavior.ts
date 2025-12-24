import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapBehaviorFacts(facts: CanonicalFact[]): MappingResult | null {
  const moodFact = facts.find((f) => f.dimension === DIMENSIONS.CHILD_MOOD);
  if (!moodFact) return null;

  return {
    domain: DOMAINS.BEHAVIOR,
    type: INTENTION_TYPES.BEHAVIOR_LOG,
    attributes: { mood: moodFact.value },
    confidence: moodFact.confidence,
  };
}

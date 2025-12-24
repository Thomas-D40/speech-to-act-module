import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult } from '../types';

export function mapMedicationFacts(facts: CanonicalFact[]): MappingResult | null {
  const medicationFact = facts.find((f) => f.dimension === DIMENSIONS.MEDICATION_TYPE);
  if (!medicationFact) return null;

  return {
    domain: DOMAINS.MEDICATION,
    type: INTENTION_TYPES.MEDICATION_ADMINISTRATION,
    attributes: { medicationType: medicationFact.value },
    confidence: medicationFact.confidence,
  };
}

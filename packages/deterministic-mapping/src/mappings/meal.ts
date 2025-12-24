import { DIMENSIONS, DOMAINS, INTENTION_TYPES, CanonicalFact, MappingResult, Dimension } from '../types';

const MEAL_DIMENSIONS: readonly Dimension[] = [
  DIMENSIONS.MEAL_MAIN_CONSUMPTION,
  DIMENSIONS.MEAL_DESSERT_CONSUMPTION,
  DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION,
  DIMENSIONS.MEAL_TYPE,
];

export function mapMealFacts(facts: CanonicalFact[]): MappingResult | null {
  const mealFacts = facts.filter((f) => MEAL_DIMENSIONS.includes(f.dimension));

  if (mealFacts.length === 0) return null;

  const attributes: Record<string, unknown> = {};
  let totalConfidence = 0;

  for (const fact of mealFacts) {
    switch (fact.dimension) {
      case DIMENSIONS.MEAL_MAIN_CONSUMPTION:
        attributes.main = fact.value;
        break;
      case DIMENSIONS.MEAL_DESSERT_CONSUMPTION:
        attributes.dessert = fact.value;
        break;
      case DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION:
        attributes.vegetable = fact.value;
        break;
      case DIMENSIONS.MEAL_TYPE:
        attributes.mealType = fact.value;
        break;
    }
    totalConfidence += fact.confidence;
  }

  return {
    domain: DOMAINS.MEAL,
    type: INTENTION_TYPES.MEAL_CONSUMPTION,
    attributes,
    confidence: totalConfidence / mealFacts.length,
  };
}

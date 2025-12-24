/**
 * Type definitions for deterministic mapping
 * This is the SINGLE SOURCE OF TRUTH for dimensions, values, and mappings
 */

// Domain constants
export const DOMAINS = {
  MEAL: 'MEAL',
  SLEEP: 'SLEEP',
  DIAPER: 'DIAPER',
  ACTIVITY: 'ACTIVITY',
  HEALTH: 'HEALTH',
  BEHAVIOR: 'BEHAVIOR',
  MEDICATION: 'MEDICATION',
} as const;

export type Domain = typeof DOMAINS[keyof typeof DOMAINS];

// Dimension constants
export const DIMENSIONS = {
  MEAL_MAIN_CONSUMPTION: 'MEAL_MAIN_CONSUMPTION',
  MEAL_DESSERT_CONSUMPTION: 'MEAL_DESSERT_CONSUMPTION',
  MEAL_VEGETABLE_CONSUMPTION: 'MEAL_VEGETABLE_CONSUMPTION',
  MEAL_TYPE: 'MEAL_TYPE',
  SLEEP_STATE: 'SLEEP_STATE',
  DIAPER_CHANGE_TYPE: 'DIAPER_CHANGE_TYPE',
  ACTIVITY_TYPE: 'ACTIVITY_TYPE',
  CHILD_MOOD: 'CHILD_MOOD',
  HEALTH_STATUS: 'HEALTH_STATUS',
  MEDICATION_TYPE: 'MEDICATION_TYPE',
} as const;

export type Dimension = typeof DIMENSIONS[keyof typeof DIMENSIONS];

// Valid values for each dimension
export const DIMENSION_VALUES: Record<Dimension, readonly string[]> = {
  [DIMENSIONS.MEAL_MAIN_CONSUMPTION]: ['NOTHING', 'QUARTER', 'HALF', 'THREE_QUARTERS', 'ALL'] as const,
  [DIMENSIONS.MEAL_DESSERT_CONSUMPTION]: ['NOTHING', 'QUARTER', 'HALF', 'THREE_QUARTERS', 'ALL'] as const,
  [DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION]: ['NOTHING', 'QUARTER', 'HALF', 'THREE_QUARTERS', 'ALL'] as const,
  [DIMENSIONS.MEAL_TYPE]: ['BREAKFAST', 'LUNCH', 'SNACK', 'DINNER'] as const,
  [DIMENSIONS.SLEEP_STATE]: ['ASLEEP', 'WOKE_UP', 'RESTING', 'REFUSED_SLEEP'] as const,
  [DIMENSIONS.DIAPER_CHANGE_TYPE]: ['WET', 'DIRTY', 'BOTH', 'DRY'] as const,
  [DIMENSIONS.ACTIVITY_TYPE]: ['OUTDOOR_PLAY', 'INDOOR_PLAY', 'CRAFT', 'READING', 'MUSIC', 'MOTOR_SKILLS', 'FREE_PLAY'] as const,
  [DIMENSIONS.CHILD_MOOD]: ['HAPPY', 'CALM', 'TIRED', 'UPSET', 'EXCITED', 'CRANKY'] as const,
  [DIMENSIONS.HEALTH_STATUS]: ['HEALTHY', 'FEVER', 'COUGH', 'RUNNY_NOSE', 'RASH', 'VOMITING', 'DIARRHEA'] as const,
  [DIMENSIONS.MEDICATION_TYPE]: ['PAIN_RELIEVER', 'ANTIBIOTIC', 'ALLERGY', 'VITAMIN', 'OTHER'] as const,
};

// Dimension to Domain mapping
export const DIMENSION_TO_DOMAIN: Record<Dimension, Domain> = {
  [DIMENSIONS.MEAL_MAIN_CONSUMPTION]: DOMAINS.MEAL,
  [DIMENSIONS.MEAL_DESSERT_CONSUMPTION]: DOMAINS.MEAL,
  [DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION]: DOMAINS.MEAL,
  [DIMENSIONS.MEAL_TYPE]: DOMAINS.MEAL,
  [DIMENSIONS.SLEEP_STATE]: DOMAINS.SLEEP,
  [DIMENSIONS.DIAPER_CHANGE_TYPE]: DOMAINS.DIAPER,
  [DIMENSIONS.ACTIVITY_TYPE]: DOMAINS.ACTIVITY,
  [DIMENSIONS.CHILD_MOOD]: DOMAINS.BEHAVIOR,
  [DIMENSIONS.HEALTH_STATUS]: DOMAINS.HEALTH,
  [DIMENSIONS.MEDICATION_TYPE]: DOMAINS.MEDICATION,
};

// Dimension descriptions for LLM prompts
export const DIMENSION_DESCRIPTIONS: Record<Dimension, string> = {
  [DIMENSIONS.MEAL_MAIN_CONSUMPTION]: 'How much of the main dish the child ate',
  [DIMENSIONS.MEAL_DESSERT_CONSUMPTION]: 'How much dessert the child ate',
  [DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION]: 'How much vegetables the child ate',
  [DIMENSIONS.MEAL_TYPE]: 'Type of meal (breakfast, lunch, snack, dinner)',
  [DIMENSIONS.SLEEP_STATE]: 'Sleep-related state change',
  [DIMENSIONS.DIAPER_CHANGE_TYPE]: 'Type of diaper change needed',
  [DIMENSIONS.ACTIVITY_TYPE]: 'Type of activity the child participated in',
  [DIMENSIONS.CHILD_MOOD]: 'Current mood or emotional state of the child',
  [DIMENSIONS.HEALTH_STATUS]: 'Health observation or symptom',
  [DIMENSIONS.MEDICATION_TYPE]: 'Type of medication administered',
};

// Intention types
export const INTENTION_TYPES = {
  MEAL_CONSUMPTION: 'MEAL_CONSUMPTION',
  SLEEP_LOG: 'SLEEP_LOG',
  DIAPER_CHANGE: 'DIAPER_CHANGE',
  ACTIVITY_LOG: 'ACTIVITY_LOG',
  HEALTH_OBSERVATION: 'HEALTH_OBSERVATION',
  BEHAVIOR_LOG: 'BEHAVIOR_LOG',
  MEDICATION_ADMINISTRATION: 'MEDICATION_ADMINISTRATION',
} as const;

export type IntentionType = typeof INTENTION_TYPES[keyof typeof INTENTION_TYPES];

// Intention Contract
export interface IntentionContract {
  domain: Domain;
  type: string;
  targets: string[];
  attributes: Record<string, unknown>;
  metadata?: {
    timestamp?: string;
    confidence?: number;
    source?: string;
  };
}

// Canonical Fact
export interface CanonicalFact {
  dimension: Dimension;
  value: string;
  confidence: number;
}

// Mapping types
export interface MappingResult {
  domain: Domain;
  type: string;
  attributes: Record<string, unknown>;
  confidence?: number;
}

export type MappingFunction = (facts: CanonicalFact[]) => MappingResult | null;

export interface MappingInput {
  facts: CanonicalFact[];
  targets: string[];
}

// Schema export for API
export interface DimensionSchema {
  dimension: string;
  description: string;
  domain: string;
  validValues: readonly string[];
}

export interface MappingSchema {
  domains: string[];
  dimensions: DimensionSchema[];
  canonicalFactSchema: {
    dimension: string;
    value: string;
    confidence: string;
  };
}

export function getSchema(): MappingSchema {
  const dimensions: DimensionSchema[] = Object.values(DIMENSIONS).map((dim) => ({
    dimension: dim,
    description: DIMENSION_DESCRIPTIONS[dim],
    domain: DIMENSION_TO_DOMAIN[dim],
    validValues: DIMENSION_VALUES[dim],
  }));

  return {
    domains: Object.values(DOMAINS),
    dimensions,
    canonicalFactSchema: {
      dimension: 'One of the valid dimension values',
      value: 'One of the valid values for the chosen dimension',
      confidence: 'Number between 0 and 1 indicating classification confidence',
    },
  };
}

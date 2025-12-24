/**
 * Type definitions for deterministic mapping
 */
export declare const DOMAINS: {
    readonly MEAL: "MEAL";
    readonly SLEEP: "SLEEP";
    readonly DIAPER: "DIAPER";
    readonly ACTIVITY: "ACTIVITY";
    readonly HEALTH: "HEALTH";
    readonly BEHAVIOR: "BEHAVIOR";
    readonly MEDICATION: "MEDICATION";
};
export type Domain = typeof DOMAINS[keyof typeof DOMAINS];
export declare const DIMENSIONS: {
    readonly MEAL_MAIN_CONSUMPTION: "MEAL_MAIN_CONSUMPTION";
    readonly MEAL_DESSERT_CONSUMPTION: "MEAL_DESSERT_CONSUMPTION";
    readonly MEAL_VEGETABLE_CONSUMPTION: "MEAL_VEGETABLE_CONSUMPTION";
    readonly MEAL_TYPE: "MEAL_TYPE";
    readonly SLEEP_STATE: "SLEEP_STATE";
    readonly DIAPER_CHANGE_TYPE: "DIAPER_CHANGE_TYPE";
    readonly ACTIVITY_TYPE: "ACTIVITY_TYPE";
    readonly CHILD_MOOD: "CHILD_MOOD";
    readonly HEALTH_STATUS: "HEALTH_STATUS";
    readonly MEDICATION_TYPE: "MEDICATION_TYPE";
};
export type Dimension = typeof DIMENSIONS[keyof typeof DIMENSIONS];
export declare const INTENTION_TYPES: {
    readonly MEAL_CONSUMPTION: "MEAL_CONSUMPTION";
    readonly SLEEP_LOG: "SLEEP_LOG";
    readonly DIAPER_CHANGE: "DIAPER_CHANGE";
    readonly ACTIVITY_LOG: "ACTIVITY_LOG";
    readonly HEALTH_OBSERVATION: "HEALTH_OBSERVATION";
    readonly BEHAVIOR_LOG: "BEHAVIOR_LOG";
    readonly MEDICATION_ADMINISTRATION: "MEDICATION_ADMINISTRATION";
};
export type IntentionType = typeof INTENTION_TYPES[keyof typeof INTENTION_TYPES];
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
export interface CanonicalFact {
    dimension: Dimension;
    value: string;
    confidence: number;
}
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
//# sourceMappingURL=types.d.ts.map
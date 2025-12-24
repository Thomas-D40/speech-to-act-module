"""
Domain constants for MCP Intent Gateway.
This is the SINGLE SOURCE OF TRUTH for dimensions, values, and mappings.
Mirrored from packages/deterministic-mapping/src/types.ts
"""

from enum import Enum


class Domain(str, Enum):
    """Domain constants."""

    MEAL = "MEAL"
    SLEEP = "SLEEP"
    DIAPER = "DIAPER"
    ACTIVITY = "ACTIVITY"
    HEALTH = "HEALTH"
    BEHAVIOR = "BEHAVIOR"
    MEDICATION = "MEDICATION"


class Dimension(str, Enum):
    """Dimension constants."""

    MEAL_MAIN_CONSUMPTION = "MEAL_MAIN_CONSUMPTION"
    MEAL_DESSERT_CONSUMPTION = "MEAL_DESSERT_CONSUMPTION"
    MEAL_VEGETABLE_CONSUMPTION = "MEAL_VEGETABLE_CONSUMPTION"
    MEAL_TYPE = "MEAL_TYPE"
    SLEEP_STATE = "SLEEP_STATE"
    DIAPER_CHANGE_TYPE = "DIAPER_CHANGE_TYPE"
    ACTIVITY_TYPE = "ACTIVITY_TYPE"
    CHILD_MOOD = "CHILD_MOOD"
    HEALTH_STATUS = "HEALTH_STATUS"
    MEDICATION_TYPE = "MEDICATION_TYPE"


class IntentionType(str, Enum):
    """Intention type constants."""

    MEAL_CONSUMPTION = "MEAL_CONSUMPTION"
    SLEEP_LOG = "SLEEP_LOG"
    DIAPER_CHANGE = "DIAPER_CHANGE"
    ACTIVITY_LOG = "ACTIVITY_LOG"
    HEALTH_OBSERVATION = "HEALTH_OBSERVATION"
    BEHAVIOR_LOG = "BEHAVIOR_LOG"
    MEDICATION_ADMINISTRATION = "MEDICATION_ADMINISTRATION"


# Valid values for each dimension - MUST match TypeScript exactly
DIMENSION_VALUES: dict[Dimension, list[str]] = {
    Dimension.MEAL_MAIN_CONSUMPTION: ["NOTHING", "QUARTER", "HALF", "THREE_QUARTERS", "ALL"],
    Dimension.MEAL_DESSERT_CONSUMPTION: ["NOTHING", "QUARTER", "HALF", "THREE_QUARTERS", "ALL"],
    Dimension.MEAL_VEGETABLE_CONSUMPTION: ["NOTHING", "QUARTER", "HALF", "THREE_QUARTERS", "ALL"],
    Dimension.MEAL_TYPE: ["BREAKFAST", "LUNCH", "SNACK", "DINNER"],
    Dimension.SLEEP_STATE: ["ASLEEP", "WOKE_UP", "RESTING", "REFUSED_SLEEP"],
    Dimension.DIAPER_CHANGE_TYPE: ["WET", "DIRTY", "BOTH", "DRY"],
    Dimension.ACTIVITY_TYPE: [
        "OUTDOOR_PLAY",
        "INDOOR_PLAY",
        "CRAFT",
        "READING",
        "MUSIC",
        "MOTOR_SKILLS",
        "FREE_PLAY",
    ],
    Dimension.CHILD_MOOD: ["HAPPY", "CALM", "TIRED", "UPSET", "EXCITED", "CRANKY"],
    Dimension.HEALTH_STATUS: [
        "HEALTHY",
        "FEVER",
        "COUGH",
        "RUNNY_NOSE",
        "RASH",
        "VOMITING",
        "DIARRHEA",
    ],
    Dimension.MEDICATION_TYPE: ["PAIN_RELIEVER", "ANTIBIOTIC", "ALLERGY", "VITAMIN", "OTHER"],
}

# Dimension to Domain mapping
DIMENSION_TO_DOMAIN: dict[Dimension, Domain] = {
    Dimension.MEAL_MAIN_CONSUMPTION: Domain.MEAL,
    Dimension.MEAL_DESSERT_CONSUMPTION: Domain.MEAL,
    Dimension.MEAL_VEGETABLE_CONSUMPTION: Domain.MEAL,
    Dimension.MEAL_TYPE: Domain.MEAL,
    Dimension.SLEEP_STATE: Domain.SLEEP,
    Dimension.DIAPER_CHANGE_TYPE: Domain.DIAPER,
    Dimension.ACTIVITY_TYPE: Domain.ACTIVITY,
    Dimension.CHILD_MOOD: Domain.BEHAVIOR,
    Dimension.HEALTH_STATUS: Domain.HEALTH,
    Dimension.MEDICATION_TYPE: Domain.MEDICATION,
}

# Dimension descriptions for LLM prompts
DIMENSION_DESCRIPTIONS: dict[Dimension, str] = {
    Dimension.MEAL_MAIN_CONSUMPTION: "How much of the main dish the child ate",
    Dimension.MEAL_DESSERT_CONSUMPTION: "How much dessert the child ate",
    Dimension.MEAL_VEGETABLE_CONSUMPTION: "How much vegetables the child ate",
    Dimension.MEAL_TYPE: "Type of meal (breakfast, lunch, snack, dinner)",
    Dimension.SLEEP_STATE: "Sleep-related state change",
    Dimension.DIAPER_CHANGE_TYPE: "Type of diaper change needed",
    Dimension.ACTIVITY_TYPE: "Type of activity the child participated in",
    Dimension.CHILD_MOOD: "Current mood or emotional state of the child",
    Dimension.HEALTH_STATUS: "Health observation or symptom",
    Dimension.MEDICATION_TYPE: "Type of medication administered",
}


def is_valid_value_for_dimension(dimension: Dimension, value: str) -> bool:
    """Check if a value is valid for a given dimension."""
    valid_values = DIMENSION_VALUES.get(dimension, [])
    return value in valid_values


def get_domain_for_dimension(dimension: Dimension) -> Domain:
    """Get the domain for a given dimension."""
    return DIMENSION_TO_DOMAIN[dimension]

"""
Constants for semantic normalization - NURSERY DOMAIN
Mirrors the TypeScript schema definitions
"""

from enum import Enum
from typing import Literal


class Dimension(str, Enum):
    """Semantic dimension constants"""
    # Meal dimensions
    MEAL_MAIN_CONSUMPTION = "MEAL_MAIN_CONSUMPTION"
    MEAL_DESSERT_CONSUMPTION = "MEAL_DESSERT_CONSUMPTION"
    MEAL_VEGETABLE_CONSUMPTION = "MEAL_VEGETABLE_CONSUMPTION"
    MEAL_TYPE = "MEAL_TYPE"

    # Sleep dimensions
    SLEEP_STATE = "SLEEP_STATE"

    # Diaper dimensions
    DIAPER_CHANGE_TYPE = "DIAPER_CHANGE_TYPE"

    # Activity dimensions
    ACTIVITY_TYPE = "ACTIVITY_TYPE"

    # Mood/behavior dimensions
    CHILD_MOOD = "CHILD_MOOD"

    # Health dimensions
    HEALTH_STATUS = "HEALTH_STATUS"

    # Medication dimensions
    MEDICATION_TYPE = "MEDICATION_TYPE"


class MealConsumptionValue(str, Enum):
    """Canonical values for meal consumption"""
    NONE = "NONE"
    QUARTER = "QUARTER"
    HALF = "HALF"
    THREE_QUARTERS = "THREE_QUARTERS"
    ALL = "ALL"


class MealTypeValue(str, Enum):
    """Meal types in nursery context"""
    BREAKFAST = "BREAKFAST"
    MORNING_SNACK = "MORNING_SNACK"
    LUNCH = "LUNCH"
    AFTERNOON_SNACK = "AFTERNOON_SNACK"
    DINNER = "DINNER"


class SleepStateValue(str, Enum):
    """Sleep states"""
    ASLEEP = "ASLEEP"
    AWAKE = "AWAKE"
    NAP_START = "NAP_START"
    NAP_END = "NAP_END"


class DiaperTypeValue(str, Enum):
    """Diaper change types"""
    WET = "WET"
    DIRTY = "DIRTY"
    BOTH = "BOTH"


class ActivityTypeValue(str, Enum):
    """Activity types"""
    OUTDOOR_PLAY = "OUTDOOR_PLAY"
    INDOOR_PLAY = "INDOOR_PLAY"
    ARTS_CRAFTS = "ARTS_CRAFTS"
    READING = "READING"
    MUSIC = "MUSIC"
    FREE_PLAY = "FREE_PLAY"


class MoodValue(str, Enum):
    """Mood/behavior states"""
    HAPPY = "HAPPY"
    CALM = "CALM"
    FUSSY = "FUSSY"
    CRYING = "CRYING"
    TIRED = "TIRED"
    ENERGETIC = "ENERGETIC"


class HealthStatusValue(str, Enum):
    """Health indicators"""
    NORMAL = "NORMAL"
    FEVER = "FEVER"
    COLD = "COLD"
    COUGH = "COUGH"
    UPSET_STOMACH = "UPSET_STOMACH"
    RASH = "RASH"


class MedicationTypeValue(str, Enum):
    """Medication types"""
    FEVER_REDUCER = "FEVER_REDUCER"
    ANTIBIOTIC = "ANTIBIOTIC"
    VITAMIN = "VITAMIN"
    PAIN_RELIEVER = "PAIN_RELIEVER"
    ALLERGY_MEDICINE = "ALLERGY_MEDICINE"
    COUGH_SYRUP = "COUGH_SYRUP"


# Mapping of dimensions to their valid values
DIMENSION_VALUE_MAP = {
    Dimension.MEAL_MAIN_CONSUMPTION: MealConsumptionValue,
    Dimension.MEAL_DESSERT_CONSUMPTION: MealConsumptionValue,
    Dimension.MEAL_VEGETABLE_CONSUMPTION: MealConsumptionValue,
    Dimension.MEAL_TYPE: MealTypeValue,
    Dimension.SLEEP_STATE: SleepStateValue,
    Dimension.DIAPER_CHANGE_TYPE: DiaperTypeValue,
    Dimension.ACTIVITY_TYPE: ActivityTypeValue,
    Dimension.CHILD_MOOD: MoodValue,
    Dimension.HEALTH_STATUS: HealthStatusValue,
    Dimension.MEDICATION_TYPE: MedicationTypeValue,
}

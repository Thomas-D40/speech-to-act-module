"""
Semantic Normalization Layer
LLM-based classification for speech-to-act system
"""

from .normalizer import SemanticNormalizer
from .models import CanonicalFact, NormalizationOutput
from .constants import (
    Dimension,
    MealConsumptionValue,
    MealTypeValue,
    SleepStateValue,
    DiaperTypeValue,
    ActivityTypeValue,
    MoodValue,
    HealthStatusValue,
    MedicationTypeValue,
    DIMENSION_VALUE_MAP,
)

__all__ = [
    "SemanticNormalizer",
    "CanonicalFact",
    "NormalizationOutput",
    "Dimension",
    "MealConsumptionValue",
    "MealTypeValue",
    "SleepStateValue",
    "DiaperTypeValue",
    "ActivityTypeValue",
    "MoodValue",
    "HealthStatusValue",
    "MedicationTypeValue",
    "DIMENSION_VALUE_MAP",
]

__version__ = "1.0.0"

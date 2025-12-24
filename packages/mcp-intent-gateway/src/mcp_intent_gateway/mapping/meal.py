"""Meal mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact

MEAL_DIMENSIONS: list[Dimension] = [
    Dimension.MEAL_MAIN_CONSUMPTION,
    Dimension.MEAL_DESSERT_CONSUMPTION,
    Dimension.MEAL_VEGETABLE_CONSUMPTION,
    Dimension.MEAL_TYPE,
]


def map_meal_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map meal-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no meal facts found
    """
    meal_facts = [f for f in facts if f.dimension in MEAL_DIMENSIONS]

    if not meal_facts:
        return None

    attributes: dict[str, Any] = {}
    total_confidence = 0.0

    for fact in meal_facts:
        match fact.dimension:
            case Dimension.MEAL_MAIN_CONSUMPTION:
                attributes["main"] = fact.value
            case Dimension.MEAL_DESSERT_CONSUMPTION:
                attributes["dessert"] = fact.value
            case Dimension.MEAL_VEGETABLE_CONSUMPTION:
                attributes["vegetable"] = fact.value
            case Dimension.MEAL_TYPE:
                attributes["mealType"] = fact.value
        total_confidence += fact.confidence

    return {
        "domain": Domain.MEAL,
        "type": IntentionType.MEAL_CONSUMPTION,
        "attributes": attributes,
        "confidence": total_confidence / len(meal_facts),
    }

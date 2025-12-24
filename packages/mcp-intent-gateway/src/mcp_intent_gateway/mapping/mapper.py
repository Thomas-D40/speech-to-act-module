"""DeterministicMapper - Pure Python, NO AI/LLM.

Transforms CanonicalFacts into MappingResults deterministically.
"""

from typing import Any, Callable

from ..models.canonical_fact import CanonicalFact
from .activity import map_activity_facts
from .behavior import map_behavior_facts
from .diaper import map_diaper_facts
from .health import map_health_facts
from .meal import map_meal_facts
from .medication import map_medication_facts
from .sleep import map_sleep_facts

# Type alias for mapping functions
MappingFunction = Callable[[list[CanonicalFact]], dict[str, Any] | None]


class DeterministicMapper:
    """
    DeterministicMapper - Pure Python, NO AI/LLM.
    Transforms CanonicalFacts into MappingResults deterministically.
    Same input ALWAYS produces same output.
    """

    def __init__(self) -> None:
        """Initialize the mapper with all domain mapping functions."""
        self._mapping_functions: list[MappingFunction] = [
            map_meal_facts,
            map_sleep_facts,
            map_diaper_facts,
            map_activity_facts,
            map_health_facts,
            map_behavior_facts,
            map_medication_facts,
        ]

    def map(self, facts: list[CanonicalFact]) -> dict[str, Any]:
        """
        Map canonical facts to a mapping result.
        This is 100% deterministic - same input ALWAYS produces same output.

        Args:
            facts: List of canonical facts to map

        Returns:
            Mapping result with domain, type, attributes, and confidence

        Raises:
            ValueError: If facts list is empty or no mapping found
        """
        if not facts:
            raise ValueError("Cannot map empty facts list")

        for mapping_fn in self._mapping_functions:
            result = mapping_fn(facts)
            if result is not None:
                return result

        dimensions = ", ".join(f.dimension.value for f in facts)
        raise ValueError(f"No mapping found for dimensions: {dimensions}")

    def validate_facts(self, facts: list[CanonicalFact]) -> bool:
        """
        Validate that all facts have valid structure.

        Args:
            facts: List of canonical facts to validate

        Returns:
            True if all facts are valid, False otherwise
        """
        return all(
            fact.dimension
            and fact.value
            and isinstance(fact.confidence, float)
            and 0.0 <= fact.confidence <= 1.0
            for fact in facts
        )

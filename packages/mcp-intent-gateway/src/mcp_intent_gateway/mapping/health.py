"""Health mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_health_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map health-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no health facts found
    """
    health_fact = next(
        (f for f in facts if f.dimension == Dimension.HEALTH_STATUS),
        None,
    )

    if not health_fact:
        return None

    return {
        "domain": Domain.HEALTH,
        "type": IntentionType.HEALTH_OBSERVATION,
        "attributes": {"status": health_fact.value},
        "confidence": health_fact.confidence,
    }

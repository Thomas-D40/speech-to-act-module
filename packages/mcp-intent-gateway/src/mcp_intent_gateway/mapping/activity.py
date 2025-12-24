"""Activity mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_activity_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map activity-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no activity facts found
    """
    activity_fact = next(
        (f for f in facts if f.dimension == Dimension.ACTIVITY_TYPE),
        None,
    )

    if not activity_fact:
        return None

    return {
        "domain": Domain.ACTIVITY,
        "type": IntentionType.ACTIVITY_LOG,
        "attributes": {"activityType": activity_fact.value},
        "confidence": activity_fact.confidence,
    }

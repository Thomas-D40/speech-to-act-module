"""Sleep mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_sleep_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map sleep-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no sleep facts found
    """
    sleep_fact = next(
        (f for f in facts if f.dimension == Dimension.SLEEP_STATE),
        None,
    )

    if not sleep_fact:
        return None

    return {
        "domain": Domain.SLEEP,
        "type": IntentionType.SLEEP_LOG,
        "attributes": {"state": sleep_fact.value},
        "confidence": sleep_fact.confidence,
    }

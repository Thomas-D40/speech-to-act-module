"""Diaper mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_diaper_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map diaper-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no diaper facts found
    """
    diaper_fact = next(
        (f for f in facts if f.dimension == Dimension.DIAPER_CHANGE_TYPE),
        None,
    )

    if not diaper_fact:
        return None

    return {
        "domain": Domain.DIAPER,
        "type": IntentionType.DIAPER_CHANGE,
        "attributes": {"changeType": diaper_fact.value},
        "confidence": diaper_fact.confidence,
    }

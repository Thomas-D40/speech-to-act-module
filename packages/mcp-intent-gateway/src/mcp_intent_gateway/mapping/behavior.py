"""Behavior mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_behavior_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map behavior/mood-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no behavior facts found
    """
    mood_fact = next(
        (f for f in facts if f.dimension == Dimension.CHILD_MOOD),
        None,
    )

    if not mood_fact:
        return None

    return {
        "domain": Domain.BEHAVIOR,
        "type": IntentionType.BEHAVIOR_LOG,
        "attributes": {"mood": mood_fact.value},
        "confidence": mood_fact.confidence,
    }

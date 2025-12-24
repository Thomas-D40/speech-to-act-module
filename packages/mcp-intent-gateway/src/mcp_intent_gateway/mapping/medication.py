"""Medication mapping function."""

from typing import Any

from ..domain.constants import Dimension, Domain, IntentionType
from ..models.canonical_fact import CanonicalFact


def map_medication_facts(facts: list[CanonicalFact]) -> dict[str, Any] | None:
    """
    Map medication-related facts to a MappingResult.

    Args:
        facts: List of canonical facts to process

    Returns:
        Mapping result dict or None if no medication facts found
    """
    medication_fact = next(
        (f for f in facts if f.dimension == Dimension.MEDICATION_TYPE),
        None,
    )

    if not medication_fact:
        return None

    return {
        "domain": Domain.MEDICATION,
        "type": IntentionType.MEDICATION_ADMINISTRATION,
        "attributes": {"medicationType": medication_fact.value},
        "confidence": medication_fact.confidence,
    }

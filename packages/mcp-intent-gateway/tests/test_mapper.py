"""Tests for DeterministicMapper."""

import pytest

from mcp_intent_gateway.domain.constants import Dimension, Domain, IntentionType
from mcp_intent_gateway.mapping.mapper import DeterministicMapper
from mcp_intent_gateway.models.canonical_fact import CanonicalFact


class TestDeterministicMapper:
    """Tests for DeterministicMapper class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = DeterministicMapper()

    def test_map_meal_main_consumption(self) -> None:
        """Test mapping MEAL_MAIN_CONSUMPTION."""
        facts = [
            CanonicalFact(
                subjects=["Lucas"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="HALF",
                confidence=0.92,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.MEAL
        assert result["type"] == IntentionType.MEAL_CONSUMPTION
        assert result["attributes"]["main"] == "HALF"
        assert result["confidence"] == 0.92

    def test_map_multiple_meal_facts(self) -> None:
        """Test mapping multiple meal-related facts."""
        facts = [
            CanonicalFact(
                subjects=["Lucas"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="ALL",
                confidence=0.9,
            ),
            CanonicalFact(
                subjects=["Lucas"],
                dimension=Dimension.MEAL_DESSERT_CONSUMPTION,
                value="HALF",
                confidence=0.8,
            ),
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.MEAL
        assert result["attributes"]["main"] == "ALL"
        assert result["attributes"]["dessert"] == "HALF"
        assert result["confidence"] == pytest.approx(0.85)  # Average of 0.9 and 0.8

    def test_map_sleep_state(self) -> None:
        """Test mapping SLEEP_STATE."""
        facts = [
            CanonicalFact(
                subjects=["Léa"],
                dimension=Dimension.SLEEP_STATE,
                value="ASLEEP",
                confidence=0.95,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.SLEEP
        assert result["type"] == IntentionType.SLEEP_LOG
        assert result["attributes"]["state"] == "ASLEEP"

    def test_map_diaper_change(self) -> None:
        """Test mapping DIAPER_CHANGE_TYPE."""
        facts = [
            CanonicalFact(
                subjects=["Nathan"],
                dimension=Dimension.DIAPER_CHANGE_TYPE,
                value="WET",
                confidence=0.98,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.DIAPER
        assert result["type"] == IntentionType.DIAPER_CHANGE
        assert result["attributes"]["changeType"] == "WET"

    def test_map_activity(self) -> None:
        """Test mapping ACTIVITY_TYPE."""
        facts = [
            CanonicalFact(
                subjects=["Jules", "Lina"],
                dimension=Dimension.ACTIVITY_TYPE,
                value="OUTDOOR_PLAY",
                confidence=0.88,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.ACTIVITY
        assert result["type"] == IntentionType.ACTIVITY_LOG
        assert result["attributes"]["activityType"] == "OUTDOOR_PLAY"

    def test_map_health(self) -> None:
        """Test mapping HEALTH_STATUS."""
        facts = [
            CanonicalFact(
                subjects=["Emma"],
                dimension=Dimension.HEALTH_STATUS,
                value="FEVER",
                confidence=0.90,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.HEALTH
        assert result["type"] == IntentionType.HEALTH_OBSERVATION

    def test_map_behavior(self) -> None:
        """Test mapping CHILD_MOOD."""
        facts = [
            CanonicalFact(
                subjects=["Paul"],
                dimension=Dimension.CHILD_MOOD,
                value="HAPPY",
                confidence=0.85,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.BEHAVIOR
        assert result["type"] == IntentionType.BEHAVIOR_LOG

    def test_map_medication(self) -> None:
        """Test mapping MEDICATION_TYPE."""
        facts = [
            CanonicalFact(
                subjects=["Sophie"],
                dimension=Dimension.MEDICATION_TYPE,
                value="PAIN_RELIEVER",
                confidence=0.99,
            )
        ]
        result = self.mapper.map(facts)

        assert result["domain"] == Domain.MEDICATION
        assert result["type"] == IntentionType.MEDICATION_ADMINISTRATION

    def test_map_empty_facts_raises_error(self) -> None:
        """Test that empty facts list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot map empty facts list"):
            self.mapper.map([])

    def test_deterministic_output(self) -> None:
        """Test that same input always produces same output."""
        facts = [
            CanonicalFact(
                subjects=["Nathan"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="THREE_QUARTERS",
                confidence=0.88,
            )
        ]

        result1 = self.mapper.map(facts)
        result2 = self.mapper.map(facts)

        assert result1["domain"] == result2["domain"]
        assert result1["type"] == result2["type"]
        assert result1["attributes"] == result2["attributes"]
        assert result1["confidence"] == result2["confidence"]

    def test_validate_facts_valid(self) -> None:
        """Test validating valid facts."""
        facts = [
            CanonicalFact(
                subjects=["Gabriel"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="HALF",
                confidence=0.92,
            )
        ]
        assert self.mapper.validate_facts(facts) is True

    def test_validate_facts_empty(self) -> None:
        """Test validating empty facts returns True (no invalid facts)."""
        assert self.mapper.validate_facts([]) is True

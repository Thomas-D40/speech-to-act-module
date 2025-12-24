"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from mcp_intent_gateway.domain.constants import Dimension
from mcp_intent_gateway.models.canonical_fact import CanonicalFact
from mcp_intent_gateway.models.intent_contract import IntentContract, IntentContractMetadata
from mcp_intent_gateway.models.responses import ProcessingResult, ValidationError


class TestCanonicalFact:
    """Tests for CanonicalFact model."""

    def test_valid_canonical_fact(self) -> None:
        """Test creating a valid canonical fact."""
        fact = CanonicalFact(
            subjects=["Gabriel"],
            dimension=Dimension.MEAL_MAIN_CONSUMPTION,
            value="ALL",
            confidence=0.92,
        )
        assert fact.subjects == ["Gabriel"]
        assert fact.dimension == Dimension.MEAL_MAIN_CONSUMPTION
        assert fact.value == "ALL"
        assert fact.confidence == 0.92

    def test_canonical_fact_with_multiple_subjects(self) -> None:
        """Test canonical fact with multiple subjects."""
        fact = CanonicalFact(
            subjects=["Gabriel", "Léa"],
            dimension=Dimension.ACTIVITY_TYPE,
            value="OUTDOOR_PLAY",
            confidence=0.88,
        )
        assert len(fact.subjects) == 2

    def test_canonical_fact_default_confidence(self) -> None:
        """Test that confidence defaults to 1.0."""
        fact = CanonicalFact(
            subjects=["Gabriel"],
            dimension=Dimension.SLEEP_STATE,
            value="ASLEEP",
        )
        assert fact.confidence == 1.0

    def test_canonical_fact_invalid_confidence_too_high(self) -> None:
        """Test that confidence > 1.0 raises error."""
        with pytest.raises(PydanticValidationError):
            CanonicalFact(
                subjects=["Gabriel"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="ALL",
                confidence=1.5,
            )

    def test_canonical_fact_invalid_confidence_negative(self) -> None:
        """Test that negative confidence raises error."""
        with pytest.raises(PydanticValidationError):
            CanonicalFact(
                subjects=["Gabriel"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="ALL",
                confidence=-0.1,
            )

    def test_canonical_fact_empty_subjects(self) -> None:
        """Test that empty subjects list raises error."""
        with pytest.raises(PydanticValidationError):
            CanonicalFact(
                subjects=[],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="ALL",
            )

    def test_canonical_fact_invalid_value_for_dimension(self) -> None:
        """Test that invalid value for dimension raises error."""
        with pytest.raises(PydanticValidationError):
            CanonicalFact(
                subjects=["Gabriel"],
                dimension=Dimension.MEAL_MAIN_CONSUMPTION,
                value="INVALID_VALUE",
            )

    def test_canonical_fact_strips_whitespace(self) -> None:
        """Test that subject names are stripped of whitespace."""
        fact = CanonicalFact(
            subjects=["  Gabriel  "],
            dimension=Dimension.MEAL_MAIN_CONSUMPTION,
            value="ALL",
        )
        assert fact.subjects == ["Gabriel"]


class TestIntentContract:
    """Tests for IntentContract model."""

    def test_valid_intent_contract(self) -> None:
        """Test creating a valid intent contract."""
        contract = IntentContract(
            child_id=123,
            action="record_meal",
            properties={"consumption": "ALL"},
        )
        assert contract.child_id == 123
        assert contract.action == "record_meal"
        assert contract.properties == {"consumption": "ALL"}
        assert contract.metadata is None

    def test_intent_contract_with_metadata(self) -> None:
        """Test intent contract with metadata."""
        contract = IntentContract(
            child_id=456,
            action="record_sleep",
            properties={"state": "ASLEEP"},
            metadata=IntentContractMetadata(confidence=0.95),
        )
        assert contract.metadata is not None
        assert contract.metadata.confidence == 0.95
        assert contract.metadata.source == "mcp-intent-gateway"


class TestProcessingResult:
    """Tests for ProcessingResult model."""

    def test_success_result(self) -> None:
        """Test creating a success result."""
        contract = IntentContract(
            child_id=123,
            action="record_meal",
            properties={"consumption": "ALL"},
        )
        result = ProcessingResult(
            success=True,
            message="Event recorded for Gabriel",
            intent_contract=contract,
        )
        assert result.success is True
        assert result.intent_contract is not None
        assert result.errors is None

    def test_failure_result(self) -> None:
        """Test creating a failure result."""
        result = ProcessingResult(
            success=False,
            message="Validation failed",
            errors=[
                ValidationError(
                    field="value",
                    message="Invalid value",
                    code="INVALID_VALUE",
                )
            ],
        )
        assert result.success is False
        assert result.intent_contract is None
        assert result.errors is not None
        assert len(result.errors) == 1

    def test_result_serialization(self) -> None:
        """Test that result can be serialized to dict."""
        result = ProcessingResult(
            success=True,
            message="Success",
        )
        data = result.model_dump()
        assert "success" in data
        assert "message" in data

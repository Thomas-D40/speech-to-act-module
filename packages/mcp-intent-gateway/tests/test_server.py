"""Tests for MCP server tools."""

import pytest

from mcp_intent_gateway.server import (
    get_valid_dimensions,
    health_check,
    process_canonical_fact,
)


class TestProcessCanonicalFact:
    """Tests for process_canonical_fact tool."""

    @pytest.mark.asyncio
    async def test_process_meal_fact_success(self) -> None:
        """Test processing a valid meal fact."""
        result = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
            confidence=0.92,
        )

        assert result["success"] is True
        assert "Gabriel" in result["message"]
        assert result["intent_contract"] is not None
        assert result["intent_contract"]["action"] == "record_meal"
        assert result["intent_contract"]["properties"]["main"] == "ALL"

    @pytest.mark.asyncio
    async def test_process_sleep_fact_success(self) -> None:
        """Test processing a valid sleep fact."""
        result = await process_canonical_fact(
            subjects=["Léa"],
            dimension="SLEEP_STATE",
            value="ASLEEP",
            confidence=0.95,
        )

        assert result["success"] is True
        assert result["intent_contract"]["action"] == "record_sleep"
        assert result["intent_contract"]["properties"]["state"] == "ASLEEP"

    @pytest.mark.asyncio
    async def test_process_invalid_dimension(self) -> None:
        """Test processing with invalid dimension."""
        result = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="INVALID_DIMENSION",
            value="ALL",
        )

        assert result["success"] is False
        assert "Invalid dimension" in result["message"]
        assert result["errors"] is not None
        assert result["errors"][0]["code"] == "INVALID_DIMENSION"

    @pytest.mark.asyncio
    async def test_process_invalid_value(self) -> None:
        """Test processing with invalid value for dimension."""
        result = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="INVALID_VALUE",
        )

        assert result["success"] is False
        assert "Invalid value" in result["message"]
        assert result["errors"] is not None
        assert result["errors"][0]["code"] == "INVALID_VALUE"

    @pytest.mark.asyncio
    async def test_process_empty_subjects(self) -> None:
        """Test processing with empty subjects list."""
        result = await process_canonical_fact(
            subjects=[],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
        )

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_process_default_confidence(self) -> None:
        """Test that default confidence is 1.0."""
        result = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_process_multiple_subjects(self) -> None:
        """Test processing with multiple subjects (uses first one)."""
        result = await process_canonical_fact(
            subjects=["Gabriel", "Léa"],
            dimension="ACTIVITY_TYPE",
            value="OUTDOOR_PLAY",
        )

        assert result["success"] is True
        # Should use first subject for child lookup
        assert "Gabriel" in result["message"]


class TestGetValidDimensions:
    """Tests for get_valid_dimensions tool."""

    @pytest.mark.asyncio
    async def test_get_valid_dimensions(self) -> None:
        """Test getting valid dimensions."""
        result = await get_valid_dimensions()

        assert "dimensions" in result
        assert "MEAL_MAIN_CONSUMPTION" in result["dimensions"]
        assert "SLEEP_STATE" in result["dimensions"]

        # Check structure of dimension info
        meal_dim = result["dimensions"]["MEAL_MAIN_CONSUMPTION"]
        assert "valid_values" in meal_dim
        assert "ALL" in meal_dim["valid_values"]
        assert "HALF" in meal_dim["valid_values"]


class TestHealthCheck:
    """Tests for health_check tool."""

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        """Test health check returns expected structure."""
        result = await health_check()

        assert result["status"] == "ok"
        assert result["service"] == "mcp-intent-gateway"
        assert "backend_available" in result
        assert "backend_url" in result

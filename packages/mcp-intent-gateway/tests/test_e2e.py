"""End-to-end tests using example files from REFACTO_MCP.md."""

import json
from pathlib import Path

import pytest

from mcp_intent_gateway.server import process_canonical_fact

EXAMPLES_DIR = Path(__file__).parent / "examples"


class TestE2EExamples:
    """End-to-end tests based on examples from REFACTO_MCP.md."""

    @pytest.mark.asyncio
    async def test_meal_example(self) -> None:
        """
        Test Example 1 - Meal Event.

        Input CanonicalFact from LLM:
        {
          "subjects": ["Gabriel"],
          "dimension": "MEAL_MAIN_CONSUMPTION",
          "value": "ALL"
        }

        Expected IntentContract:
        IntentContract(
            child_id=<resolved>,
            action="record_meal",
            properties={"main": "ALL"}
        )
        """
        # Load example
        with open(EXAMPLES_DIR / "meal_example.json") as f:
            example = json.load(f)

        # Process the canonical fact
        input_fact = example["input"]["canonical_fact"]
        result = await process_canonical_fact(
            subjects=input_fact["subjects"],
            dimension=input_fact["dimension"],
            value=input_fact["value"],
            confidence=input_fact.get("confidence", 1.0),
        )

        # Verify success
        assert result["success"] is True, f"Expected success, got: {result}"

        # Verify intent contract
        contract = result["intent_contract"]
        assert contract is not None
        assert contract["action"] == "record_meal"
        assert contract["properties"]["main"] == "ALL"
        assert contract["child_id"] is not None

    @pytest.mark.asyncio
    async def test_sleep_example(self) -> None:
        """
        Test Example 2 - Sleep Event.

        Input CanonicalFact from LLM:
        {
          "subjects": ["Léa"],
          "dimension": "SLEEP_STATE",
          "value": "ASLEEP"
        }

        Expected IntentContract:
        IntentContract(
            child_id=<resolved>,
            action="record_sleep",
            properties={"state": "ASLEEP"}
        )
        """
        # Load example
        with open(EXAMPLES_DIR / "sleep_example.json") as f:
            example = json.load(f)

        # Process the canonical fact
        input_fact = example["input"]["canonical_fact"]
        result = await process_canonical_fact(
            subjects=input_fact["subjects"],
            dimension=input_fact["dimension"],
            value=input_fact["value"],
            confidence=input_fact.get("confidence", 1.0),
        )

        # Verify success
        assert result["success"] is True, f"Expected success, got: {result}"

        # Verify intent contract
        contract = result["intent_contract"]
        assert contract is not None
        assert contract["action"] == "record_sleep"
        assert contract["properties"]["state"] == "ASLEEP"
        assert contract["child_id"] is not None

    @pytest.mark.asyncio
    async def test_deterministic_child_id_resolution(self) -> None:
        """Test that same child name always resolves to same ID."""
        result1 = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
        )
        result2 = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="SLEEP_STATE",
            value="ASLEEP",
        )

        # Same child name should always get same ID
        assert result1["intent_contract"]["child_id"] == result2["intent_contract"]["child_id"]

    @pytest.mark.asyncio
    async def test_different_children_get_different_ids(self) -> None:
        """Test that different child names get different IDs."""
        result1 = await process_canonical_fact(
            subjects=["Gabriel"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
        )
        result2 = await process_canonical_fact(
            subjects=["Léa"],
            dimension="MEAL_MAIN_CONSUMPTION",
            value="ALL",
        )

        # Different children should get different IDs
        assert result1["intent_contract"]["child_id"] != result2["intent_contract"]["child_id"]

"""Tests for normalizer module."""
import pytest
from unittest.mock import MagicMock, patch
from semantic_normalization.normalizer import SemanticNormalizer, NormalizationResult


class MockToolCall:
    """Mock OpenAI tool call."""
    def __init__(self, name: str, arguments: str):
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments


class MockMessage:
    """Mock OpenAI message with tool calls."""
    def __init__(self, tool_calls: list):
        self.tool_calls = tool_calls


class MockChoice:
    """Mock OpenAI choice."""
    def __init__(self, message):
        self.message = message


class MockResponse:
    """Mock OpenAI response."""
    def __init__(self, tool_calls: list):
        self.choices = [MockChoice(MockMessage(tool_calls))]


@pytest.fixture
def normalizer():
    """Create a normalizer instance with fallback schema."""
    # Provide a dummy API key for testing
    return SemanticNormalizer(api_key="sk-test-dummy-key-for-testing")


def test_normalize_meal_consumption(normalizer):
    """Test that meal utterance produces correct tool call."""
    with patch.object(normalizer.client.chat.completions, 'create') as mock_create:
        # Mock OpenAI response with tool call
        mock_create.return_value = MockResponse([
            MockToolCall(
                name="process_canonical_fact",
                arguments='{"subjects": ["Gabriel"], "dimension": "MEAL_MAIN_CONSUMPTION", "value": "ALL", "confidence": 0.95}'
            )
        ])

        tool_calls, rag_context = normalizer.normalize("Gabriel a tout mangé")

        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "process_canonical_fact"
        assert tool_calls[0]["arguments"]["dimension"] == "MEAL_MAIN_CONSUMPTION"
        assert tool_calls[0]["arguments"]["value"] == "ALL"
        assert tool_calls[0]["arguments"]["subjects"] == ["Gabriel"]
        assert isinstance(rag_context, str)


def test_normalize_no_tool_calls(normalizer):
    """Test handling of response with no tool calls."""
    with patch.object(normalizer.client.chat.completions, 'create') as mock_create:
        # Mock OpenAI response with no tool calls
        mock_create.return_value = MockResponse([])

        tool_calls, rag_context = normalizer.normalize("invalid input")

        assert len(tool_calls) == 0
        assert isinstance(rag_context, str)


@pytest.mark.asyncio
async def test_normalize_and_dispatch_success(normalizer):
    """Test successful normalization and dispatch."""
    from unittest.mock import AsyncMock

    # Mock the normalize method
    with patch.object(normalizer, 'normalize') as mock_normalize:
        mock_normalize.return_value = (
            [{
                "name": "process_canonical_fact",
                "arguments": {
                    "subjects": ["Gabriel"],
                    "dimension": "MEAL_MAIN_CONSUMPTION",
                    "value": "ALL",
                    "confidence": 0.95
                }
            }],
            "RAG context here"
        )

        # Mock MCP client with async method
        mock_client = MagicMock()
        mock_client.execute_tool_call = AsyncMock(return_value={
            "success": True,
            "message": "Event recorded"
        })

        result = await normalizer.normalize_and_dispatch("Gabriel a tout mangé", mock_client)

        assert isinstance(result, NormalizationResult)
        assert result.input_text == "Gabriel a tout mangé"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].success is True
        assert result.all_succeeded is True

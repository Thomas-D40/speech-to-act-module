"""Tests for tool_schema module."""
import pytest
from semantic_normalization.tool_schema import (
    mcp_to_openai_tool,
    get_fallback_schema,
    clear_cache,
)


def test_mcp_to_openai_tool():
    """Test conversion from MCP tool schema to OpenAI format."""
    mcp_tool = {
        "name": "process_canonical_fact",
        "description": "Process a canonical fact",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subjects": {"type": "array"},
                "dimension": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["subjects", "dimension", "value"]
        }
    }

    openai_tool = mcp_to_openai_tool(mcp_tool)

    assert openai_tool["type"] == "function"
    assert openai_tool["function"]["name"] == "process_canonical_fact"
    assert openai_tool["function"]["description"] == "Process a canonical fact"
    assert openai_tool["function"]["parameters"] == mcp_tool["inputSchema"]


def test_get_fallback_schema():
    """Test fallback schema structure."""
    schema = get_fallback_schema()

    assert isinstance(schema, list)
    assert len(schema) == 1
    assert schema[0]["type"] == "function"
    assert schema[0]["function"]["name"] == "process_canonical_fact"
    assert "parameters" in schema[0]["function"]

    # Check required properties
    params = schema[0]["function"]["parameters"]
    assert "subjects" in params["properties"]
    assert "dimension" in params["properties"]
    assert "value" in params["properties"]
    assert "confidence" in params["properties"]
    assert params["required"] == ["subjects", "dimension", "value"]


def test_clear_cache():
    """Test cache clearing."""
    # Import the cache variable
    from semantic_normalization import tool_schema

    # Set cache
    tool_schema._CACHED_SCHEMA = [{"test": "data"}]
    assert tool_schema._CACHED_SCHEMA is not None

    # Clear cache
    clear_cache()
    assert tool_schema._CACHED_SCHEMA is None

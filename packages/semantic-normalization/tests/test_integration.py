"""Integration tests for end-to-end flow."""
import pytest
from semantic_normalization.normalizer import SemanticNormalizer
from semantic_normalization.mcp_client import IntentGatewayClient
from semantic_normalization.tool_schema import fetch_tool_schema_from_gateway


@pytest.mark.asyncio
@pytest.mark.integration
async def test_end_to_end_with_gateway():
    """
    Full pipeline: RAG → LLM → MCP Gateway → Backend

    NOTE: This test requires:
    - OpenAI API key set in environment
    - MCP gateway server available
    - Mock backend running
    """
    pytest.skip("Requires OpenAI API key and running gateway")

    async with IntentGatewayClient() as mcp_client:
        # Fetch tool schema from gateway
        tool_schema = await fetch_tool_schema_from_gateway(mcp_client)

        # Create normalizer with gateway schema
        normalizer = SemanticNormalizer(tool_schema=tool_schema)

        # Test normalization and dispatch
        result = await normalizer.normalize_and_dispatch(
            "Gabriel a tout mangé",
            mcp_client
        )

        assert result.all_succeeded
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].success
        assert result.tool_calls[0].gateway_response["success"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_gateway_connection():
    """Test basic MCP gateway connection."""
    pytest.skip("Requires running gateway")

    async with IntentGatewayClient() as mcp_client:
        # Fetch schema to verify connection
        tool_schema = await fetch_tool_schema_from_gateway(mcp_client)

        assert isinstance(tool_schema, list)
        assert len(tool_schema) > 0
        assert tool_schema[0]["function"]["name"] == "process_canonical_fact"

"""
Fetches and converts MCP tool schema for OpenAI function calling.
"""
from typing import Any


# Cached schema for the session
_CACHED_SCHEMA: list[dict[str, Any]] | None = None


def mcp_to_openai_tool(mcp_tool: dict) -> dict:
    """
    Convert MCP tool schema to OpenAI function calling format.

    MCP format:
    {
        "name": "process_canonical_fact",
        "description": "...",
        "inputSchema": {"type": "object", "properties": {...}}
    }

    OpenAI format:
    {
        "type": "function",
        "function": {
            "name": "process_canonical_fact",
            "description": "...",
            "parameters": {"type": "object", "properties": {...}}
        }
    }
    """
    return {
        "type": "function",
        "function": {
            "name": mcp_tool["name"],
            "description": mcp_tool.get("description", ""),
            "parameters": mcp_tool.get("inputSchema", {"type": "object", "properties": {}})
        }
    }


async def fetch_tool_schema_from_gateway(mcp_client) -> list[dict]:
    """
    Fetch tool schemas from MCP gateway and convert to OpenAI format.

    Args:
        mcp_client: MCP client session (StdioServerParameters context)

    Returns:
        List of OpenAI tool schemas
    """
    global _CACHED_SCHEMA

    if _CACHED_SCHEMA is not None:
        return _CACHED_SCHEMA

    tools_result = await mcp_client.list_tools()

    openai_tools = []
    for tool in tools_result.tools:
        if tool.name == "process_canonical_fact":
            openai_tools.append(mcp_to_openai_tool({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }))

    _CACHED_SCHEMA = openai_tools
    return openai_tools


def get_fallback_schema() -> list[dict]:
    """
    Fallback schema for testing without gateway.
    This should match the gateway's process_canonical_fact exactly.
    """
    return [{
        "type": "function",
        "function": {
            "name": "process_canonical_fact",
            "description": "Process a canonical fact extracted from natural language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subjects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of child names (e.g., ['Gabriel'])"
                    },
                    "dimension": {
                        "type": "string",
                        "description": "The dimension type (e.g., 'MEAL_MAIN_CONSUMPTION')"
                    },
                    "value": {
                        "type": "string",
                        "description": "The value for the dimension (e.g., 'ALL')"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score 0-1",
                        "default": 1.0
                    }
                },
                "required": ["subjects", "dimension", "value"]
            }
        }
    }]


def clear_cache():
    """Clear the cached schema (useful for testing)."""
    global _CACHED_SCHEMA
    _CACHED_SCHEMA = None

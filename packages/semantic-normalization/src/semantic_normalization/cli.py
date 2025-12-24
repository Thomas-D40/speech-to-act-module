"""
CLI for testing semantic normalization
"""

import sys
import json
from dotenv import load_dotenv
from .normalizer import SemanticNormalizer
from .mcp_client import IntentGatewayClient


def main():
    """Main CLI entry point for simple normalization (no MCP dispatch)"""
    # Load environment variables
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python -m semantic_normalization.cli \"<text to normalize>\"")
        print("Example: python -m semantic_normalization.cli \"il a mangé la moitié\"")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])

    # Initialize normalizer
    normalizer = SemanticNormalizer()

    # Normalize (returns tool calls without executing them)
    print(f"Input: {input_text}")
    print("-" * 50)

    try:
        tool_calls, rag_context = normalizer.normalize(input_text)

        result = {
            "input": input_text,
            "rag_context": rag_context,
            "tool_calls": tool_calls
        }

        print(json.dumps(result, indent=2, ensure_ascii=True))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main_with_dispatch():
    """Main entry point with MCP dispatch (async)"""
    # Load environment variables
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python -m semantic_normalization.cli \"<text to normalize>\"")
        print("Example: python -m semantic_normalization.cli \"Gabriel a tout mangé\"")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])

    print(f"Input: {input_text}")
    print("-" * 50)

    try:
        # Connect to MCP gateway
        async with IntentGatewayClient() as mcp_client:
            # Get tool schema from gateway
            from .tool_schema import fetch_tool_schema_from_gateway
            tool_schema = await fetch_tool_schema_from_gateway(mcp_client)

            # Initialize normalizer with gateway schema
            normalizer = SemanticNormalizer(tool_schema=tool_schema)

            # Normalize and dispatch
            result = await normalizer.normalize_and_dispatch(input_text, mcp_client)

            # Print results
            output = {
                "input": result.input_text,
                "rag_context": result.rag_context,
                "tool_calls": [
                    {
                        "tool_name": tc.tool_name,
                        "arguments": tc.arguments,
                        "success": tc.success,
                        "gateway_response": tc.gateway_response,
                        "error": tc.error
                    }
                    for tc in result.tool_calls
                ],
                "all_succeeded": result.all_succeeded
            }

            print(json.dumps(output, indent=2, ensure_ascii=True))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Default to simple normalization without dispatch
    main()
    # Uncomment below to use dispatch mode instead:
    # asyncio.run(main_with_dispatch())

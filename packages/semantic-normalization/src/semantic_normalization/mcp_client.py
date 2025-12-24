"""
MCP Client for Intent Gateway communication.
"""
import json
import logging
import os
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .tool_schema import fetch_tool_schema_from_gateway

logger = logging.getLogger(__name__)


class IntentGatewayClient:
    """
    MCP client for the Intent Gateway.

    Manages connection to the MCP gateway subprocess and provides
    methods for executing tool calls.

    Usage:
        async with IntentGatewayClient() as client:
            result = await client.execute_tool_call("process_canonical_fact", {...})
    """

    def __init__(self, gateway_module: str = "mcp_intent_gateway.server"):
        """
        Initialize the MCP client.

        Args:
            gateway_module: Python module path for the gateway server
        """
        self.gateway_module = gateway_module
        self.session: ClientSession | None = None
        self._stdio_context = None
        self._read = None
        self._write = None

    async def __aenter__(self):
        """Enter async context manager - start MCP subprocess."""
        logger.info(f"Starting MCP gateway subprocess: {self.gateway_module}")

        # Determine Python executable
        # Use the virtual environment's Python if available
        python_exe = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            python_exe = "python"

        # Create server parameters
        server_params = StdioServerParameters(
            command=python_exe,
            args=["-m", self.gateway_module],
            env=None,
        )

        # Start stdio client
        self._stdio_context = stdio_client(server_params)
        self._read, self._write = await self._stdio_context.__aenter__()

        # Initialize session
        self.session = ClientSession(self._read, self._write)
        await self.session.__aenter__()

        # Initialize the session
        await self.session.initialize()

        logger.info("MCP gateway connected successfully")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager - close MCP subprocess."""
        logger.info("Closing MCP gateway connection")

        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)

        if self._stdio_context:
            await self._stdio_context.__aexit__(exc_type, exc_val, exc_tb)

        self.session = None
        self._stdio_context = None
        self._read = None
        self._write = None

    async def get_tool_schema(self) -> list[dict]:
        """
        Fetch tool schema from gateway.

        Returns:
            List of OpenAI-formatted tool schemas
        """
        if not self.session:
            raise RuntimeError("Client not connected. Use async with context manager.")

        return await fetch_tool_schema_from_gateway(self.session)

    async def execute_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a tool call against the MCP gateway.

        Args:
            tool_name: Name of the tool to call (e.g., "process_canonical_fact")
            arguments: Tool arguments as a dictionary

        Returns:
            Tool result as a dictionary

        Raises:
            RuntimeError: If client not connected
            Exception: If tool call fails
        """
        if not self.session:
            raise RuntimeError("Client not connected. Use async with context manager.")

        logger.info(f"Executing tool call: {tool_name} with args: {arguments}")

        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)

            # MCP returns a CallToolResult with content list
            # Each content item is a TextContent or ImageContent
            # For our case, we expect TextContent with JSON
            if not result.content:
                raise ValueError("Empty response from tool call")

            # Extract the text content
            content = result.content[0]
            if hasattr(content, 'text'):
                response_data = json.loads(content.text)
                logger.info(f"Tool call successful: {response_data.get('message', 'No message')}")
                return response_data
            else:
                raise ValueError(f"Unexpected content type: {type(content)}")

        except Exception as e:
            logger.error(f"Tool call failed: {e}", exc_info=True)
            raise

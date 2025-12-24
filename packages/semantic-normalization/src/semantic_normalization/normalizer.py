"""
Semantic normalizer using OpenAI function calling with MCP tools.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import OpenAI

from .mcp_client import IntentGatewayClient
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .rag_interface import RAGRetriever, VectorRAGRetriever, CompatibilityRAGRetriever
from .tool_schema import get_fallback_schema

logger = logging.getLogger(__name__)


@dataclass
class ToolCallResult:
    """Result of a single tool call."""
    tool_name: str
    arguments: dict[str, Any]
    gateway_response: dict[str, Any] | None = None
    success: bool = False
    error: str | None = None


@dataclass
class NormalizationResult:
    """Complete result of normalization and dispatch."""
    input_text: str
    rag_context: str
    tool_calls: list[ToolCallResult] = field(default_factory=list)
    all_succeeded: bool = False


class SemanticNormalizer:
    """
    LLM-based normalizer that uses function calling to invoke MCP tools.

    Domain knowledge flows:
    1. RAG provides semantic context (phrase → dimension/value hints)
    2. MCP tool schema defines the available functions
    3. LLM decides which tool(s) to call based on input
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        rag_retriever: Optional[RAGRetriever] = None,
        compatibility_rag_retriever: Optional[RAGRetriever] = None,  # NEW
        tool_schema: Optional[list[dict]] = None,  # From gateway or fallback
    ):
        """
        Initialize the semantic normalizer.

        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model to use
            temperature: Temperature for generation (0 = deterministic)
            rag_retriever: RAG retriever instance (defaults to VectorRAGRetriever)
            compatibility_rag_retriever: Compatibility RAG retriever (defaults to CompatibilityRAGRetriever)
            tool_schema: OpenAI tool schema (defaults to fallback schema)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.rag_retriever = rag_retriever or VectorRAGRetriever()
        self.compatibility_rag_retriever = compatibility_rag_retriever or CompatibilityRAGRetriever()  # NEW
        self.tool_schema = tool_schema or get_fallback_schema()

    def _extract_dimension_hints(self, lexical_context: str) -> list[str]:
        """
        Extract dimension keywords from lexical RAG context.
        Simple regex to find dimension names (e.g., "MEAL_MAIN_CONSUMPTION").

        Args:
            lexical_context: RAG context string with dimension mentions

        Returns:
            List of detected dimension names
        """
        import re
        # Pattern: UPPERCASE_WORDS with underscores
        dimensions = re.findall(r'\b[A-Z_]{3,}\b', lexical_context)
        # Deduplicate and filter known dimensions
        return list(set(dimensions))

    def _build_messages(self, input_text: str) -> tuple[list[dict], str]:
        """
        Build messages with DUAL RAG context (lexical + compatibility).

        Args:
            input_text: Raw text to classify

        Returns:
            Tuple of (messages, combined_context_for_debugging)
        """
        # 1. Get lexical context (existing)
        lexical_context = self.rag_retriever.retrieve_context(input_text)

        # 2. Extract dimension hints from lexical context
        detected_dimensions = self._extract_dimension_hints(lexical_context)

        # 3. Get compatibility context
        compatibility_context = ""
        if detected_dimensions:
            # Query with space-separated dimensions
            dimension_query = " ".join(detected_dimensions)
            compatibility_context = self.compatibility_rag_retriever.retrieve_context(
                dimension_query,
                top_k=3
            )

        # 4. Build combined context
        combined_context = lexical_context
        if compatibility_context:
            combined_context += f"\n\n{compatibility_context}"

        # 5. Inject into prompt
        user_content = USER_PROMPT_TEMPLATE.format(
            rag_context=combined_context,  # Combined lexical + compatibility
            input_text=input_text
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        return messages, combined_context

    def normalize(self, input_text: str) -> tuple[list[dict], str]:
        """
        Normalize text and return tool calls (not executed).

        Args:
            input_text: Raw text utterance

        Returns:
            Tuple of (tool_calls, rag_context)
        """
        messages, rag_context = self._build_messages(input_text)

        # Call OpenAI with function calling
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_schema,
            tool_choice="auto",  # Let LLM decide
            temperature=self.temperature,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            logger.warning(f"No tool calls for input: {input_text}")
            return [], rag_context

        # Extract tool calls
        tool_calls = []
        for tc in message.tool_calls:
            tool_calls.append({
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments)
            })

        return tool_calls, rag_context

    async def normalize_and_dispatch(
        self,
        input_text: str,
        mcp_client: IntentGatewayClient
    ) -> NormalizationResult:
        """
        Normalize text and dispatch tool calls to MCP gateway.

        This is the main entry point for the integrated workflow.

        Args:
            input_text: Raw text utterance
            mcp_client: Connected MCP client instance

        Returns:
            NormalizationResult with tool call results
        """
        tool_calls, rag_context = self.normalize(input_text)

        result = NormalizationResult(
            input_text=input_text,
            rag_context=rag_context,
        )

        if not tool_calls:
            result.all_succeeded = True  # No calls = vacuously true
            return result

        # Execute each tool call against MCP gateway
        for tc in tool_calls:
            tc_result = ToolCallResult(
                tool_name=tc["name"],
                arguments=tc["arguments"]
            )

            try:
                gateway_response = await mcp_client.execute_tool_call(
                    tc["name"],
                    tc["arguments"]
                )
                tc_result.gateway_response = gateway_response
                tc_result.success = gateway_response.get("success", False)
            except Exception as e:
                tc_result.error = str(e)
                tc_result.success = False
                logger.error(f"Tool call execution failed: {e}", exc_info=True)

            result.tool_calls.append(tc_result)

        result.all_succeeded = all(tc.success for tc in result.tool_calls)
        return result

name: "Connect Semantic Normalization to MCP Intent Gateway"
description: |

## Purpose
Integrate the `semantic-normalization` module with the `mcp-intent-gateway` using a **domain-agnostic architecture** where:
1. Domain knowledge (dimensions, values) comes from the **RAG vector database** (not hardcoded)
2. The **CanonicalFact schema is derived from the MCP tool** exposed by the gateway
3. The **LLM directly calls the MCP tool** via OpenAI function/tool calling

## Core Principles
1. **No domain knowledge in semantic-normalizer**: All dimension/value information comes from RAG or MCP tool schema
2. **MCP tool schema IS the contract**: The `process_canonical_fact` tool defines what CanonicalFact looks like
3. **LLM uses function calling**: OpenAI's tool/function calling invokes the MCP tool directly
4. **Single source of truth**: Gateway owns the schema; RAG provides semantic mappings

---

## Goal
Refactor the `semantic-normalization` module to:
1. Remove hardcoded domain constants (dimensions, values)
2. Use RAG to provide semantic context for the LLM
3. Fetch the MCP tool schema from the gateway dynamically
4. Use OpenAI function calling with the MCP tool as the available function
5. Execute tool calls against the MCP gateway and return results

## Why
- **Zero domain coupling**: Adding new dimensions/values requires NO changes to semantic-normalizer
- **Single source of truth**: Gateway defines the schema, RAG provides the lexicon
- **Native LLM integration**: OpenAI function calling is designed for tool invocation
- **Testability**: Mock the MCP tool schema for testing without gateway

## What
The semantic-normalizer workflow becomes:
1. Receive speech-to-text input
2. Query RAG for semantic context (French phrases → dimension/value hints)
3. Fetch MCP tool schema (`get_valid_dimensions` or tool list)
4. Call OpenAI with the tool schema as available functions
5. LLM produces tool call(s) to `process_canonical_fact`
6. Execute each tool call against MCP gateway
7. Return aggregated results

### Success Criteria
- [ ] `semantic-normalization/constants.py` is DELETED or contains NO dimension/value definitions
- [ ] LLM prompt uses ONLY RAG-provided context for domain knowledge
- [ ] OpenAI function calling is used with MCP tool schema
- [ ] End-to-end test passes: speech → RAG → LLM → MCP tool → backend
- [ ] All linting/type checks pass

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://platform.openai.com/docs/guides/function-calling
  why: OpenAI function/tool calling - how to pass tool schemas and handle tool_calls
  critical: |
    The LLM receives tools as JSON schema and returns tool_calls:
    ```python
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{
            "type": "function",
            "function": {
                "name": "process_canonical_fact",
                "parameters": {...}  # From MCP tool schema
            }
        }]
    )
    tool_call = response.choices[0].message.tool_calls[0]
    ```

- url: https://github.com/modelcontextprotocol/python-sdk
  why: MCP Python SDK - list_tools() to get schema, call_tool() to execute

- file: packages/mcp-intent-gateway/src/mcp_intent_gateway/server.py
  why: |
    The MCP tool `process_canonical_fact` defines the CanonicalFact schema:
    - subjects: list[str]
    - dimension: str
    - value: str
    - confidence: float
    The tool `get_valid_dimensions` returns all valid dimension/value pairs.

- file: packages/rag-knowledge-base/data/initial_lexicon.json
  why: |
    AUTHORITATIVE source of French phrase → dimension/value mappings.
    This is embedded into ChromaDB and retrieved by RAG.
    Structure: { "DIMENSION": { "VALUE": ["phrase1", "phrase2", ...] } }

- file: packages/semantic-normalization/src/semantic_normalization/rag_interface.py
  why: |
    VectorRAGRetriever.retrieve_context() returns formatted context:
    "RELEVANT KNOWLEDGE (Semantic Match):
    - 'tout mangé' → MEAL_MAIN_CONSUMPTION: ALL (dist: 0.15)"

- file: packages/semantic-normalization/src/semantic_normalization/normalizer.py
  why: Current implementation to refactor - remove hardcoded schema dependency
```

### Current Codebase Tree
```bash
packages/
├── rag-knowledge-base/
│   ├── data/
│   │   └── initial_lexicon.json      # AUTHORITATIVE: phrase → dimension/value mappings
│   ├── src/
│   │   └── init_vector_db.py         # Embeds lexicon into ChromaDB
│   └── dist/
│       └── vector_store/             # ChromaDB persistent store
│
├── mcp-intent-gateway/
│   ├── src/mcp_intent_gateway/
│   │   ├── server.py                 # MCP tools: process_canonical_fact, get_valid_dimensions
│   │   ├── domain/constants.py       # Dimension enum, DIMENSION_VALUES
│   │   └── models/canonical_fact.py  # Pydantic model (for gateway validation)
│   └── tests/
│
├── semantic-normalization/
│   ├── src/semantic_normalization/
│   │   ├── normalizer.py             # TO REFACTOR: remove schema dependency
│   │   ├── models.py                 # TO DELETE: local CanonicalFact
│   │   ├── constants.py              # TO DELETE: hardcoded dimensions
│   │   ├── prompts.py                # TO REFACTOR: remove hardcoded values
│   │   └── rag_interface.py          # KEEP: RAG retrieval
│   └── pyproject.toml
```

### Desired Codebase Tree
```bash
packages/semantic-normalization/
├── src/semantic_normalization/
│   ├── __init__.py
│   ├── normalizer.py                 # REFACTORED: uses function calling + MCP
│   ├── mcp_client.py                 # NEW: MCP client wrapper
│   ├── tool_schema.py                # NEW: Fetches/caches tool schema from gateway
│   ├── prompts.py                    # REFACTORED: domain-agnostic prompts
│   ├── rag_interface.py              # UNCHANGED
│   └── cli.py
│   # DELETED: models.py, constants.py
├── tests/
│   ├── test_normalizer.py
│   ├── test_mcp_client.py
│   └── test_integration.py
└── pyproject.toml                    # ADD: mcp>=1.0.0
```

### Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA #1: RAG LEXICON vs GATEWAY VALUES MISMATCH
# The rag-knowledge-base/initial_lexicon.json uses some values that
# don't exist in the gateway's DIMENSION_VALUES:
#
# Lexicon has:                     Gateway expects:
# -----------                      ----------------
# "NONE"                           "NOTHING"
# "NAP_START", "NAP_END"           "ASLEEP", "WOKE_UP", "RESTING", "REFUSED_SLEEP"
# "MORNING_SNACK", "AFTERNOON_SNACK"  "SNACK"
# "FUSSY", "CRYING", "ENERGETIC"   "UPSET", "CRANKY", "EXCITED"
#
# SOLUTION: Update initial_lexicon.json to use gateway-valid values,
# then rebuild the vector database with init_vector_db.py

# CRITICAL GOTCHA #2: OpenAI Function Calling Response Structure
# The response contains tool_calls, not direct content:
response.choices[0].message.tool_calls[0].function.name  # "process_canonical_fact"
response.choices[0].message.tool_calls[0].function.arguments  # JSON string!
# MUST parse: json.loads(tool_call.function.arguments)

# CRITICAL GOTCHA #3: MCP Tool Schema Format
# MCP tools use JSON Schema for parameters. Convert to OpenAI format:
# MCP: tool.inputSchema = {"type": "object", "properties": {...}}
# OpenAI: {"type": "function", "function": {"name": ..., "parameters": inputSchema}}

# CRITICAL GOTCHA #4: Async/Sync Boundary
# OpenAI client is sync, MCP client is async. Use asyncio.run() or async wrapper.

# CRITICAL GOTCHA #5: Multiple Tool Calls
# LLM may return multiple tool_calls for multi-fact utterances.
# Must iterate: for tool_call in response.choices[0].message.tool_calls
```

## Implementation Blueprint

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        semantic-normalization                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌─────────────┐     ┌───────────────────┐     │
│  │ Speech Text  │────▶│     RAG     │────▶│   OpenAI API      │     │
│  └──────────────┘     │ (ChromaDB)  │     │ (function calling)│     │
│                       └──────┬──────┘     └─────────┬─────────┘     │
│                              │                      │               │
│                              │ context              │ tool_calls    │
│                              ▼                      ▼               │
│                       ┌─────────────────────────────────┐           │
│                       │      LLM Prompt Builder         │           │
│                       │  - RAG context injection        │           │
│                       │  - MCP tool schema as function  │           │
│                       └─────────────────────────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Execute tool_calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       mcp-intent-gateway (MCP Server)                │
├─────────────────────────────────────────────────────────────────────┤
│  Tools:                                                              │
│  - process_canonical_fact(subjects, dimension, value, confidence)    │
│  - get_valid_dimensions() → schema                                   │
│  - health_check()                                                    │
│                                                                      │
│  Responsibilities:                                                   │
│  - Validate dimension/value                                         │
│  - Resolve child entities                                           │
│  - Map to IntentContract                                            │
│  - Call backend API                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### List of Tasks

```yaml
Task 0: Fix RAG Lexicon Values (PREREQUISITE)
MODIFY packages/rag-knowledge-base/data/initial_lexicon.json:
  - UPDATE values to match gateway's DIMENSION_VALUES exactly
  - "NONE" → "NOTHING"
  - "NAP_START"/"NAP_END" → "ASLEEP"/"WOKE_UP" (or remove if no equivalent)
  - "MORNING_SNACK"/"AFTERNOON_SNACK" → "SNACK"
  - "FUSSY"/"CRYING" → "UPSET"/"CRANKY"
  - "ENERGETIC" → "EXCITED"
RUN packages/rag-knowledge-base/src/init_vector_db.py to rebuild embeddings

Task 1: Create Tool Schema Fetcher
CREATE packages/semantic-normalization/src/semantic_normalization/tool_schema.py:
  - Fetch tool schema from MCP gateway via list_tools()
  - Convert MCP schema to OpenAI function format
  - Cache schema to avoid repeated fetches
  - Fallback: hardcoded schema if gateway unavailable (for testing)

Task 2: Create MCP Client Module
CREATE packages/semantic-normalization/src/semantic_normalization/mcp_client.py:
  - IntentGatewayClient class (async context manager)
  - Methods: get_tool_schema(), execute_tool_call(name, args)
  - Handle subprocess lifecycle

Task 3: Refactor Prompts to be Domain-Agnostic
MODIFY packages/semantic-normalization/src/semantic_normalization/prompts.py:
  - REMOVE hardcoded dimension/value lists from SYSTEM_PROMPT
  - ADD placeholder for RAG context injection
  - ADD placeholder for tool schema injection
  - Prompt instructs LLM to use provided tools

Task 4: Refactor Normalizer to Use Function Calling
MODIFY packages/semantic-normalization/src/semantic_normalization/normalizer.py:
  - REMOVE dependency on local CanonicalFact model
  - ADD tool_schema parameter (from gateway or cached)
  - USE OpenAI tools parameter with MCP tool schema
  - PARSE tool_calls from response
  - EXECUTE tool_calls via MCP client
  - RETURN aggregated results

Task 5: Delete Hardcoded Domain Files
DELETE packages/semantic-normalization/src/semantic_normalization/constants.py
DELETE packages/semantic-normalization/src/semantic_normalization/models.py
  - Or keep minimal models.py for response types only

Task 6: Update Dependencies
MODIFY packages/semantic-normalization/pyproject.toml:
  - ADD: "mcp>=1.0.0"
  - ADD: "anyio>=4.0.0" (for async compatibility)

Task 7: Create Unit Tests
CREATE packages/semantic-normalization/tests/test_tool_schema.py
CREATE packages/semantic-normalization/tests/test_mcp_client.py
  - Mock MCP session for unit tests

Task 8: Create Integration Tests
CREATE packages/semantic-normalization/tests/test_integration.py
  - Full pipeline with real RAG, real LLM, real gateway
```

### Task 1: Tool Schema Fetcher - Pseudocode

```python
# packages/semantic-normalization/src/semantic_normalization/tool_schema.py
"""
Fetches and converts MCP tool schema for OpenAI function calling.
"""
from typing import Any
import json

# Cached schema for the session
_CACHED_SCHEMA: dict[str, Any] | None = None


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
    """
    tools_result = await mcp_client.list_tools()

    openai_tools = []
    for tool in tools_result.tools:
        if tool.name == "process_canonical_fact":
            openai_tools.append(mcp_to_openai_tool({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }))

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
```

### Task 3: Domain-Agnostic Prompts - Pseudocode

```python
# packages/semantic-normalization/src/semantic_normalization/prompts.py
"""
Domain-agnostic prompts for semantic normalization.
All domain knowledge comes from RAG context and tool schema.
"""

SYSTEM_PROMPT = """You are a semantic normalization assistant for event tracking system.

Your task is to interpret natural language utterances and call the appropriate tool to record events.

IMPORTANT RULES:
1. Use ONLY the tool provided to record facts
2. Extract child names as subjects (if mentioned, otherwise use ["UNKNOWN"])
3. Use the dimension and value that best matches the utterance
4. Set confidence based on clarity: 0.9+ for clear, 0.5-0.9 for ambiguous
5. If the utterance contains multiple facts, make multiple tool calls
6. The RELEVANT KNOWLEDGE section shows valid dimension/value pairs from similar phrases

DO NOT invent dimensions or values - only use what's available in the tool schema get_valid_dimensions().
If no tool applies, respond with a text message explaining why."""

# RAG context is injected dynamically - no hardcoded values here
USER_PROMPT_TEMPLATE = """
{rag_context}

Classify this utterance and call the appropriate tool:

Input: "{input_text}"
"""

# Examples now use the tool calling format
# Few-shot examples can be added to messages as assistant tool_calls
```

### Task 4: Refactored Normalizer - Pseudocode

```python
# packages/semantic-normalization/src/semantic_normalization/normalizer.py
"""
Semantic normalizer using OpenAI function calling with MCP tools.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from .mcp_client import IntentGatewayClient
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .rag_interface import RAGRetriever, VectorRAGRetriever
from .tool_schema import fetch_tool_schema_from_gateway, get_fallback_schema

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
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        rag_retriever: RAGRetriever | None = None,
        tool_schema: list[dict] | None = None,  # From gateway or fallback
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.rag_retriever = rag_retriever or VectorRAGRetriever()
        self.tool_schema = tool_schema or get_fallback_schema()

    def _build_messages(self, input_text: str) -> list[dict]:
        """Build messages with RAG context."""
        # Get RAG context
        rag_context = self.rag_retriever.retrieve_context(input_text)

        user_content = USER_PROMPT_TEMPLATE.format(
            rag_context=rag_context,
            input_text=input_text
        )

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

    def normalize(self, input_text: str) -> tuple[list[dict], str]:
        """
        Normalize text and return tool calls (not executed).

        Returns:
            Tuple of (tool_calls, rag_context)
        """
        messages = self._build_messages(input_text)
        rag_context = self.rag_retriever.retrieve_context(input_text)

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

            result.tool_calls.append(tc_result)

        result.all_succeeded = all(tc.success for tc in result.tool_calls)
        return result
```

### Integration Points

```yaml
RAG_DATABASE:
  - packages/rag-knowledge-base/data/initial_lexicon.json
    MUST use gateway-valid values
  - Run init_vector_db.py after any lexicon changes

MCP_GATEWAY:
  - Tool: process_canonical_fact(subjects, dimension, value, confidence)
  - Tool: get_valid_dimensions() - for dynamic schema discovery
  - The tool inputSchema IS the CanonicalFact contract

DEPENDENCIES:
  - semantic-normalization/pyproject.toml:
    - ADD: "mcp>=1.0.0"
    - KEEP: "openai>=1.0.0"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
cd packages/semantic-normalization

# Lint
../../.venv/Scripts/ruff.exe check src/ --fix

# Type check
../../.venv/Scripts/mypy.exe src/

# Expected: No errors
```

### Level 2: Unit Tests

```python
# Test that normalizer produces correct tool calls (mocked OpenAI)
def test_normalize_meal_consumption():
    """Test that meal utterance produces correct tool call."""
    with patch.object(OpenAI, 'chat') as mock_chat:
        mock_chat.completions.create.return_value = MockResponse(
            tool_calls=[MockToolCall(
                function=MockFunction(
                    name="process_canonical_fact",
                    arguments='{"subjects": ["Gabriel"], "dimension": "MEAL_MAIN_CONSUMPTION", "value": "ALL", "confidence": 0.95}'
                )
            )]
        )

        normalizer = SemanticNormalizer()
        tool_calls, _ = normalizer.normalize("Gabriel a tout mangé")

        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "process_canonical_fact"
        assert tool_calls[0]["arguments"]["dimension"] == "MEAL_MAIN_CONSUMPTION"
```

```bash
cd packages/semantic-normalization
PYTHONPATH=./src ../../.venv/Scripts/pytest.exe tests/ -v
```

### Level 3: Integration Test

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_end_to_end():
    """Full pipeline: RAG → LLM → MCP Gateway → Backend"""
    async with IntentGatewayClient() as mcp_client:
        # Optionally fetch schema from gateway
        tool_schema = await fetch_tool_schema_from_gateway(mcp_client)

        normalizer = SemanticNormalizer(tool_schema=tool_schema)
        result = await normalizer.normalize_and_dispatch(
            "Gabriel a tout mangé",
            mcp_client
        )

        assert result.all_succeeded
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].gateway_response["success"]
```

## Final Validation Checklist
- [ ] `constants.py` deleted or contains NO dimension definitions
- [ ] `models.py` deleted or contains NO CanonicalFact
- [ ] `prompts.py` contains NO hardcoded dimension/value lists
- [ ] RAG lexicon uses gateway-valid values
- [ ] OpenAI function calling works with MCP tool schema
- [ ] All tests pass
- [ ] End-to-end integration works

---

## Anti-Patterns to Avoid
- **Don't hardcode dimensions/values in semantic-normalizer** - use RAG + tool schema
- **Don't define CanonicalFact locally** - it comes from the MCP tool
- **Don't parse LLM text output** - use tool_calls from function calling
- **Don't validate values in semantic-normalizer** - gateway handles validation
- **Don't maintain parallel constant files** - single source of truth in gateway

---

## Error Handling Strategy

```python
class NormalizationError(Exception):
    """Base exception for normalization errors."""
    pass

class NoToolCallsError(NormalizationError):
    """LLM did not produce any tool calls."""
    pass

class MCPConnectionError(NormalizationError):
    """Cannot connect to MCP gateway."""
    pass

class ToolExecutionError(NormalizationError):
    """Tool call failed (gateway rejection, etc.)."""
    def __init__(self, tool_name: str, arguments: dict, gateway_errors: list):
        self.tool_name = tool_name
        self.arguments = arguments
        self.gateway_errors = gateway_errors
```

Error flow:
1. **RAG errors**: Log warning, continue with empty context
2. **OpenAI errors**: Raise immediately (API failure)
3. **No tool calls**: Return empty result (valid for non-actionable input)
4. **MCP connection errors**: Raise MCPConnectionError
5. **Gateway validation errors**: Captured in ToolCallResult, propagated to caller

---

## Data Synchronization: RAG ↔ Gateway

**CRITICAL**: The RAG lexicon (`initial_lexicon.json`) must use values that the gateway accepts.

| Source | Role | Values |
|--------|------|--------|
| `mcp-intent-gateway/domain/constants.py` | **Authoritative** | Defines valid dimensions/values |
| `rag-knowledge-base/initial_lexicon.json` | Semantic mapping | Maps French phrases to dimension/value |
| `semantic-normalization` | Consumer | Uses RAG context + tool schema |

When adding new dimensions/values:
1. Add to gateway's `constants.py` and `DIMENSION_VALUES`
2. Add French phrases to `initial_lexicon.json`
3. Run `init_vector_db.py` to rebuild embeddings
4. No changes needed in semantic-normalization!

---

## Confidence Score: 8.5/10

**Strengths:**
- Clean separation of concerns (RAG for semantics, gateway for schema)
- Native OpenAI function calling integration
- No hardcoded domain knowledge in semantic layer
- Single source of truth architecture

**Risks:**
- RAG lexicon must be synchronized with gateway values (Task 0)
- OpenAI function calling may produce unexpected tool_calls
- MCP subprocess management on Windows

**Mitigation:**
- Task 0 explicitly fixes lexicon before other work
- Fallback schema for testing without gateway
- Comprehensive error handling

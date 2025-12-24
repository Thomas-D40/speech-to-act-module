## FEATURE:

Semantic Normalization → MCP Intent Gateway Integration (CanonicalFact-based)

This feature connects the **semantic-normalization** module to the **mcp-intent-gateway**.

The semantic-normalizer acts as a **strict LLM wrapper** whose responsibility is limited to:
1. Receiving raw text from speech-to-text
2. Extracting **one or more CanonicalFact objects**
3. Calling the **mcp-intent-gateway MCP tool** with these CanonicalFacts
4. Returning structured success or error responses

The semantic-normalizer must not:
- Apply business rules
- Perform entity resolution
- Call backend APIs directly
- Mutate or enrich CanonicalFacts beyond extraction

All validation, consistency checks, entity resolution, and side effects are delegated to the **mcp-intent-gateway**.

---

## EXAMPLES:

Examples should be placed in `examples/semantic-normalization/`.

### Example 1 — Simple semantic extraction and dispatch

**Input (speech-to-text):**
```text
Gabriel ate everything
```

Expected CanonicalFact produced by the LLM:
```JSON
{
  "subjects": ["Gabriel"],
  "dimension": "MEAL_MAIN_CONSUMPTION",
  "value": "ALL",
  "confidence": 0.95
}
```


Expected behavior:
The semantic-normalizer validates the output against the CanonicalFact schema
The CanonicalFact is passed as-is to the MCP tool exposed by mcp-intent-gateway
No interpretation or correction is applied locally

### Example 2 — Multiple paraphrases, same canonical output

Inputs:
```Text
Gabriel finished his plate

Gabriel left nothing to eat
```

Expected CanonicalFact:
```JSON
{
  "subjects": ["Gabriel"],
  "dimension": "MEAL_MAIN_CONSUMPTION",
  "value": "ALL",
  "confidence": 0.9
}
```

Expected behavior:

Semantic equivalence is handled by the LLM
Determinism is enforced via schema validation, not heuristics

### Example 3 — Low confidence extraction

Input:
```Text
I think Gabriel maybe ate
```

Expected CanonicalFact:
```JSON
{
  "subjects": ["Gabriel"],
  "dimension": "MEAL_MAIN_CONSUMPTION",
  "value": "UNKNOWN",
  "confidence": 0.4
}
```

Expected behavior:

Low confidence is preserved
The MCP gateway decides whether the fact is actionable

### Example 4 — Tool-level rejection

Input:
```Text
Someone ate everything
```

Expected behavior:

LLM may produce a CanonicalFact with an invalid or generic subject
The semantic-normalizer forwards it
The MCP tool rejects it due to failed subject resolution

## DOCUMENTATION:

The following documentation must be referenced, preferably via Context7, during implementation:

OpenAI API documentation (Python SDK, tool/function calling)

MCP protocol specification

Internal documentation of mcp-intent-gateway:
Tool name
Expected input schema (CanonicalFact)
Error and response formats

Pydantic documentation (BaseModel validation, Field constraints)

Python best practices:
Typed interfaces
Explicit error handling
Dependency injection

Context7 MCP:
Used to retrieve up-to-date MCP and OpenAI references

## OTHER CONSIDERATIONS:
CanonicalFact contract (authoritative)

The semantic-normalizer must strictly adhere to the following model:

class CanonicalFact(BaseModel):
    """
    Input from LLM via MCP tool.
    Represents a canonical semantic fact extracted from natural language.
    """

    subjects: list[str]
    dimension: Dimension
    value: str
    confidence: float = 1.0


No additional fields are allowed
No implicit defaults except confidence
The semantic-normalizer is responsible for schema validation only

MCP interaction rules

The MCP tool is the single execution boundary
CanonicalFacts are passed without transformation
The semantic-normalizer must not assume success
All tool errors must be propagated transparently

LLM usage constraints

OpenAI API key is provided via .env

Prompting must:

Focus on structured extraction
Avoid reasoning verbosity
Enforce schema compliance
No retries that modify the original intent
No hallucinated recovery logic

Error handling

Errors must be clearly classified:
LLM extraction errors (invalid or missing CanonicalFact)
MCP tool validation errors
Infrastructure/runtime errors
Errors must remain machine-readable and traceable.
Quality and maintainability
Python-only implementation
Deterministic behavior outside of the LLM
Test-first mindset (golden examples)

Clear separation between:

semantic-normalization
mcp-intent-gateway
backend API
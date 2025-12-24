## FEATURE:

Deterministic Mapping and MCP Intent Gateway Refactor

Refactor the deterministic mapping module and the MCP “intent gateway” to centralize all business logic and validation in the MCP layer.
In order to homogenize codebase, use python instead of typescript

Key responsibilities:

Deterministic Mapping Module
Accept canonical facts from the LLM.
Map them deterministically into an internal representation (IntentContract) for the MCP.
Do not expose internal mappings or lexicons externally yet.
MCP Intent Gateway (previously MCP server)
Receive canonical facts via the MCP tool.
Resolve the child entity from the subject/prename.
Validate the canonical fact against business rules (e.g., allowed dimensions/values, child existence).
Construct the internal IntentContract.
Call a mock API endpoint to get child by firstname in order to deduct id.
Using IntentContract, call a mock API endpoint to create/add the event using childId as pathParameter and the others informations as payload.

Return structured feedback to the LLM (success/failure, validation info).

## EXAMPLES:
Example 1 – Meal Event

Input CanonicalFact from LLM:

{
  "subjects": ["Gabriel"],
  "dimension": "MEAL_MAIN_CONSUMPTION",
  "value": "ALL"
}


Internal IntentContract (MCP):

IntentContract(
    child_id=123,
    action="record_meal",
    properties={"consumption": "ALL"}
)


Mock API Call:
POST to child/{childId}/add_event with payload {action, properties}

Example 2 – Sleep Event

Input CanonicalFact from LLM:

{
  "subjects": ["Léa"],
  "dimension": "SLEEP_STATE",
  "value": "ASLEEP"
}


Internal IntentContract (MCP):

IntentContract(
    child_id=456,
    action="record_sleep",
    properties={"state": "ASLEEP"}
)


Mock API Call:
POST to child/{childId}/add_event with payload {action, properties}

All examples should be stored in the examples/ folder for end-to-end testing.

## DOCUMENTATION:

MCP / context7 documentation: https://crawl4ai.com/mcp

FastAPI documentation: https://fastapi.tiangolo.com/

Pydantic documentation: https://docs.pydantic.dev/

Internal business lexicons and allowed dimensions/values (for reference and validation)

Mock API endpoint specification: /add_event (single endpoint for creating events)

## OTHER CONSIDERATIONS:

Validation & Robustness
MCP is responsible for all business validation; backend sees only REST requests.
Strict Pydantic typing for CanonicalFact and IntentContract.
Logging for audit and traceability.

Scope
CanonicalFact and IntentContract remain internal to MCP; no externalization yet.
Two mock API endpoint only (get /child/{childId} and post /child/{childId}/add_event).
Extensibility
Architecture allows future parameterization or multi-context support.
Future LLM or RAG swaps should not require changes in MCP core logic.
For now, isolate domain vocabulary and classes into specific packages.

Testing
End-to-end tests.
Handle probabilistic LLM outputs with retry/fallback strategies.
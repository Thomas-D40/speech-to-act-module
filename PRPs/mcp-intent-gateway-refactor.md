name: "MCP Intent Gateway Python Refactor"
description: |

## Purpose
Refactor the deterministic mapping module and MCP intent gateway from TypeScript to Python, centralizing all business logic and validation in the MCP layer using FastMCP and Pydantic.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md (if exists)

---

## Goal
Refactor the TypeScript-based deterministic mapping module and intent gateway to Python, creating:
- A Python MCP server using FastMCP that exposes the intent processing as an MCP tool
- Pydantic v2 models for CanonicalFact, IntentContract, and all validation
- Deterministic mapping logic in pure Python
- Mock API endpoints (GET child by firstname, POST add_event)
- Structured feedback to LLM (success/failure, validation info)

## Why
- **Codebase Homogenization**: Use Python instead of TypeScript to match existing semantic-normalization package
- **MCP Integration**: Leverage FastMCP SDK for clean MCP tool definitions
- **Type Safety**: Pydantic v2 provides strict validation and serialization
- **Maintainability**: Single language for LLM-facing components reduces cognitive load
- **Extensibility**: Python ecosystem allows future RAG/LLM swaps without MCP core changes

## What

### User-visible behavior
- LLM sends CanonicalFact via MCP tool
- MCP server resolves child entity from subject/prename via mock API
- MCP server validates canonical fact against business rules
- MCP server constructs IntentContract
- MCP server calls mock API to create/add event
- MCP server returns structured feedback (success/failure, validation info)

### Success Criteria
- [ ] MCP server runs and exposes `process_canonical_fact` tool
- [ ] CanonicalFact is validated with Pydantic (dimension, value, confidence)
- [ ] Child lookup by firstname returns mock child ID
- [ ] IntentContract is correctly constructed from CanonicalFact
- [ ] Mock API add_event is called with correct payload
- [ ] Structured feedback returned to LLM
- [ ] All existing dimension/value mappings work correctly
- [ ] End-to-end tests pass for meal and sleep examples

---

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://github.com/modelcontextprotocol/python-sdk
  why: Official Python MCP SDK - FastMCP server creation, tool decorators, resources

- url: https://pypi.org/project/mcp/
  why: Installation instructions, latest version info

- url: https://modelcontextprotocol.github.io/python-sdk/
  why: Full MCP Python SDK documentation

- url: https://docs.pydantic.dev/
  why: Pydantic v2 model validation, Field constraints, validators

- url: https://fastapi.tiangolo.com/
  why: FastAPI patterns for the mock backend (if needed)

- url: https://www.python-httpx.org/async/
  why: Async HTTP client for calling mock backend

- file: packages/deterministic-mapping/src/types.ts
  why: Source of truth for DOMAINS, DIMENSIONS, DIMENSION_VALUES mappings

- file: packages/deterministic-mapping/src/mapper.ts
  why: Pattern for DeterministicMapper class

- file: packages/deterministic-mapping/src/mappings/*.ts
  why: All domain mapping functions (meal, sleep, diaper, etc.)

- file: packages/intent-gateway/src/validator.ts
  why: IntentionContract validation logic

- file: packages/semantic-normalization/src/semantic_normalization/constants.py
  why: Existing Python enum patterns for Dimension, values

- file: packages/semantic-normalization/src/semantic_normalization/models.py
  why: Existing Pydantic model patterns for CanonicalFact
```

### Current Codebase tree
```bash
packages/
├── backend-mock/           # [TS] Mock REST API - KEEP AS IS
├── deterministic-mapping/  # [TS] TO BE REPLACED BY PYTHON
├── intent-gateway/         # [TS] TO BE REPLACED BY PYTHON
├── orchestrator/           # [TS] Will call new Python MCP
├── rag-knowledge-base/     # [Python] Keep as is
├── semantic-normalization/ # [Python] Keep as is - already has models.py, constants.py
└── speech-to-text-mock/    # [TS] Keep as is
```

### Desired Codebase tree with files to be added
```bash
packages/
├── mcp-intent-gateway/                    # NEW PYTHON PACKAGE
│   ├── pyproject.toml                     # Package definition with dependencies
│   ├── README.md                          # Usage documentation
│   ├── src/
│   │   └── mcp_intent_gateway/
│   │       ├── __init__.py
│   │       ├── server.py                  # FastMCP server with tools
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   ├── canonical_fact.py      # CanonicalFact Pydantic model
│   │       │   ├── intent_contract.py     # IntentContract Pydantic model
│   │       │   └── responses.py           # Response models (validation errors, etc.)
│   │       ├── domain/
│   │       │   ├── __init__.py
│   │       │   ├── constants.py           # DOMAINS, DIMENSIONS, DIMENSION_VALUES
│   │       │   └── validators.py          # Business rule validators
│   │       ├── mapping/
│   │       │   ├── __init__.py
│   │       │   ├── mapper.py              # DeterministicMapper class
│   │       │   ├── meal.py                # Meal mapping function
│   │       │   ├── sleep.py               # Sleep mapping function
│   │       │   ├── diaper.py              # Diaper mapping function
│   │       │   ├── activity.py            # Activity mapping function
│   │       │   ├── health.py              # Health mapping function
│   │       │   ├── behavior.py            # Behavior mapping function
│   │       │   └── medication.py          # Medication mapping function
│   │       └── clients/
│   │           ├── __init__.py
│   │           └── mock_backend.py        # httpx async client for mock backend
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py                 # Model validation tests
│       ├── test_mapper.py                 # Mapping tests
│       ├── test_server.py                 # MCP server integration tests
│       └── examples/                      # E2E test examples
│           ├── meal_example.json
│           └── sleep_example.json
└── examples/                              # Shared E2E test data
    ├── meal_event.json
    └── sleep_event.json
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: Use Pydantic v2 syntax (not v1)
# - Use model_validate() not parse_obj()
# - Use Field() not schema_extra
# - Use field_validator not validator

# CRITICAL: FastMCP tool decorator pattern
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Intent Gateway")

@mcp.tool()
async def process_canonical_fact(fact: dict) -> dict:
    """Process a canonical fact from the LLM."""
    # Tool implementation
    pass

# CRITICAL: httpx async client pattern
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(f"{base_url}/child/{child_id}")

# CRITICAL: Enum usage with str mixin for JSON serialization
class Domain(str, Enum):
    MEAL = "MEAL"
    SLEEP = "SLEEP"

# CRITICAL: Match TypeScript dimension values EXACTLY
# Values from packages/deterministic-mapping/src/types.ts must be preserved
```

---

## Implementation Blueprint

### Data models and structure

```python
# models/canonical_fact.py
from pydantic import BaseModel, Field, field_validator
from typing import List
from ..domain.constants import Dimension

class CanonicalFact(BaseModel):
    """Input from LLM via MCP tool"""
    subjects: List[str] = Field(..., min_length=1, description="Child names/prenames")
    dimension: Dimension
    value: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    @field_validator('value')
    @classmethod
    def validate_value_for_dimension(cls, v, info):
        # Validate value against allowed values for dimension
        pass

# models/intent_contract.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..domain.constants import Domain

class IntentContractMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: Optional[float] = None
    source: str = "mcp-intent-gateway"

class IntentContract(BaseModel):
    """Internal contract for backend API"""
    child_id: int
    action: str  # e.g., "record_meal", "record_sleep"
    properties: Dict[str, Any]
    metadata: Optional[IntentContractMetadata] = None

# models/responses.py
from pydantic import BaseModel
from typing import List, Optional

class ValidationError(BaseModel):
    field: str
    message: str
    code: str

class ProcessingResult(BaseModel):
    success: bool
    message: str
    intent_contract: Optional[IntentContract] = None
    errors: Optional[List[ValidationError]] = None
```

### List of tasks to be completed in order

```yaml
Task 1: Create package structure and pyproject.toml
  CREATE packages/mcp-intent-gateway/pyproject.toml:
    - Define package metadata
    - Add dependencies: mcp>=2.0.0, pydantic>=2.0.0, httpx>=0.27.0, pytest>=7.0.0
    - Add dev dependencies: ruff, mypy, pytest-asyncio
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/__init__.py

Task 2: Create domain constants (mirror TypeScript types.ts)
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/domain/constants.py:
    - Define Domain enum (MEAL, SLEEP, DIAPER, ACTIVITY, HEALTH, BEHAVIOR, MEDICATION)
    - Define Dimension enum (all dimensions from TS)
    - Define DIMENSION_VALUES dict mapping dimension to valid values
    - Define DIMENSION_TO_DOMAIN mapping
    - Define IntentionType enum (MEAL_CONSUMPTION, SLEEP_LOG, etc.)

Task 3: Create Pydantic models
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/models/canonical_fact.py:
    - CanonicalFact model with subjects, dimension, value, confidence
    - Validation for dimension-specific values
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/models/intent_contract.py:
    - IntentContract model with child_id, action, properties
    - IntentContractMetadata model
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/models/responses.py:
    - ValidationError, ProcessingResult models

Task 4: Create mapping functions (mirror TypeScript mappings/)
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/mapping/meal.py:
    - map_meal_facts(facts: List[CanonicalFact]) -> MappingResult | None
  CREATE similar files for: sleep.py, diaper.py, activity.py, health.py, behavior.py, medication.py
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/mapping/mapper.py:
    - DeterministicMapper class with map() method

Task 5: Create mock backend client
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/clients/mock_backend.py:
    - MockBackendClient class
    - async get_child_by_firstname(firstname: str) -> Optional[Child]
    - async add_event(child_id: int, action: str, properties: dict) -> EventResponse

Task 6: Create FastMCP server with tools
  CREATE packages/mcp-intent-gateway/src/mcp_intent_gateway/server.py:
    - Initialize FastMCP("Intent Gateway")
    - @mcp.tool() process_canonical_fact(fact: dict) -> dict
    - Main logic: validate -> resolve child -> map -> call backend -> return result

Task 7: Create unit tests
  CREATE packages/mcp-intent-gateway/tests/test_models.py:
    - Test CanonicalFact validation
    - Test IntentContract construction
  CREATE packages/mcp-intent-gateway/tests/test_mapper.py:
    - Test each mapping function
    - Test determinism (same input -> same output)
  CREATE packages/mcp-intent-gateway/tests/test_server.py:
    - Integration tests for MCP tool

Task 8: Create E2E examples
  CREATE packages/mcp-intent-gateway/tests/examples/:
    - meal_example.json (as per REFACTO_MCP.md)
    - sleep_example.json (as per REFACTO_MCP.md)
```

### Per-task pseudocode

```python
# Task 2: domain/constants.py
from enum import Enum

class Domain(str, Enum):
    MEAL = "MEAL"
    SLEEP = "SLEEP"
    # ... all domains from TS types.ts

class Dimension(str, Enum):
    MEAL_MAIN_CONSUMPTION = "MEAL_MAIN_CONSUMPTION"
    SLEEP_STATE = "SLEEP_STATE"
    # ... all dimensions from TS types.ts

# CRITICAL: Must match TypeScript values exactly
DIMENSION_VALUES: dict[Dimension, list[str]] = {
    Dimension.MEAL_MAIN_CONSUMPTION: ["NOTHING", "QUARTER", "HALF", "THREE_QUARTERS", "ALL"],
    Dimension.SLEEP_STATE: ["ASLEEP", "WOKE_UP", "RESTING", "REFUSED_SLEEP"],
    # ... all from TS
}

DIMENSION_TO_DOMAIN: dict[Dimension, Domain] = {
    Dimension.MEAL_MAIN_CONSUMPTION: Domain.MEAL,
    Dimension.SLEEP_STATE: Domain.SLEEP,
    # ... all mappings
}

# Task 4: mapping/meal.py
from typing import Optional
from ..models.canonical_fact import CanonicalFact
from ..domain.constants import Dimension, Domain, IntentionType

MEAL_DIMENSIONS = [
    Dimension.MEAL_MAIN_CONSUMPTION,
    Dimension.MEAL_DESSERT_CONSUMPTION,
    Dimension.MEAL_VEGETABLE_CONSUMPTION,
    Dimension.MEAL_TYPE,
]

def map_meal_facts(facts: list[CanonicalFact]) -> Optional[dict]:
    """Map meal-related facts to MappingResult."""
    meal_facts = [f for f in facts if f.dimension in MEAL_DIMENSIONS]
    if not meal_facts:
        return None

    attributes = {}
    total_confidence = 0.0

    for fact in meal_facts:
        match fact.dimension:
            case Dimension.MEAL_MAIN_CONSUMPTION:
                attributes["main"] = fact.value
            case Dimension.MEAL_DESSERT_CONSUMPTION:
                attributes["dessert"] = fact.value
            case Dimension.MEAL_VEGETABLE_CONSUMPTION:
                attributes["vegetable"] = fact.value
            case Dimension.MEAL_TYPE:
                attributes["mealType"] = fact.value
        total_confidence += fact.confidence

    return {
        "domain": Domain.MEAL,
        "type": IntentionType.MEAL_CONSUMPTION,
        "attributes": attributes,
        "confidence": total_confidence / len(meal_facts),
    }

# Task 5: clients/mock_backend.py
import httpx
from typing import Optional
from pydantic import BaseModel

class Child(BaseModel):
    id: int
    firstname: str

class MockBackendClient:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url

    async def get_child_by_firstname(self, firstname: str) -> Optional[Child]:
        """Mock: Returns a fake child with ID based on firstname hash."""
        # Mock implementation - in real system would call actual API
        fake_id = abs(hash(firstname)) % 1000
        return Child(id=fake_id, firstname=firstname)

    async def add_event(self, child_id: int, action: str, properties: dict) -> dict:
        """Call POST /child/{childId}/add_event"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/child/{child_id}/add_event",
                json={"action": action, "properties": properties}
            )
            return response.json()

# Task 6: server.py
from mcp.server.fastmcp import FastMCP
from .models.canonical_fact import CanonicalFact
from .models.intent_contract import IntentContract
from .models.responses import ProcessingResult, ValidationError
from .mapping.mapper import DeterministicMapper
from .clients.mock_backend import MockBackendClient

mcp = FastMCP("Intent Gateway")
mapper = DeterministicMapper()
backend = MockBackendClient()

@mcp.tool()
async def process_canonical_fact(
    subjects: list[str],
    dimension: str,
    value: str,
    confidence: float = 1.0
) -> dict:
    """
    Process a canonical fact from the LLM.

    Args:
        subjects: List of child names (e.g., ["Gabriel"])
        dimension: The dimension type (e.g., "MEAL_MAIN_CONSUMPTION")
        value: The value for the dimension (e.g., "ALL")
        confidence: Confidence score 0-1

    Returns:
        Processing result with success status and any errors
    """
    try:
        # 1. Validate input
        fact = CanonicalFact(
            subjects=subjects,
            dimension=dimension,
            value=value,
            confidence=confidence
        )

        # 2. Resolve child from subject
        child = await backend.get_child_by_firstname(subjects[0])
        if not child:
            return ProcessingResult(
                success=False,
                message=f"Child not found: {subjects[0]}",
                errors=[ValidationError(field="subjects", message="Child not found", code="NOT_FOUND")]
            ).model_dump()

        # 3. Map to IntentContract
        mapping_result = mapper.map([fact])

        # 4. Construct IntentContract
        contract = IntentContract(
            child_id=child.id,
            action=f"record_{mapping_result['domain'].lower()}",
            properties=mapping_result['attributes']
        )

        # 5. Call mock backend
        result = await backend.add_event(
            child_id=contract.child_id,
            action=contract.action,
            properties=contract.properties
        )

        return ProcessingResult(
            success=True,
            message=f"Event recorded for {subjects[0]}",
            intent_contract=contract
        ).model_dump()

    except Exception as e:
        return ProcessingResult(
            success=False,
            message=str(e),
            errors=[ValidationError(field="general", message=str(e), code="ERROR")]
        ).model_dump()

if __name__ == "__main__":
    mcp.run()
```

### Integration Points
```yaml
DEPENDENCIES:
  - add: pyproject.toml
  - packages: mcp>=2.0.0, pydantic>=2.0.0, httpx>=0.27.0
  - dev: pytest>=7.0.0, pytest-asyncio>=0.23.0, ruff>=0.8.0, mypy>=1.0.0

MOCK_BACKEND:
  - existing: packages/backend-mock (port 3001)
  - new endpoints needed:
    - GET /child?firstname={firstname} (returns {id, firstname})
    - POST /child/{childId}/add_event (receives {action, properties})

MCP_SERVER:
  - transport: stdio (default) or streamable-http
  - tools exposed: process_canonical_fact

LOGGING:
  - use: Python logging module
  - level: INFO for normal ops, DEBUG for development
```

---

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd packages/mcp-intent-gateway

# Lint and format
uv run ruff check src/ --fix
uv run ruff format src/

# Type checking
uv run mypy src/

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# tests/test_models.py
import pytest
from mcp_intent_gateway.models.canonical_fact import CanonicalFact
from mcp_intent_gateway.domain.constants import Dimension

def test_canonical_fact_valid():
    fact = CanonicalFact(
        subjects=["Gabriel"],
        dimension=Dimension.MEAL_MAIN_CONSUMPTION,
        value="ALL",
        confidence=0.92
    )
    assert fact.subjects == ["Gabriel"]
    assert fact.dimension == Dimension.MEAL_MAIN_CONSUMPTION

def test_canonical_fact_invalid_confidence():
    with pytest.raises(ValueError):
        CanonicalFact(
            subjects=["Gabriel"],
            dimension=Dimension.MEAL_MAIN_CONSUMPTION,
            value="ALL",
            confidence=1.5  # Invalid: must be 0-1
        )

# tests/test_mapper.py
from mcp_intent_gateway.mapping.mapper import DeterministicMapper
from mcp_intent_gateway.models.canonical_fact import CanonicalFact
from mcp_intent_gateway.domain.constants import Dimension, Domain

def test_meal_mapping():
    mapper = DeterministicMapper()
    facts = [CanonicalFact(
        subjects=["Lucas"],
        dimension=Dimension.MEAL_MAIN_CONSUMPTION,
        value="HALF",
        confidence=0.92
    )]
    result = mapper.map(facts)
    assert result["domain"] == Domain.MEAL
    assert result["attributes"]["main"] == "HALF"

def test_deterministic_output():
    """Same input always produces same output"""
    mapper = DeterministicMapper()
    facts = [CanonicalFact(
        subjects=["Nathan"],
        dimension=Dimension.MEAL_MAIN_CONSUMPTION,
        value="THREE_QUARTERS",
        confidence=0.88
    )]
    result1 = mapper.map(facts)
    result2 = mapper.map(facts)
    assert result1 == result2
```

```bash
# Run tests
cd packages/mcp-intent-gateway
uv run pytest tests/ -v

# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the MCP server
cd packages/mcp-intent-gateway
uv run python -m mcp_intent_gateway.server

# In another terminal, use mcp dev to test
mcp dev src/mcp_intent_gateway/server.py

# Or run the MCP inspector
# Expected: Tool "process_canonical_fact" is listed and callable
```

### Level 4: E2E Test with Examples
```bash
# Test with Example 1 - Meal Event
# Input: {"subjects": ["Gabriel"], "dimension": "MEAL_MAIN_CONSUMPTION", "value": "ALL"}
# Expected: IntentContract with child_id, action="record_meal", properties={"consumption": "ALL"}

# Test with Example 2 - Sleep Event
# Input: {"subjects": ["Léa"], "dimension": "SLEEP_STATE", "value": "ASLEEP"}
# Expected: IntentContract with child_id, action="record_sleep", properties={"state": "ASLEEP"}
```

---

## Final Validation Checklist
- [ ] Package installs cleanly: `uv pip install -e packages/mcp-intent-gateway`
- [ ] All tests pass: `uv run pytest packages/mcp-intent-gateway/tests/ -v`
- [ ] No linting errors: `uv run ruff check packages/mcp-intent-gateway/src/`
- [ ] No type errors: `uv run mypy packages/mcp-intent-gateway/src/`
- [ ] MCP server starts: `uv run python -m mcp_intent_gateway.server`
- [ ] Tool is callable via MCP inspector
- [ ] Meal example returns correct IntentContract
- [ ] Sleep example returns correct IntentContract
- [ ] Error cases handled gracefully
- [ ] Logs are informative but not verbose

---

## Anti-Patterns to Avoid
- Do NOT use Pydantic v1 syntax (no `parse_obj`, no `validator` decorator)
- Do NOT hardcode child IDs - always resolve from mock API
- Do NOT catch bare `Exception` without re-raising or logging
- Do NOT use sync HTTP calls - always use async with httpx
- Do NOT modify TypeScript packages - create new Python package
- Do NOT skip validation - Pydantic models are the first line of defense
- Do NOT create patterns different from existing semantic-normalization package
- Do NOT use FastAPI for the MCP server - use FastMCP directly
- Do NOT forget to handle missing/invalid dimension values

---

## Confidence Score: 8/10

**Rationale:**
- +2: Clear existing patterns in TypeScript to follow
- +2: Well-documented MCP Python SDK with FastMCP
- +2: Existing Python code in semantic-normalization to reference
- +1: Straightforward Pydantic v2 patterns
- +1: Clear examples in REFACTO_MCP.md
- -1: Mock backend may need minor modifications for new endpoints
- -1: First MCP implementation in this codebase - may encounter undocumented edge cases

**Key Success Factors:**
1. Exact replication of TypeScript DIMENSION_VALUES
2. Correct FastMCP tool decorator usage
3. Proper async/await patterns throughout
4. Comprehensive test coverage before integration

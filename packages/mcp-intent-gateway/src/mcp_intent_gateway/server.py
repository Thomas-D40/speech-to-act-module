"""
MCP Intent Gateway Server.

FastMCP server that exposes the intent processing as an MCP tool.
Receives canonical facts from LLM, validates them, resolves child entities,
maps to IntentContract, and calls the backend API.
"""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .clients.mock_backend import MockBackendClient
from .domain.constants import DIMENSION_VALUES, Dimension
from .mapping.mapper import DeterministicMapper
from .models.canonical_fact import CanonicalFact
from .models.intent_contract import IntentContract, IntentContractMetadata
from .models.responses import ProcessingResult, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Intent Gateway")

# Initialize components
mapper = DeterministicMapper()
backend = MockBackendClient()


@mcp.tool()
async def process_canonical_fact(
    subjects: list[str],
    dimension: str,
    value: str,
    confidence: float = 1.0,
) -> dict[str, Any]:
    """
    Process a canonical fact from the LLM.

    This tool receives a canonical fact (extracted from natural language by the LLM),
    validates it, resolves the child entity, maps it to an IntentContract,
    and calls the backend API to record the event.

    Args:
        subjects: List of child names (e.g., ["Gabriel"])
        dimension: The dimension type (e.g., "MEAL_MAIN_CONSUMPTION")
        value: The value for the dimension (e.g., "ALL")
        confidence: Confidence score 0-1 (default: 1.0)

    Returns:
        Processing result with success status, message, and intent contract or errors
    """
    logger.info(
        f"Processing canonical fact: subjects={subjects}, dimension={dimension}, value={value}"
    )

    try:
        # 1. Validate dimension
        try:
            dim = Dimension(dimension)
        except ValueError:
            valid_dimensions = [d.value for d in Dimension]
            return ProcessingResult(
                success=False,
                message=f"Invalid dimension: {dimension}",
                errors=[
                    ValidationError(
                        field="dimension",
                        message=f"Must be one of: {valid_dimensions}",
                        code="INVALID_DIMENSION",
                    )
                ],
            ).model_dump()

        # 2. Validate value for dimension
        valid_values = DIMENSION_VALUES.get(dim, [])
        if value not in valid_values:
            return ProcessingResult(
                success=False,
                message=f"Invalid value '{value}' for dimension '{dimension}'",
                errors=[
                    ValidationError(
                        field="value",
                        message=f"Must be one of: {valid_values}",
                        code="INVALID_VALUE",
                    )
                ],
            ).model_dump()

        # 3. Create and validate CanonicalFact
        try:
            fact = CanonicalFact(
                subjects=subjects,
                dimension=dim,
                value=value,
                confidence=confidence,
            )
        except ValueError as e:
            return ProcessingResult(
                success=False,
                message=f"Validation error: {str(e)}",
                errors=[
                    ValidationError(
                        field="canonical_fact",
                        message=str(e),
                        code="VALIDATION_ERROR",
                    )
                ],
            ).model_dump()

        # 4. Resolve child from subject
        child = await backend.get_child_by_firstname(subjects[0])
        if not child:
            return ProcessingResult(
                success=False,
                message=f"Child not found: {subjects[0]}",
                errors=[
                    ValidationError(
                        field="subjects",
                        message=f"Could not find child: {subjects[0]}",
                        code="CHILD_NOT_FOUND",
                    )
                ],
            ).model_dump()

        logger.info(f"Resolved child '{subjects[0]}' to ID {child.id}")

        # 5. Map to MappingResult
        try:
            mapping_result = mapper.map([fact])
        except ValueError as e:
            return ProcessingResult(
                success=False,
                message=f"Mapping error: {str(e)}",
                errors=[
                    ValidationError(
                        field="mapping",
                        message=str(e),
                        code="MAPPING_ERROR",
                    )
                ],
            ).model_dump()

        # 6. Construct IntentContract
        domain_lower = mapping_result["domain"].value.lower()
        action = f"record_{domain_lower}"

        contract = IntentContract(
            child_id=child.id,
            action=action,
            properties=mapping_result["attributes"],
            metadata=IntentContractMetadata(
                confidence=mapping_result.get("confidence"),
            ),
        )

        logger.info(f"Created IntentContract: action={action}, child_id={child.id}")

        # 7. Call mock backend
        event_response = await backend.add_event(
            child_id=contract.child_id,
            action=contract.action,
            properties=contract.properties,
        )

        if not event_response.success:
            return ProcessingResult(
                success=False,
                message=f"Backend error: {event_response.message}",
                errors=[
                    ValidationError(
                        field="backend",
                        message=event_response.message,
                        code="BACKEND_ERROR",
                    )
                ],
            ).model_dump()

        # 8. Return success
        logger.info(f"Successfully processed canonical fact for {subjects[0]}")
        return ProcessingResult(
            success=True,
            message=f"Event recorded for {subjects[0]}",
            intent_contract=contract,
        ).model_dump()

    except Exception as e:
        logger.error(f"Unexpected error processing canonical fact: {e}", exc_info=True)
        return ProcessingResult(
            success=False,
            message=f"Unexpected error: {str(e)}",
            errors=[
                ValidationError(
                    field="general",
                    message=str(e),
                    code="UNEXPECTED_ERROR",
                )
            ],
        ).model_dump()


@mcp.tool()
async def get_valid_dimensions() -> dict[str, Any]:
    """
    Get all valid dimensions and their allowed values.

    This tool returns a schema of all valid dimensions and values
    that can be used in process_canonical_fact.

    Returns:
        Dictionary mapping dimension names to their valid values
    """
    return {
        "dimensions": {
            dim.value: {
                "valid_values": DIMENSION_VALUES[dim],
                "domain": mapper._mapping_functions[0].__name__,  # Just return structure
            }
            for dim in Dimension
        }
    }


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """
    Check the health of the MCP Intent Gateway and backend.

    Returns:
        Health status including backend availability
    """
    backend_healthy = await backend.health_check()
    return {
        "status": "ok",
        "service": "mcp-intent-gateway",
        "backend_available": backend_healthy,
        "backend_url": backend.base_url,
    }


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting MCP Intent Gateway server...")
    mcp.run()


if __name__ == "__main__":
    main()

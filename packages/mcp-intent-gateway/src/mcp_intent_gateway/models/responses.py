"""Response models for MCP Intent Gateway."""

from pydantic import BaseModel, Field

from .intent_contract import IntentContract


class ValidationError(BaseModel):
    """Validation error details."""

    field: str = Field(..., description="The field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Error code for programmatic handling")


class ProcessingResult(BaseModel):
    """Result of processing a canonical fact."""

    success: bool = Field(..., description="Whether processing succeeded")
    message: str = Field(..., description="Human-readable result message")
    intent_contract: IntentContract | None = Field(
        default=None,
        description="The resulting intent contract (if successful)",
    )
    errors: list[ValidationError] | None = Field(
        default=None,
        description="List of validation errors (if failed)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Event recorded for Gabriel",
                    "intent_contract": {
                        "child_id": 123,
                        "action": "record_meal",
                        "properties": {"consumption": "ALL"},
                    },
                },
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": [
                        {
                            "field": "value",
                            "message": "Invalid value 'INVALID' for dimension",
                            "code": "INVALID_VALUE",
                        }
                    ],
                },
            ]
        }
    }

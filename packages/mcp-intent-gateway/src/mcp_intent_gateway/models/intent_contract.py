"""IntentContract Pydantic model - Internal contract for backend API."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class IntentContractMetadata(BaseModel):
    """Metadata for an IntentContract."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the contract was created",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score from the mapping",
    )
    source: str = Field(
        default="mcp-intent-gateway",
        description="Source of the contract",
    )


class IntentContract(BaseModel):
    """
    Internal contract for backend API.
    Represents a validated intent ready to be sent to the backend.
    """

    child_id: int = Field(
        ...,
        description="The resolved child ID from the mock backend",
    )
    action: str = Field(
        ...,
        description="The action to perform (e.g., 'record_meal', 'record_sleep')",
    )
    properties: dict[str, Any] = Field(
        ...,
        description="Properties for the action (e.g., {'consumption': 'ALL'})",
    )
    metadata: IntentContractMetadata | None = Field(
        default=None,
        description="Optional metadata about the contract",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "child_id": 123,
                    "action": "record_meal",
                    "properties": {"consumption": "ALL"},
                    "metadata": {
                        "timestamp": "2024-12-24T12:00:00Z",
                        "confidence": 0.92,
                        "source": "mcp-intent-gateway",
                    },
                },
                {
                    "child_id": 456,
                    "action": "record_sleep",
                    "properties": {"state": "ASLEEP"},
                },
            ]
        }
    }

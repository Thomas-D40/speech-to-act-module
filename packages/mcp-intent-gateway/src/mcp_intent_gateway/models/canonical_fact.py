"""CanonicalFact Pydantic model - Input from LLM via MCP tool."""


from pydantic import BaseModel, Field, field_validator, model_validator

from ..domain.constants import DIMENSION_VALUES, Dimension


class CanonicalFact(BaseModel):
    """
    Input from LLM via MCP tool.
    Represents a canonical semantic fact extracted from natural language.
    """

    subjects: list[str] = Field(
        ...,
        min_length=1,
        description="Child names/prenames (e.g., ['Gabriel'])",
    )
    dimension: Dimension = Field(
        ...,
        description="The dimension type (e.g., MEAL_MAIN_CONSUMPTION)",
    )
    value: str = Field(
        ...,
        description="The value for the dimension (e.g., 'ALL')",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1",
    )

    @field_validator("subjects")
    @classmethod
    def validate_subjects_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure subjects list is not empty and contains valid strings."""
        if not v:
            raise ValueError("Subjects list cannot be empty")
        for subject in v:
            if not subject or not subject.strip():
                raise ValueError("Subject names cannot be empty strings")
        return [s.strip() for s in v]

    @model_validator(mode="after")
    def validate_value_for_dimension(self) -> "CanonicalFact":
        """Validate that the value is valid for the given dimension."""
        valid_values = DIMENSION_VALUES.get(self.dimension, [])
        if self.value not in valid_values:
            raise ValueError(
                f"Invalid value '{self.value}' for dimension '{self.dimension}'. "
                f"Valid values are: {valid_values}"
            )
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "subjects": ["Gabriel"],
                    "dimension": "MEAL_MAIN_CONSUMPTION",
                    "value": "ALL",
                    "confidence": 0.92,
                },
                {
                    "subjects": ["Léa"],
                    "dimension": "SLEEP_STATE",
                    "value": "ASLEEP",
                    "confidence": 0.95,
                },
            ]
        }
    }

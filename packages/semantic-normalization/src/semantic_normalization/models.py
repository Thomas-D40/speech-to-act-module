"""
Pydantic models for semantic normalization
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .constants import Dimension


class CanonicalFact(BaseModel):
    """
    Output from Semantic Normalization Layer
    Input to Deterministic Mapping Layer
    """
    dimension: Dimension
    value: str
    subjects: list[str] = Field(default_factory=list, description="List of identified subjects (names/pronouns)")
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class NormalizationOutput(BaseModel):
    """Complete output from semantic normalization"""
    facts: list[CanonicalFact]
    metadata: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "facts": [
                    {
                        "dimension": "MEAL_MAIN_CONSUMPTION",
                        "value": "HALF",
                        "confidence": 0.92
                    }
                ],
                "metadata": {
                    "processing_time": 0.234,
                    "model": "gpt-4",
                    "raw_input": "il a mangé la moitié"
                }
            }
        }

"""
Semantic Normalization Layer
LLM-based classification for speech-to-act system
"""

from .normalizer import SemanticNormalizer, NormalizationResult, ToolCallResult
from .mcp_client import IntentGatewayClient
from .tool_schema import get_fallback_schema, fetch_tool_schema_from_gateway
from .rag_interface import VectorRAGRetriever, CompatibilityRAGRetriever

__all__ = [
    "SemanticNormalizer",
    "NormalizationResult",
    "ToolCallResult",
    "IntentGatewayClient",
    "get_fallback_schema",
    "fetch_tool_schema_from_gateway",
    "VectorRAGRetriever",
    "CompatibilityRAGRetriever",
]

__version__ = "1.0.0"

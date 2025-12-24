"""
Main semantic normalization logic using OpenAI GPT
"""

import json
import time
from typing import Optional
from openai import OpenAI
from .models import NormalizationOutput, CanonicalFact
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, EXAMPLES
from .rag_interface import RAGRetriever, VectorRAGRetriever


class SemanticNormalizer:
    """
    LLM-based classifier that transforms natural language into canonical facts
    Uses RAG to retrieve relevant context from pre-built knowledge base
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        include_examples: bool = True,
        rag_retriever: Optional[RAGRetriever] = None
    ):
        """
        Initialize the semantic normalizer

        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model to use
            temperature: Temperature for generation (0 = deterministic)
            include_examples: Whether to include few-shot examples
            rag_retriever: RAG retriever instance (defaults to VectorRAGRetriever)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.include_examples = include_examples
        self.rag_retriever = rag_retriever or VectorRAGRetriever()

    def _build_messages(self, input_text: str) -> list[dict]:
        """
        Build messages for OpenAI chat completion
        Enriches with RAG context if available

        Args:
            input_text: Raw text to classify

        Returns:
            List of message dicts
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        # Add few-shot examples if enabled
        if self.include_examples:
            for example in EXAMPLES:
                messages.append({
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(input_text=example["input"])
                })
                messages.append({
                    "role": "assistant",
                    "content": json.dumps(example["output"], ensure_ascii=False)
                })

        # Retrieve RAG context and add to user prompt if available
        rag_context = self.rag_retriever.retrieve_context(input_text)
        user_content = USER_PROMPT_TEMPLATE.format(input_text=input_text)

        if rag_context:
            user_content = f"{rag_context}\n\n{user_content}"

        # Add the actual user input with RAG context
        messages.append({
            "role": "user",
            "content": user_content
        })

        return messages

    def normalize(self, input_text: str) -> NormalizationOutput:
        """
        Transform natural language into canonical facts

        Args:
            input_text: Raw text utterance

        Returns:
            NormalizationOutput with canonical facts

        Raises:
            ValueError: If LLM response is invalid
        """
        start_time = time.time()

        messages = self._build_messages(input_text)

        # Call OpenAI with JSON mode for structured output
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )

        # Parse response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")

        parsed = json.loads(content)

        # Validate and convert to Pydantic models
        facts = [CanonicalFact(**fact) for fact in parsed.get("facts", [])]

        processing_time = time.time() - start_time

        return NormalizationOutput(
            facts=facts,
            metadata={
                "processing_time": processing_time,
                "model": self.model,
                "raw_input": input_text,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
        )

    def normalize_batch(self, inputs: list[str]) -> list[NormalizationOutput]:
        """
        Normalize multiple inputs in batch

        Args:
            inputs: List of text utterances

        Returns:
            List of NormalizationOutput
        """
        return [self.normalize(text) for text in inputs]

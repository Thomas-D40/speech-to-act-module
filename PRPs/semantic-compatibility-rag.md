name: "Semantic Compatibility RAG Layer for CanonicalFact Coherence"
description: |

## Purpose
Implement a **Semantic Compatibility RAG layer** that constrains the LLM to produce only logically coherent CanonicalFacts by encoding semantic logic (NOT business rules). This layer prevents semantically impossible combinations (e.g., "slept everything"), guides multi-concept utterances, and helps decide when to emit one vs. multiple CanonicalFacts.

## Core Principles
1. **Semantic Logic Only**: No business rules or backend constraints
2. **Dual RAG Strategy**: Lexical RAG for phrase mapping + Semantic RAG for compatibility
3. **LLM Authority**: Compatibility rules are authoritative constraints for the LLM
4. **Incremental Design**: Minimal but expressive rule set, designed for extension
5. **Validation-Driven**: Clear test cases for incompatibility, ambiguity, and separation

---

## Goal
Create a second RAG layer that complements the existing **Lexical Equivalence RAG** by adding semantic coherence rules. The LLM will use both RAG contexts to:
- Prevent semantically invalid dimension/value pairings
- Determine when to split utterances into multiple CanonicalFacts
- Reduce hallucinated or nonsensical combinations
- Lower confidence or refuse extraction for ambiguous/invalid inputs

### Success Criteria
- [ ] Semantic compatibility rules stored in separate ChromaDB collection
- [ ] New RAG retriever for compatibility rules integrated into normalizer
- [ ] LLM receives both lexical AND semantic context in prompts
- [ ] Test cases pass for: incompatible dims, multi-fact splitting, ambiguous input
- [ ] Example files in `examples/semantic-compatibility/` work correctly
- [ ] All linting/type checks pass
- [ ] Documentation updated with compatibility rule authoring guide

## Why
- **Reduce Hallucinations**: Prevent LLM from creating nonsensical fact combinations
- **Improve Multi-Fact Handling**: Clear guidance on when to split vs. merge
- **Maintain Modularity**: Semantic rules separate from business/backend logic
- **Enable Evolution**: Easy to add new dimensions without coupling

## What
Add a semantic compatibility layer that:
1. **Stores Compatibility Rules** in ChromaDB (separate collection)
2. **Retrieves Relevant Rules** based on detected dimensions in utterance
3. **Injects Rules into LLM Context** alongside lexical mappings
4. **Guides LLM Behavior** to split, merge, reject, or lower confidence

Expected LLM behavior changes:
- "Gabriel ate everything and slept" → TWO CanonicalFacts (meal + sleep)
- "Gabriel slept everything" → NO CanonicalFact or very low confidence
- "He did everything" → NO CanonicalFact or low confidence (ambiguous)

---

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://platform.openai.com/docs/guides/function-calling
  why: Understand how LLM interprets tool schemas and instructions
  critical: |
    Function descriptions and parameter descriptions are AUTHORITATIVE to the LLM.
    We'll encode semantic rules as part of the system prompt context.

- url: https://realpython.com/chromadb-vector-database/
  why: ChromaDB best practices - collections, embedding consistency, metadata
  critical: |
    - Use SAME embedding model for both collections (paraphrase-multilingual-MiniLM-L12-v2)
    - Distance metric: lower = more similar
    - Metadata filtering for dimension-specific rules

- url: https://www.dataquest.io/blog/introduction-to-vector-databases-using-chromadb/
  why: Vector similarity search patterns for semantic rules

- url: https://github.com/coleam00/context-engineering-intro
  why: Context engineering principles for RAG-augmented prompts
  critical: |
    Context is 10x better than prompt engineering.
    Provide comprehensive examples and rules to the LLM.

- url: https://platform.openai.com/docs/guides/structured-outputs
  why: Structured outputs ensure schema adherence
  critical: |
    We're already using function calling with strict mode.
    Semantic rules should guide WHEN to call vs. refuse.

- file: packages/semantic-normalization/src/semantic_normalization/rag_interface.py
  why: Existing Lexical RAG pattern to mirror
  critical: |
    - Uses VectorRAGRetriever with ChromaDB PersistentClient
    - Embedding function: paraphrase-multilingual-MiniLM-L12-v2
    - Returns formatted context string for LLM injection
    - Pattern: retrieve_context(query, top_k) → str

- file: packages/semantic-normalization/src/semantic_normalization/normalizer.py
  why: Where to integrate the new RAG retriever
  critical: |
    - SemanticNormalizer.__init__ accepts rag_retriever parameter
    - _build_messages() calls rag_retriever.retrieve_context()
    - Context is injected into USER_PROMPT_TEMPLATE
    - We need to add a SECOND retriever for compatibility rules

- file: packages/rag-knowledge-base/src/init_vector_db.py
  why: Pattern for building vector database from JSON rules
  critical: |
    - Loads JSON data (dimension → value → phrases)
    - Creates ChromaDB collection with embedding function
    - Adds documents with metadata
    - We'll mirror this for compatibility rules

- file: packages/rag-knowledge-base/data/initial_lexicon.json
  why: Example of structured knowledge for RAG

- file: packages/semantic-normalization/src/semantic_normalization/prompts.py
  why: Where semantic compatibility context will be injected
  critical: |
    Current: "{rag_context}\n\nClassify this utterance..."
    New: "{lexical_context}\n\n{semantic_context}\n\nClassify..."
```

### Current Codebase Tree
```bash
packages/
├── rag-knowledge-base/
│   ├── data/
│   │   └── initial_lexicon.json          # Lexical: phrase → dimension/value
│   ├── src/
│   │   └── init_vector_db.py             # Pattern: build ChromaDB from JSON
│   └── dist/
│       └── vector_store/                 # ChromaDB persistent storage
│
├── semantic-normalization/
│   ├── src/semantic_normalization/
│   │   ├── normalizer.py                 # MODIFY: add compatibility RAG
│   │   ├── rag_interface.py              # EXTEND: add CompatibilityRAGRetriever
│   │   ├── prompts.py                    # MODIFY: inject semantic context
│   │   ├── tool_schema.py
│   │   ├── mcp_client.py
│   │   └── cli.py
│   └── tests/
│       ├── test_normalizer.py
│       └── test_rag_interface.py
│
└── mcp-intent-gateway/
    └── src/mcp_intent_gateway/
        └── domain/constants.py           # Reference: valid dimensions
```

### Desired Codebase Tree
```bash
packages/
├── rag-knowledge-base/
│   ├── data/
│   │   ├── initial_lexicon.json          # Lexical: phrase → dimension/value
│   │   └── semantic_compatibility.json   # NEW: compatibility rules
│   ├── src/
│   │   ├── init_vector_db.py             # MODIFY: also build compatibility collection
│   │   └── init_compatibility_db.py      # NEW: separate builder for clarity
│   └── dist/
│       └── vector_store/                 # ChromaDB with TWO collections
│
├── semantic-normalization/
│   ├── src/semantic_normalization/
│   │   ├── normalizer.py                 # MODIFY: inject both RAG contexts
│   │   ├── rag_interface.py              # EXTEND: add CompatibilityRAGRetriever
│   │   ├── prompts.py                    # MODIFY: template for dual context
│   │   └── ...
│   └── tests/
│       ├── test_compatibility_rag.py     # NEW: test compatibility retrieval
│       └── test_normalizer.py            # MODIFY: test dual RAG integration
│
└── examples/
    └── semantic-compatibility/           # NEW: example utterances + expected behavior
        ├── example1_incompatible.txt
        ├── example2_invalid_pairing.txt
        ├── example3_compatible_distinct.txt
        └── example4_ambiguous.txt
```

### Known Gotchas & Library Quirks
```python
# CRITICAL GOTCHA #1: Embedding Model Consistency
# MUST use the SAME embedding model for ALL collections in ChromaDB.
# Mixing models causes dimension mismatches or "creatively unpredictable" results.
# Solution: paraphrase-multilingual-MiniLM-L12-v2 for BOTH lexical and compatibility

# CRITICAL GOTCHA #2: ChromaDB Distance Metrics
# ChromaDB uses (1 - cosine similarity) or squared L2 distance.
# Lower values = higher similarity.
# Don't assume higher values mean better matches!

# CRITICAL GOTCHA #3: Metadata Structure for Compatibility Rules
# Unlike lexical RAG (dimension + canonical_value), compatibility rules need:
# - dimension_a, dimension_b (for pairwise rules)
# - rule_type: "incompatible", "must_split", "ambiguous"
# - explanation: "These activities are semantically distinct"

# CRITICAL GOTCHA #4: Query Strategy for Compatibility Rules
# Lexical RAG: query with user utterance (e.g., "tout mangé")
# Compatibility RAG: query with DETECTED DIMENSIONS (e.g., "MEAL_MAIN_CONSUMPTION SLEEP_STATE")
# Must extract dimension hints BEFORE querying compatibility rules!

# CRITICAL GOTCHA #5: LLM Prompt Injection Order
# System prompt → Lexical context → Compatibility context → User utterance
# Compatibility rules should be AFTER lexical mappings to override/constrain

# CRITICAL GOTCHA #6: Rule Minimalism vs. Coverage
# Start with MINIMAL rules (e.g., meal ≠ sleep, sleep ≠ diaper, activity ≠ health).
# Avoid overfitting with too many specific rules.
# Design for incremental addition as new edge cases appear.
```

---

## Implementation Blueprint

### Data Model: Semantic Compatibility Rules

The compatibility rules will be stored as plain-text documents with structured metadata:

```json
{
  "incompatible_pairs": [
    {
      "dimensions": ["MEAL_MAIN_CONSUMPTION", "SLEEP_STATE"],
      "rule_type": "must_split",
      "explanation": "Eating and sleeping are semantically distinct activities that must be recorded as separate facts.",
      "examples": ["Gabriel ate and slept", "il a mangé et dormi"]
    },
    {
      "dimensions": ["SLEEP_STATE", "DIAPER_CHANGE_TYPE"],
      "rule_type": "must_split",
      "explanation": "Sleep state and diaper changes are independent events.",
      "examples": ["he slept and had a diaper change"]
    },
    {
      "dimensions": ["CHILD_MOOD", "MEAL_MAIN_CONSUMPTION"],
      "rule_type": "compatible_but_separate",
      "explanation": "Mood and eating can co-occur but should be separate facts unless causally linked.",
      "examples": ["Gabriel ate everything and was happy"]
    }
  ],
  "invalid_pairings": [
    {
      "verb": "slept",
      "incompatible_with": ["MEAL_MAIN_CONSUMPTION", "MEAL_DESSERT_CONSUMPTION"],
      "rule_type": "semantic_nonsense",
      "explanation": "Sleep verbs cannot logically combine with consumption dimensions.",
      "examples": ["slept everything", "dormi tout"]
    },
    {
      "verb": "ate",
      "incompatible_with": ["SLEEP_STATE"],
      "rule_type": "semantic_nonsense",
      "explanation": "Eating verbs cannot logically combine with sleep states.",
      "examples": ["ate asleep"]
    }
  ],
  "ambiguous_patterns": [
    {
      "pattern": "did everything",
      "rule_type": "ambiguous_dimension",
      "explanation": "The verb 'did' is too generic to infer a specific dimension without context.",
      "action": "refuse_or_low_confidence",
      "examples": ["he did everything", "il a tout fait"]
    },
    {
      "pattern": "pronoun without context",
      "rule_type": "ambiguous_subject",
      "explanation": "Pronouns without names require very high confidence in dimension inference.",
      "action": "lower_confidence",
      "examples": ["he ate", "she slept"]
    }
  ]
}
```

**Embedding Strategy:**
- Each rule will be embedded as a plain-text document describing the incompatibility
- Metadata will include: dimension_a, dimension_b, rule_type
- Query will be constructed from detected dimension keywords in utterance

### Architecture Diagram

```
User Utterance: "Gabriel ate everything and slept"
                         ↓
        ┌────────────────────────────────┐
        │   Semantic Normalizer          │
        │                                │
        │  1. Query Lexical RAG          │ ← "tout mangé" → MEAL_MAIN_CONSUMPTION: ALL
        │  2. Extract dimension hints    │ ← ["MEAL", "SLEEP"]
        │  3. Query Compatibility RAG    │ ← "MEAL_MAIN_CONSUMPTION SLEEP_STATE"
        │                                │      ↓
        │     Compatibility Rule:        │   "must_split: eating and sleeping are distinct"
        │                                │
        │  4. Build LLM context:         │
        │     - Lexical context          │
        │     - Compatibility rules      │
        │     - System prompt            │
        │                                │
        │  5. LLM generates tool calls   │ → [process_canonical_fact(...), process_canonical_fact(...)]
        └────────────────────────────────┘
                         ↓
            TWO CanonicalFacts emitted
```

### List of Tasks

```yaml
Task 0: Create Semantic Compatibility Rule Data
CREATE packages/rag-knowledge-base/data/semantic_compatibility.json:
  - Define incompatible dimension pairs (meal ≠ sleep, etc.)
  - Define invalid verb + dimension pairings
  - Define ambiguous patterns requiring low confidence
  - Use structured JSON format with metadata for embedding

Task 1: Create Compatibility Vector Database Builder
CREATE packages/rag-knowledge-base/src/init_compatibility_db.py:
  - Load semantic_compatibility.json
  - Create ChromaDB collection "compatibility_rules"
  - Use SAME embedding function: paraphrase-multilingual-MiniLM-L12-v2
  - Embed each rule as plain-text description
  - Store metadata: dimension_a, dimension_b, rule_type
  - Mirror pattern from init_vector_db.py

Task 2: Extend RAG Interface with Compatibility Retriever
MODIFY packages/semantic-normalization/src/semantic_normalization/rag_interface.py:
  - CREATE CompatibilityRAGRetriever(RAGRetriever)
  - Use separate collection: "compatibility_rules"
  - Method: retrieve_compatibility_rules(detected_dimensions: list[str]) → str
  - Query construction: join dimensions as "DIM_A DIM_B DIM_C"
  - Return formatted context: "SEMANTIC COMPATIBILITY RULES:\n- Rule 1\n- Rule 2"
  - KEEP VectorRAGRetriever unchanged (lexical)

Task 3: Update Normalizer to Use Dual RAG
MODIFY packages/semantic-normalization/src/semantic_normalization/normalizer.py:
  - ADD compatibility_rag_retriever parameter to __init__
  - MODIFY _build_messages() to:
    1. Get lexical context (existing)
    2. Extract dimension hints from lexical context (regex or simple parsing)
    3. Get compatibility context via compatibility_rag_retriever
    4. Inject BOTH contexts into prompt
  - Pattern: lexical_context = self.rag_retriever.retrieve_context(input_text)
            compatibility_context = self.compatibility_rag_retriever.retrieve_compatibility_rules(dimensions)

Task 4: Update Prompts for Dual Context
MODIFY packages/semantic-normalization/src/semantic_normalization/prompts.py:
  - UPDATE USER_PROMPT_TEMPLATE:
    Old: "{rag_context}\n\nClassify this utterance..."
    New: "{lexical_context}\n\n{compatibility_context}\n\nClassify this utterance..."
  - ADD instructions to SYSTEM_PROMPT:
    "CRITICAL: Semantic compatibility rules are AUTHORITATIVE.
     - If dimensions are marked 'must_split', emit separate tool calls
     - If pairing is 'semantic_nonsense', refuse or set very low confidence
     - If pattern is 'ambiguous', lower confidence below 0.5"

Task 5: Create Example Files
CREATE examples/semantic-compatibility/:
  - example1_incompatible.txt: "Gabriel ate everything and slept" → TWO facts
  - example2_invalid_pairing.txt: "Gabriel slept everything" → NO fact or low confidence
  - example3_compatible_distinct.txt: "Gabriel ate and was happy" → TWO facts
  - example4_ambiguous.txt: "He did everything" → NO fact or low confidence
  - Each file includes expected output as comment

Task 6: Update Vector DB Build Process
MODIFY packages/rag-knowledge-base/src/init_vector_db.py:
  - IMPORT init_compatibility_db
  - CALL init_compatibility_db.init_db() after lexicon initialization
  - OR: Keep separate and document that BOTH must be run

Task 7: Create Unit Tests for Compatibility RAG
CREATE packages/semantic-normalization/tests/test_compatibility_rag.py:
  - test_retrieve_compatibility_rules_incompatible_dims()
  - test_retrieve_compatibility_rules_invalid_pairing()
  - test_retrieve_compatibility_rules_no_match()
  - test_compatibility_rag_embedding_consistency()

Task 8: Update Normalizer Integration Tests
MODIFY packages/semantic-normalization/tests/test_normalizer.py:
  - test_normalize_multi_fact_split() → "Gabriel ate and slept" → 2 tool calls
  - test_normalize_invalid_pairing() → "Gabriel slept everything" → 0 tool calls or low confidence
  - test_normalize_ambiguous() → "He did everything" → 0 tool calls or confidence < 0.5
  - test_normalize_compatible_separate() → "Gabriel ate and was happy" → 2 tool calls

Task 9: Update CLI for Testing
MODIFY packages/semantic-normalization/src/semantic_normalization/cli.py:
  - Initialize CompatibilityRAGRetriever in main()
  - Pass to SemanticNormalizer
  - Show BOTH lexical and compatibility contexts in verbose mode
  - Example: --show-context flag to debug RAG retrieval

Task 10: Update Documentation
CREATE packages/rag-knowledge-base/docs/compatibility_rules.md:
  - How to author new compatibility rules
  - Rule types: must_split, semantic_nonsense, ambiguous
  - When to add rules (new dimensions, edge cases)
  - How to rebuild vector database
```

### Task 1 Pseudocode: Compatibility Vector Database Builder

```python
# packages/rag-knowledge-base/src/init_compatibility_db.py
"""
Build ChromaDB collection for semantic compatibility rules.
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions

COMPATIBILITY_PATH = os.path.join(os.path.dirname(__file__), "../data/semantic_compatibility.json")
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "../dist/vector_store")
COLLECTION_NAME = "compatibility_rules"

def load_compatibility_rules():
    """Load semantic compatibility rules from JSON"""
    with open(COMPATIBILITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def init_db():
    """Initialize compatibility rules collection"""
    print(f"Initializing Compatibility Rules at {VECTOR_DB_PATH}...")

    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

    # CRITICAL: Use SAME embedding function as lexical RAG
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Delete existing collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("Deleted existing compatibility collection.")
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    rules_data = load_compatibility_rules()

    ids = []
    documents = []
    metadatas = []

    count = 0

    # Process incompatible pairs
    for rule in rules_data.get("incompatible_pairs", []):
        count += 1
        # Embed the explanation as the document
        document = f"{rule['explanation']} Dimensions: {', '.join(rule['dimensions'])}"
        ids.append(f"incompatible_{count}")
        documents.append(document)
        metadatas.append({
            "dimension_a": rule["dimensions"][0],
            "dimension_b": rule["dimensions"][1] if len(rule["dimensions"]) > 1 else "",
            "rule_type": rule["rule_type"],
            "explanation": rule["explanation"]
        })

    # Process invalid pairings
    for rule in rules_data.get("invalid_pairings", []):
        for incompatible_dim in rule["incompatible_with"]:
            count += 1
            document = f"{rule['explanation']} Verb: {rule['verb']}, Incompatible: {incompatible_dim}"
            ids.append(f"invalid_{count}")
            documents.append(document)
            metadatas.append({
                "verb": rule["verb"],
                "dimension": incompatible_dim,
                "rule_type": rule["rule_type"],
                "explanation": rule["explanation"]
            })

    # Process ambiguous patterns
    for rule in rules_data.get("ambiguous_patterns", []):
        count += 1
        document = f"{rule['explanation']} Pattern: {rule['pattern']}"
        ids.append(f"ambiguous_{count}")
        documents.append(document)
        metadatas.append({
            "pattern": rule["pattern"],
            "rule_type": rule["rule_type"],
            "action": rule["action"],
            "explanation": rule["explanation"]
        })

    # Add to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Successfully embedded {count} compatibility rules into '{COLLECTION_NAME}'.")
    print(f"Database ready at {VECTOR_DB_PATH}")

if __name__ == "__main__":
    init_db()
```

### Task 2 Pseudocode: Compatibility RAG Retriever

```python
# packages/semantic-normalization/src/semantic_normalization/rag_interface.py
# EXTEND existing file

class CompatibilityRAGRetriever(RAGRetriever):
    """
    Retrieves semantic compatibility rules for dimension combinations.
    """

    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self._collection = None
        self._init_client()

    def _init_client(self):
        """Initialize ChromaDB client for compatibility rules"""
        if not os.path.exists(self.db_path):
            print(f"WARNING: Compatibility DB not found at {self.db_path}.")
            return

        try:
            client = chromadb.PersistentClient(path=self.db_path)
            # CRITICAL: Same embedding function as lexical RAG
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            self._collection = client.get_collection(
                name="compatibility_rules",
                embedding_function=ef
            )
        except Exception as e:
            print(f"ERROR initializing Compatibility ChromaDB: {e}")

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        OVERRIDE: For compatibility, query is constructed from detected dimensions

        Args:
            query: Space-separated dimension names (e.g., "MEAL_MAIN_CONSUMPTION SLEEP_STATE")
            top_k: Number of rules to retrieve
        """
        if not self._collection:
            return ""

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k
            )

            metadatas = results['metadatas'][0]
            documents = results['documents'][0]

            if not documents:
                return ""

            context_lines = ["SEMANTIC COMPATIBILITY RULES (AUTHORITATIVE):"]
            for meta, doc in zip(metadatas, documents):
                rule_type = meta.get('rule_type', 'unknown')
                context_lines.append(f"- [{rule_type.upper()}] {doc}")

            return "\n".join(context_lines)

        except Exception as e:
            return f"Error gathering compatibility rules: {e}"
```

### Task 3 Pseudocode: Dual RAG Integration in Normalizer

```python
# packages/semantic-normalization/src/semantic_normalization/normalizer.py
# MODIFY existing file

class SemanticNormalizer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        rag_retriever: Optional[RAGRetriever] = None,  # Lexical RAG
        compatibility_rag_retriever: Optional[RAGRetriever] = None,  # NEW
        tool_schema: Optional[list[dict]] = None,
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.rag_retriever = rag_retriever or VectorRAGRetriever()
        self.compatibility_rag_retriever = compatibility_rag_retriever or CompatibilityRAGRetriever()  # NEW
        self.tool_schema = tool_schema or get_fallback_schema()

    def _extract_dimension_hints(self, lexical_context: str) -> list[str]:
        """
        Extract dimension keywords from lexical RAG context.
        Simple regex to find dimension names (e.g., "MEAL_MAIN_CONSUMPTION").
        """
        import re
        # Pattern: UPPERCASE_WORDS
        dimensions = re.findall(r'\b[A-Z_]{3,}\b', lexical_context)
        # Deduplicate and filter known dimensions
        return list(set(dimensions))

    def _build_messages(self, input_text: str) -> tuple[list[dict], str]:
        """
        Build messages with DUAL RAG context.

        Returns:
            Tuple of (messages, combined_context_for_debugging)
        """
        # 1. Get lexical context (existing)
        lexical_context = self.rag_retriever.retrieve_context(input_text)

        # 2. Extract dimension hints from lexical context
        detected_dimensions = self._extract_dimension_hints(lexical_context)

        # 3. Get compatibility context
        compatibility_context = ""
        if detected_dimensions:
            # Query with space-separated dimensions
            dimension_query = " ".join(detected_dimensions)
            compatibility_context = self.compatibility_rag_retriever.retrieve_context(
                dimension_query,
                top_k=3
            )

        # 4. Build combined context
        combined_context = f"{lexical_context}"
        if compatibility_context:
            combined_context += f"\n\n{compatibility_context}"

        # 5. Inject into prompt
        user_content = USER_PROMPT_TEMPLATE.format(
            rag_context=combined_context,  # Combined lexical + compatibility
            input_text=input_text
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        return messages, combined_context
```

### Integration Points

```yaml
DATABASE:
  - New ChromaDB collection: "compatibility_rules"
  - Same vector store path: packages/rag-knowledge-base/dist/vector_store
  - Same embedding model: paraphrase-multilingual-MiniLM-L12-v2

DATA:
  - New JSON file: packages/rag-knowledge-base/data/semantic_compatibility.json
  - Structure: incompatible_pairs, invalid_pairings, ambiguous_patterns

NORMALIZER:
  - Add compatibility_rag_retriever parameter
  - Modify _build_messages() to inject dual context
  - Update CLI to instantiate CompatibilityRAGRetriever

PROMPTS:
  - Update SYSTEM_PROMPT with compatibility rule instructions
  - Update USER_PROMPT_TEMPLATE to accept combined context
```

---

## Validation Loop

### Level 1: Syntax & Style
```bash
cd packages/semantic-normalization

# Lint
../../.venv/Scripts/ruff.exe check src/ --fix

# Type check
../../.venv/Scripts/mypy.exe src/

# Expected: No errors
```

### Level 2: Build Compatibility Vector Database
```bash
cd packages/rag-knowledge-base

# Build compatibility collection
PYTHONPATH=./src ../../.venv/Scripts/python.exe src/init_compatibility_db.py

# Expected: "Successfully embedded X compatibility rules into 'compatibility_rules'."
# Verify: dist/vector_store/ should now have TWO collections
```

### Level 3: Unit Tests
```bash
cd packages/semantic-normalization

# Test compatibility RAG retrieval
PYTHONPATH=./src ../../.venv/Scripts/pytest.exe tests/test_compatibility_rag.py -v

# Test normalizer dual RAG integration
PYTHONPATH=./src ../../.venv/Scripts/pytest.exe tests/test_normalizer.py -v -k "compatibility"

# Expected: All tests pass
```

### Level 4: Integration Test with Examples
```bash
cd packages/semantic-normalization

# Test example 1: Incompatible dimensions (should split into 2 facts)
PYTHONPATH=./src ../../.venv/Scripts/python.exe -m semantic_normalization.cli "Gabriel ate everything and slept"

# Expected output (should show TWO tool calls):
# {
#   "tool_calls": [
#     {"dimension": "MEAL_MAIN_CONSUMPTION", "value": "ALL", "subjects": ["Gabriel"]},
#     {"dimension": "SLEEP_STATE", "value": "ASLEEP", "subjects": ["Gabriel"]}
#   ]
# }

# Test example 2: Invalid pairing (should refuse or very low confidence)
PYTHONPATH=./src ../../.venv/Scripts/python.exe -m semantic_normalization.cli "Gabriel slept everything"

# Expected: No tool calls or confidence < 0.3

# Test example 3: Compatible but distinct (should emit 2 facts)
PYTHONPATH=./src ../../.venv/Scripts/python.exe -m semantic_normalization.cli "Gabriel ate and was happy"

# Expected: 2 tool calls (MEAL + CHILD_MOOD)

# Test example 4: Ambiguous (should refuse or very low confidence)
PYTHONPATH=./src ../../.venv/Scripts/python.exe -m semantic_normalization.cli "He did everything"

# Expected: No tool calls or confidence < 0.5
```

### Level 5: Manual Inspection
```bash
# Verify both collections exist
cd packages/rag-knowledge-base
ls -la dist/vector_store/

# Expected: ChromaDB directory with multiple .parquet/.bin files (2 collections)

# Test retrieval directly
cd packages/semantic-normalization
PYTHONPATH=./src ../../.venv/Scripts/python.exe -c "
from semantic_normalization.rag_interface import CompatibilityRAGRetriever
rag = CompatibilityRAGRetriever()
print(rag.retrieve_context('MEAL_MAIN_CONSUMPTION SLEEP_STATE', top_k=3))
"

# Expected: "SEMANTIC COMPATIBILITY RULES: ..."
```

---

## Final Validation Checklist
- [ ] `semantic_compatibility.json` created with minimal rule set
- [ ] `init_compatibility_db.py` builds collection successfully
- [ ] `CompatibilityRAGRetriever` retrieves rules correctly
- [ ] `SemanticNormalizer` uses dual RAG (lexical + compatibility)
- [ ] Prompts updated with compatibility instructions
- [ ] All unit tests pass
- [ ] Example files produce expected behavior
- [ ] CLI shows both RAG contexts in verbose mode
- [ ] No linting or type errors
- [ ] Documentation created for rule authoring

---

## Anti-Patterns to Avoid
- ❌ Don't encode business rules (e.g., "child must be enrolled") - only semantic logic
- ❌ Don't use different embedding models for different collections
- ❌ Don't query compatibility RAG with raw user utterance - use detected dimensions
- ❌ Don't create overly specific rules - design for generality
- ❌ Don't bypass compatibility rules in LLM prompt - make them AUTHORITATIVE
- ❌ Don't hardcode dimensions in compatibility retriever - extract dynamically

---

## Error Handling Strategy

```python
class CompatibilityRAGError(Exception):
    """Base exception for compatibility RAG errors."""
    pass

class DimensionExtractionError(CompatibilityRAGError):
    """Failed to extract dimensions from lexical context."""
    pass

class CollectionNotFoundError(CompatibilityRAGError):
    """Compatibility rules collection not initialized."""
    pass
```

Error flow:
1. **Compatibility DB not found**: Log warning, continue with lexical RAG only
2. **No dimensions detected**: Skip compatibility check, use lexical context only
3. **No compatibility rules match**: Return empty string, LLM uses lexical context
4. **ChromaDB query error**: Log error, return empty compatibility context

---

## Incremental Rollout Plan

### Phase 1: Core Implementation (This PRP)
- Compatibility rule data model
- ChromaDB collection setup
- Dual RAG retrieval
- Basic test cases

### Phase 2: Rule Expansion (Future)
- Add more dimension pair rules as edge cases discovered
- Add verb + dimension incompatibilities
- Add temporal compatibility (can't sleep and be active simultaneously)

### Phase 3: Advanced Features (Future)
- Confidence scoring based on rule strength
- Rule conflict resolution (multiple rules apply)
- Dynamic rule learning from rejected tool calls

---

## Data Synchronization: Compatibility Rules ↔ Gateway

**CRITICAL**: Compatibility rules reference dimensions from `mcp-intent-gateway/domain/constants.py`.

| Source | Role | Dimensions |
|--------|------|-----------|
| `mcp-intent-gateway/domain/constants.py` | **Authoritative** | Defines valid dimensions |
| `semantic_compatibility.json` | Semantic rules | References dimension pairs |
| `semantic-normalization` | Consumer | Uses both RAG layers |

When adding new dimensions:
1. Add to gateway's `constants.py` (DIMENSION enum)
2. Add lexical phrases to `initial_lexicon.json`
3. Add compatibility rules to `semantic_compatibility.json` (if needed)
4. Run BOTH `init_vector_db.py` and `init_compatibility_db.py`
5. No changes needed in semantic-normalization code!

---

## Confidence Score: 9/10

**Strengths:**
- Clear separation of concerns (lexical vs. semantic)
- Mirrors existing RAG pattern exactly
- Minimal but extensible rule design
- Comprehensive test coverage
- Well-defined validation gates

**Risks:**
- Dimension extraction regex might miss edge cases (0.5 risk)
- LLM might ignore compatibility rules if prompt not authoritative enough (0.5 risk)

**Mitigation:**
- Start with simple regex, iterate based on test failures
- Make compatibility rules BOLD/UPPERCASE in prompt to emphasize authority
- Test with multiple utterances during validation

---

## Example Data: semantic_compatibility.json (Starter)

```json
{
  "incompatible_pairs": [
    {
      "dimensions": ["MEAL_MAIN_CONSUMPTION", "SLEEP_STATE"],
      "rule_type": "must_split",
      "explanation": "Eating and sleeping are semantically distinct activities. If both are mentioned, emit TWO separate CanonicalFacts.",
      "examples": ["Gabriel ate everything and slept", "il a tout mangé et dormi"]
    },
    {
      "dimensions": ["SLEEP_STATE", "DIAPER_CHANGE_TYPE"],
      "rule_type": "must_split",
      "explanation": "Sleep state and diaper changes are independent events. Always emit separate facts.",
      "examples": ["he slept and had a diaper change"]
    },
    {
      "dimensions": ["CHILD_MOOD", "MEAL_MAIN_CONSUMPTION"],
      "rule_type": "compatible_but_separate",
      "explanation": "Mood and eating can co-occur but should be separate facts unless causally linked.",
      "examples": ["Gabriel ate everything and was happy"]
    },
    {
      "dimensions": ["ACTIVITY_TYPE", "HEALTH_STATUS"],
      "rule_type": "must_split",
      "explanation": "Activities and health observations are distinct concerns. Emit separate facts.",
      "examples": ["played outside and had a fever"]
    }
  ],
  "invalid_pairings": [
    {
      "verb": "slept",
      "incompatible_with": ["MEAL_MAIN_CONSUMPTION", "MEAL_DESSERT_CONSUMPTION", "MEAL_VEGETABLE_CONSUMPTION"],
      "rule_type": "semantic_nonsense",
      "explanation": "Sleep-related verbs (slept, sleeping, nap) cannot logically combine with consumption dimensions. This is semantically invalid.",
      "examples": ["slept everything", "dormi tout"]
    },
    {
      "verb": "ate",
      "incompatible_with": ["SLEEP_STATE"],
      "rule_type": "semantic_nonsense",
      "explanation": "Eating verbs cannot logically combine with sleep states. This is semantically invalid.",
      "examples": ["ate asleep"]
    }
  ],
  "ambiguous_patterns": [
    {
      "pattern": "did everything",
      "rule_type": "ambiguous_dimension",
      "explanation": "The verb 'did' is too generic to infer a specific dimension without additional context. Refuse extraction or set confidence < 0.5.",
      "action": "refuse_or_low_confidence",
      "examples": ["he did everything", "il a tout fait"]
    },
    {
      "pattern": "pronoun without name",
      "rule_type": "ambiguous_subject",
      "explanation": "Pronouns (he, she, it) without explicit names require very high confidence in dimension inference. Lower confidence to < 0.7.",
      "action": "lower_confidence",
      "examples": ["he ate", "she slept"]
    }
  ]
}
```

---

## Sources
- [ChromaDB Vector Database Guide](https://realpython.com/chromadb-vector-database/)
- [ChromaDB Best Practices](https://www.dataquest.io/blog/introduction-to-vector-databases-using-chromadb/)
- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro)
- [Vector Stores Semantic Search](https://medium.com/@chaudhuri.anusha1/vector-stores-demystified-unlocking-smarter-semantic-search-with-chromadb-and-more-7232446971a5)
- [ChromaDB Similarity Search Tutorial](https://medium.com/@tahirbalarabe2/how-to-use-chroma-db-for-similarity-search-188e490badac)

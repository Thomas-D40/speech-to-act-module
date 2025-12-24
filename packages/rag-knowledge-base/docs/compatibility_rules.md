# Semantic Compatibility Rules Documentation

## Overview

The Semantic Compatibility RAG layer constrains the LLM to produce only logically coherent CanonicalFacts by encoding semantic logic (NOT business rules). This layer prevents semantically impossible combinations, guides multi-concept utterances, and helps decide when to emit one vs. multiple CanonicalFacts.

## Rule Types

### 1. `must_split`
Dimensions that are semantically distinct and must ALWAYS be recorded as separate facts.

**Example:**
```json
{
  "dimensions": ["MEAL_MAIN_CONSUMPTION", "SLEEP_STATE"],
  "rule_type": "must_split",
  "explanation": "Eating and sleeping are semantically distinct activities that must be recorded as separate facts."
}
```

**Behavior:** When both dimensions are detected, the LLM will emit TWO separate tool calls.

### 2. `compatible_but_separate`
Dimensions that can co-occur but should generally be separate facts unless causally linked.

**Example:**
```json
{
  "dimensions": ["CHILD_MOOD", "MEAL_MAIN_CONSUMPTION"],
  "rule_type": "compatible_but_separate",
  "explanation": "Mood and eating can co-occur but should be separate facts unless causally linked."
}
```

**Behavior:** The LLM will emit separate tool calls but won't reject the combination entirely.

### 3. `semantic_nonsense`
Verb + dimension combinations that are logically impossible.

**Example:**
```json
{
  "verb": "slept",
  "incompatible_with": ["MEAL_MAIN_CONSUMPTION", "MEAL_DESSERT_CONSUMPTION"],
  "rule_type": "semantic_nonsense",
  "explanation": "Sleep-related verbs cannot logically combine with consumption dimensions."
}
```

**Behavior:** The LLM will refuse extraction or set confidence below 0.3.

### 4. `ambiguous_dimension`
Patterns that are too vague to infer a specific dimension.

**Example:**
```json
{
  "pattern": "did everything",
  "rule_type": "ambiguous_dimension",
  "explanation": "The verb 'did' is too generic to infer a specific dimension without additional context.",
  "action": "refuse_or_low_confidence"
}
```

**Behavior:** The LLM will refuse extraction or set confidence below 0.5.

### 5. `ambiguous_subject`
Patterns with unclear subjects requiring caution.

**Example:**
```json
{
  "pattern": "pronoun without name",
  "rule_type": "ambiguous_subject",
  "explanation": "Pronouns without explicit names require very high confidence in dimension inference.",
  "action": "lower_confidence"
}
```

**Behavior:** The LLM will lower confidence below 0.7.

---

## How to Author New Rules

### Step 1: Identify the Semantic Issue
Determine what kind of incompatibility you're addressing:
- Are two dimensions fundamentally different activities? → `must_split`
- Can they occur together but shouldn't be merged? → `compatible_but_separate`
- Is a verb incompatible with a dimension? → `semantic_nonsense`
- Is a pattern too vague? → `ambiguous_dimension` or `ambiguous_subject`

### Step 2: Add to `semantic_compatibility.json`

Edit `packages/rag-knowledge-base/data/semantic_compatibility.json`:

```json
{
  "incompatible_pairs": [
    {
      "dimensions": ["NEW_DIMENSION_A", "NEW_DIMENSION_B"],
      "rule_type": "must_split",
      "explanation": "Clear explanation of why these are incompatible.",
      "examples": ["example phrase 1", "example phrase 2"]
    }
  ]
}
```

### Step 3: Rebuild the Vector Database

After adding or modifying rules, rebuild the compatibility collection:

```bash
cd packages/rag-knowledge-base
PYTHONPATH=./src ../../.venv/Scripts/python.exe src/init_compatibility_db.py
```

Or rebuild both collections at once:

```bash
cd packages/rag-knowledge-base
PYTHONPATH=./src ../../.venv/Scripts/python.exe src/init_vector_db.py
```

### Step 4: Test Your Rules

Use the CLI to test with example utterances:

```bash
cd packages/semantic-normalization
PYTHONPATH=./src ../../.venv/Scripts/python.exe -m semantic_normalization.cli "your test utterance"
```

Check the output to ensure:
- The compatibility rules are retrieved
- The LLM behaves as expected (splits, refuses, lowers confidence)

---

## When to Add Rules

### ✅ Add rules when:
- New dimensions are added that are semantically distinct from existing ones
- Edge cases are discovered where the LLM incorrectly merges incompatible concepts
- Common ambiguous patterns cause incorrect extractions
- User testing reveals semantic confusion

### ❌ Do NOT add rules when:
- The issue is a business rule (e.g., "child must be enrolled") → belongs in the gateway
- The issue is a value validation problem → belongs in the gateway
- You're trying to fix a specific utterance without generalizing → wait for more examples

---

## Rule Design Principles

### 1. **Start Minimal**
Begin with the most obvious incompatibilities (meal ≠ sleep, sleep ≠ diaper, activity ≠ health).
Avoid overfitting with too many specific rules.

### 2. **Design for Generality**
Each rule should cover a category of incompatibilities, not a single edge case.

**Good:** "Sleep verbs cannot combine with consumption dimensions"
**Bad:** "The phrase 'slept everything' is invalid"

### 3. **Provide Clear Explanations**
The explanation field is embedded in the vector database and retrieved by the LLM.
Make it authoritative and unambiguous.

### 4. **Include Examples**
Examples help document the rule and can be used for testing.

### 5. **Test Incrementally**
After adding a rule, test with multiple utterances to ensure:
- It works for the intended case
- It doesn't cause unintended side effects

---

## Troubleshooting

### Rule Not Retrieved
If your rule isn't appearing in the RAG context:
1. Check that you rebuilt the vector database
2. Verify the dimension names match exactly (case-sensitive)
3. Test the embedding similarity manually:
   ```python
   from semantic_normalization.rag_interface import CompatibilityRAGRetriever
   rag = CompatibilityRAGRetriever()
   print(rag.retrieve_context('DIMENSION_A DIMENSION_B', top_k=5))
   ```

### LLM Ignoring Rules
If the LLM doesn't follow the rules:
1. Check that the explanation is clear and authoritative
2. Ensure the rule type is correct
3. Try strengthening the language in the explanation
4. Verify the rules appear in the RAG context output

### Too Many Rules Retrieved
If irrelevant rules are being retrieved:
1. Make explanations more specific
2. Add more distinctive keywords to the explanation
3. Reduce `top_k` in the retriever (default is 3)

---

## Architecture

```
User Utterance → Lexical RAG → Extract Dimensions → Compatibility RAG → LLM → Tool Calls
                      ↓                                      ↓
              "ate", "slept"                    "MUST_SPLIT: eating and sleeping"
                                                        ↓
                                                 TWO tool calls
```

---

## Examples

See `examples/semantic-compatibility/` for working examples:
- `example1_incompatible.txt`: Must split (meal + sleep)
- `example2_invalid_pairing.txt`: Semantic nonsense
- `example3_compatible_distinct.txt`: Compatible but separate
- `example4_ambiguous.txt`: Ambiguous pattern

---

## Data Synchronization

**CRITICAL**: Compatibility rules reference dimensions from `mcp-intent-gateway/domain/constants.py`.

When adding new dimensions:
1. Add to gateway's `constants.py` (DIMENSION enum)
2. Add lexical phrases to `initial_lexicon.json`
3. Add compatibility rules to `semantic_compatibility.json` (if needed)
4. Rebuild BOTH vector databases
5. No changes needed in semantic-normalization code!

---

## Further Reading

- [ChromaDB Best Practices](https://realpython.com/chromadb-vector-database/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Context Engineering Principles](https://github.com/coleam00/context-engineering-intro)

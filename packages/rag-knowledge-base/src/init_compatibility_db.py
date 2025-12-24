"""
Build ChromaDB collection for semantic compatibility rules.
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions

# Configuration
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

    # Ensure dist directory exists
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

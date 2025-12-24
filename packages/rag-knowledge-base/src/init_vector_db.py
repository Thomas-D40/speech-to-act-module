"""
Vector Database Builder
Reads the initial lexicon and embeds it into a ChromaDB persistent store.
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions

# Configuration
LEXICON_PATH = os.path.join(os.path.dirname(__file__), "../data/initial_lexicon.json")
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "../dist/vector_store")
COLLECTION_NAME = "lexicon_embeddings"

def load_lexicon():
    """Load the JSON lexicon"""
    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def init_db():
    """Initialize ChromaDB and populate it"""
    print(f"Initializing Vector DB at {VECTOR_DB_PATH}...")
    
    # Ensure dist directory exists
    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)

    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    
    # Use multilingual model for better French support
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    # Get or create collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("Deleted existing collection.")
    except Exception:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    lexicon = load_lexicon()
    
    ids = []
    documents = []
    metadatas = []
    
    print("Embedding data...")
    count = 0
    for dimension, mapping in lexicon.items():
        for canonical_value, phrases in mapping.items():
            for phrase in phrases:
                count += 1
                ids.append(f"{dimension}_{canonical_value}_{count}")
                documents.append(phrase)
                metadatas.append({
                    "dimension": dimension,
                    "canonical_value": canonical_value,
                    "original_phrase": phrase
                })

    # Add to collection in batches to be safe, though volume is low here
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully embedded {count} items into '{COLLECTION_NAME}'.")
    print(f"Database ready at {VECTOR_DB_PATH}")

if __name__ == "__main__":
    init_db()

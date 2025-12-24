"""
RAG retrieval interface
Uses ChromaDB for semantic similarity search
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from abc import ABC, abstractmethod

# Robust path resolution
# We want to find packages/rag-knowledge-base/dist/vector_store relative to this file
# File is in: packages/semantic-normalization/src/semantic_normalization/
# ../ -> src
# ../../ -> semantic-normalization
# ../../../ -> packages
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.abspath(os.path.join(
    CURRENT_DIR, 
    "../../../rag-knowledge-base/dist/vector_store"
))
COLLECTION_NAME = "lexicon_embeddings"

class RAGRetriever(ABC):
    """Abstract interface for RAG retrieval"""

    @abstractmethod
    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve relevant context for a query"""
        pass


class VectorRAGRetriever(RAGRetriever):
    """
    RAG implementation using persistent ChromaDB vector store
    """

    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self._collection = None
        self._init_client()

    def _init_client(self):
        """Initialize ChromaDB client gracefully"""
        if not os.path.exists(self.db_path):
            print(f"WARNING: Vector DB not found at {self.db_path}. RAG will be empty.")
            return

        try:
            client = chromadb.PersistentClient(path=self.db_path)
            # Use multilingual model for French support
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
            self._collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        except Exception as e:
            print(f"ERROR initializing ChromaDB: {e}")

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve most similar context from vector store"""
        if not self._collection:
            return "WARNING: Knowledge base not initialized."

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # ChromaDB returns list of lists (one for each query)
            metadatas = results['metadatas'][0]
            documents = results['documents'][0]
            distances = results['distances'][0]

            context_lines = ["RELEVANT KNOWLEDGE (Semantic Match):"]
            for meta, doc, dist in zip(metadatas, documents, distances):
                # distance is typically L2 or cosine distance. Lower is better for L2.
                # Just formatting for context injection
                context_lines.append(
                    f"- '{doc}' → {meta['dimension']}: {meta['canonical_value']} (dist: {dist:.2f})"
                )
            
            return "\n".join(context_lines)

        except Exception as e:
            return f"Error gathering context: {e}"


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
        Retrieve compatibility rules for detected dimensions.

        Args:
            query: Space-separated dimension names (e.g., "MEAL_MAIN_CONSUMPTION SLEEP_STATE")
            top_k: Number of rules to retrieve

        Returns:
            Formatted compatibility rules context
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

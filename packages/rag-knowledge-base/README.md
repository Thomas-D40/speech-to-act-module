# RAG Knowledge Base

This package manages the Retrieval-Augmented Generation (RAG) knowledge base for the Semantic Normalization Layer.

It uses **ChromaDB** as a vector store and **SentenceTransformers** for embedding generation.

## Structure

- `data/initial_lexicon.json`: Source of truth for the lexicon. Add synonyms here.
- `src/init_vector_db.py`: Script to generate the persistent vector database.
- `dist/vector_store`: The generated ChromaDB (not committed to git).

## Setup & Usage

### 1. Install Dependencies

Ensure you have the required packages installed in your environment:

```bash
pip install chromadb sentence-transformers
```

### 2. Build the Database

Run the initialization script to ingest `initial_lexicon.json` into the vector store:

```bash
python src/init_vector_db.py
```

This will create a `dist/vector_store` directory.

### 3. Usage in other modules

The `semantic-normalization` package expects to find the vector store at `../rag-knowledge-base/dist/vector_store`.

## Architecture: Embedded & Serverless

This RAG implementation is **fully embedded**:
- **No Docker Container**: ChromaDB runs inside the Python process using `chromadb.PersistentClient`.
- **No Network Ports**: It reads/writes directly to the file system (`dist/vector_store`).
- **Zero Ops**: Just ensure the files are there. No database server to manage.

## Future Scalability

As the project grows, migrating to a standalone database might be necessary if:
1.  **Concurrency**: You have multiple API replicas writing to the DB simultaneously (Embedded is single-writer).
2.  **Size**: The dataset exceeds memory/local disk feasibility (e.g., >100k documents).
3.  **Separation**: You want to decouple the knowledge base updates from the application deployment.

**Migration Path:**
Since we use the official ChromaDB client, switching is a one-line code change:
- Change `chromadb.PersistentClient(path="...")`
- To `chromadb.HttpClient(host="my-chroma-server", port=8000)`

## Updating the Knowledge Base

1. Edit `data/initial_lexicon.json` to add new terms or dimensions.
2. Re-run `python src/init_vector_db.py` to rebuild the vector store.

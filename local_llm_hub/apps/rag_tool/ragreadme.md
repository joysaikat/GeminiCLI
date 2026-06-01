# Local RAG Tool

A private, local Retrieval-Augmented Generation (RAG) system running on Apple Silicon.

## Setup & Activation

This project uses a dedicated virtual environment named `rag_env`.

1. **Navigate to the project directory:**
   ```bash
   cd local_llm_hub/apps/rag_tool
   ```

2. **Activate the environment:**
   ```bash
   source rag_env/bin/activate
   ```
   *Your terminal prompt should now show `(rag_env)`.*

## How to Use

### 1. Prepare Documents
Place your `.txt` or `.pdf` files in the `docs/` directory.

### 2. Ingest Data
Process your documents and build the local vector database:
```bash
python3 ingest.py
```
*Note: The first run will download the embedding model (approx 80MB) and Llama 3 (if not already pulled via Ollama).*

### 3. Query the AI
Ask questions based on your private documents:
```bash
python3 query.py "What are the specific rules mentioned in the document?"
```

## Technical Stack
- **LLM Engine:** [Ollama](https://ollama.com/) (running `llama3`)
- **Orchestration:** LangChain
- **Vector Database:** ChromaDB
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Local)

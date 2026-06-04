# Local RAG Tool: Production-Ready Private AI

A private, secure, and local Retrieval-Augmented Generation (RAG) system optimized for enterprise use.

## 🏢 Business Use Cases (Out-of-the-Box)

1. **Internal Knowledge Base:** Instant Q&A over company wikis, HR policies, and technical documentation without data leaving the firewall.
2. **Legal & Compliance Audit:** Rapid search and summarization across thousands of contracts, NDAs, and regulatory filings.
3. **Customer Support Co-pilot:** Give support agents a tool that instantly retrieves product specs and troubleshooting guides to provide accurate answers.
4. **Medical/Research Assistant:** Query vast libraries of proprietary research papers or patient case studies while maintaining strict HIPAA-level privacy.

## 💻 System Specifications

### Local Development (Apple Silicon - Recommended)
- **Minimum:** M1/M2/M3 with 16GB Unified Memory (Llama 3 8B).
- **Optimal:** M2 Max/Ultra with 64GB+ Unified Memory (Llama 3 70B).

### Server Deployment (Linux/Cloud)
- **CPU:** 8+ Cores (AMD EPYC / Intel Xeon).
- **RAM:** 32GB+ System RAM.
- **GPU:** 
  - **Minimum:** NVIDIA RTX 3090/4090 (24GB VRAM).
  - **Optimal:** NVIDIA A100/H100 (80GB VRAM) for high concurrency.
- **Storage:** NVMe SSD (minimum 50GB for models and vector DB).

## 🚀 Setup & Activation
...

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

> **Note:** This system requires **two separate terminal windows/tabs** to be running simultaneously.

### 🏁 Tab 1: Launch the Backend (API)
The "brain" of the system. It handles document processing and Llama 3 communication.
```bash
cd local_llm_hub/apps/rag_tool
source rag_env/bin/activate
python3 api.py
```
*Wait for: `Uvicorn running on http://0.0.0.0:8000`*

### 🎨 Tab 2: Launch the Frontend (Web UI)
The user interface you see in your browser.
```bash
cd local_llm_hub/apps/rag_tool
source rag_env/bin/activate
python3 ui.py
```
*Wait for: `Running on local URL:  http://0.0.0.0:7860`*

### 🌍 Step 3: Open in Browser
Go to **`http://127.0.0.1:7860`** to start chatting!

---

## Troubleshooting "Connection Error"
If the UI says "Connection Error," ensure:
1. **Ollama is running** (`ollama list` should work in terminal).
2. **Backend is running** in its own tab on port 8000.
3. If using a Mac, try accessing `127.0.0.1:8000` instead of `localhost:8000`.

## Technical Stack
- **LLM Engine:** [Ollama](https://ollama.com/) (running `llama3`)
- **Orchestration:** LangChain
- **Vector Database:** ChromaDB
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Local)

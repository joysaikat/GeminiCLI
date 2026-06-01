import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuration
DOCS_PATH = "docs"
DB_PATH = "vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"

def ingest_docs():
    # 1. Load Documents
    print(f"Loading documents from {DOCS_PATH}...")
    # Support for both .txt and .pdf
    loaders = [
        DirectoryLoader(DOCS_PATH, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(DOCS_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader),
    ]
    
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    
    if not docs:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(docs)} documents.")

    # 2. Split Documents into Chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    # 3. Create Embeddings and Store in Vector DB
    print(f"Creating embeddings using {MODEL_NAME} and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    print(f"Ingestion complete! Vector DB saved to {DB_PATH}.")

if __name__ == "__main__":
    # Ensure docs directory exists
    if not os.path.exists(DOCS_PATH):
        os.makedirs(DOCS_PATH)
        print(f"Created {DOCS_PATH} directory. Please add some files and run again.")
    else:
        ingest_docs()

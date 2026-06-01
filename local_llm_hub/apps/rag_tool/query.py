from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

# Configuration
DB_PATH = "vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3"

def query_rag(query_text):
    # 1. Load the Vector DB
    print(f"Loading Vector DB from {DB_PATH}...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    # 2. Retrieve Relevant Documents
    print(f"Retrieving context for: {query_text}")
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query_text)
    
    # 3. Format Context
    context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
    
    # 4. Setup the LLM (Ollama)
    llm = OllamaLLM(model=LLM_MODEL)
    
    # 5. Create the Prompt
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])
    
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    # 6. Run the LLM
    print("Generating answer...")
    response = llm.invoke(prompt)
    
    return {
        "answer": response,
        "context": docs
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Ask a question about your documents: ")
    
    print("\nThinking...")
    result = query_rag(query)
    
    print("\n--- ANSWER ---")
    print(result["answer"])
    print("\n--- SOURCES ---")
    for doc in result["context"]:
        source = doc.metadata.get('source', 'Unknown')
        print(f"- {source}")

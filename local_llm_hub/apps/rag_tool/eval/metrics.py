import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class RAGEvaluator:
    def __init__(self, model_name=LLM_MODEL):
        self.llm = OllamaLLM(model=model_name, base_url=OLLAMA_BASE_URL)

    def _get_llm_score(self, prompt):
        """Helper to get a numeric score (0-10) from the LLM judge."""
        try:
            response = self.llm.invoke(prompt)
            # Simple extraction of a digit from the response
            # In a robust system, we'd use Structured Output/Pydantic
            import re
            match = re.search(r'\b([0-9]|10)\b', response)
            return int(match.group(1)) if match else 5 # Default to middle if unclear
        except Exception as e:
            print(f"Eval Error: {e}")
            return 0

    def evaluate_faithfulness(self, answer, context_docs):
        """Measures if the answer is grounded in the context (no hallucinations)."""
        context_text = "\n---\n".join([doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in context_docs])
        
        prompt = f"""
        You are an expert judge. Rate the FAITHFULNESS of the answer based ONLY on the provided context.
        An answer is faithful if every claim it makes is supported by the context.
        
        CONTEXT:
        {context_text}
        
        ANSWER:
        {answer}
        
        Rate the faithfulness from 0 to 10 (10 being perfectly faithful). 
        Provide only the number.
        """
        return self._get_llm_score(prompt)

    def evaluate_relevance(self, query, answer):
        """Measures if the answer addresses the user's question directly."""
        prompt = f"""
        You are an expert judge. Rate the RELEVANCE of the answer to the user's query.
        Does the answer actually address the question asked?
        
        QUERY: {query}
        ANSWER: {answer}
        
        Rate the relevance from 0 to 10 (10 being perfectly relevant). 
        Provide only the number.
        """
        return self._get_llm_score(prompt)

    def run_full_evaluation(self, query, answer, context_docs):
        print(f"\n--- 🤖 AI Judge: Evaluation Report ---")
        
        faith_score = self.evaluate_faithfulness(answer, context_docs)
        rel_score = self.evaluate_relevance(query, answer)
        
        avg_score = (faith_score + rel_score) / 2
        
        print(f"1. Faithfulness (Anti-Hallucination): {faith_score}/10")
        print(f"2. Answer Relevance: {rel_score}/10")
        print(f"---------------------------------------")
        print(f"OVERALL QUALITY SCORE: {avg_score}/10")
        
        if avg_score >= 8:
            print("Status: ✅ PASS (High Quality)")
        elif avg_score >= 5:
            print("Status: ⚠️ WARNING (Review Recommended)")
        else:
            print("Status: ❌ FAIL (Potential Hallucination or Irrelevance)")

if __name__ == "__main__":
    # Test with sample data
    judge = RAGEvaluator()
    sample_query = "What is the rule about security?"
    sample_context = ["Rule 1: Security First. Never log secrets."]
    sample_answer = "The rule is to keep security first and never log secrets."
    
    judge.run_full_evaluation(sample_query, sample_answer, sample_context)

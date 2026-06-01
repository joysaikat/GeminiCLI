import requests
import json

def chat_with_llm(prompt, model="llama3"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

if __name__ == "__main__":
    print(f"--- Local LLM Chat (Model: llama3) ---")
    user_input = input("You: ")
    print("\nLLM is thinking...")
    response = chat_with_llm(user_input)
    print(f"\nAI: {response}")

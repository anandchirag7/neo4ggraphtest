import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from config import EURON_API_KEY, ANSWER_URL, ANSWER_MODEL
from langchain_openai import ChatOpenAI

def debug_connection():
    print(f"Original ANSWER_URL: {ANSWER_URL}")
    
    # Force try the standard Ollama OpenAI-compatible endpoint
    base_url = "http://localhost:11434/v1"
        
    print(f"Forced base_url for testing: {base_url}")
    print(f"Model: {ANSWER_MODEL}")
    print(f"API Key: {EURON_API_KEY[:5]}...")
    
    llm = ChatOpenAI(
        model=ANSWER_MODEL,
        api_key=EURON_API_KEY,
        base_url=base_url,
        temperature=0
    )
    
    try:
        print("Attempting to invoke LLM...")
        response = llm.invoke("Hello, are you working?")
        print("Success!")
        print(response.content)
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    debug_connection()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from config import EURON_API_KEY, EMBEDDING_URL, EMBEDDING_MODEL
from langchain_openai import OpenAIEmbeddings

def debug_embeddings():
    print(f"Original EMBEDDING_URL: {EMBEDDING_URL}")
    
    # Mirror logic from rag_eval.py
    if "localhost:11434" in EMBEDDING_URL:
        base_url = "http://localhost:11434/v1"
    elif "/embeddings" in EMBEDDING_URL:
        base_url = EMBEDDING_URL.split("/embeddings")[0]
    else:
        base_url = EMBEDDING_URL
        
    print(f"Derived base_url: {base_url}")
    print(f"Model: {EMBEDDING_MODEL}")
    
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=EURON_API_KEY,
        base_url=base_url
    )
    
    try:
        print("Attempting to embed a single string...")
        res1 = embeddings.embed_query("Hello world")
        print(f"Success! Vector dim: {len(res1)}")
        
        print("Attempting to embed a list of strings...")
        res2 = embeddings.embed_documents(["Hello world", "Another string"])
        print(f"Success! Number of vectors: {len(res2)}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    debug_embeddings()

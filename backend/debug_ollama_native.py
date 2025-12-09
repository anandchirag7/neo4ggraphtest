from langchain_community.embeddings import OllamaEmbeddings
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from config import EMBEDDING_MODEL

def debug_native_ollama():
    print(f"Testing Native OllamaEmbeddings with model: {EMBEDDING_MODEL}")
    # OllamaEmbeddings uses the default base_url http://localhost:11434 usually
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url="http://localhost:11434" 
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
    debug_native_ollama()

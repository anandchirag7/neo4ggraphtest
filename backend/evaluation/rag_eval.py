import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import config from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    EURON_API_KEY, 
    ANSWER_URL, ANSWER_MODEL,
    EMBEDDING_URL, EMBEDDING_MODEL
)

def get_eval_llm():
    # Detect if using local Ollama
    if "localhost:11434" in ANSWER_URL:
        # Ollama requires /v1 for OpenAI compatibility
        base_url = "http://localhost:11434/v1"
    elif "/chat/completions" in ANSWER_URL:
        # Standard OpenAI/Euron style
        base_url = ANSWER_URL.split("/chat/completions")[0]
    else:
        base_url = ANSWER_URL
    
    return ChatOpenAI(
        model=ANSWER_MODEL,
        api_key=EURON_API_KEY,
        base_url=base_url,
        temperature=0
    )

from langchain_community.embeddings import OllamaEmbeddings

# ... (rest of imports)

def get_eval_embeddings():
    # Detect if using local Ollama
    if "localhost:11434" in EMBEDDING_URL:
        # Use native OllamaEmbeddings for better compatibility
        return OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url="http://localhost:11434"
        )
    
    # Fallback to OpenAI/Euron
    if "/embeddings" in EMBEDDING_URL:
        base_url = EMBEDDING_URL.split("/embeddings")[0]
    else:
        base_url = EMBEDDING_URL
    
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=EURON_API_KEY,
        base_url=base_url
    )

def evaluate_response(question: str, answer: str, contexts: list[str], ground_truth: str = None):
    """
    Evaluates a single RAG response using Ragas metrics.
    """
    
    # Prepare dataset row
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
    }
    
    if ground_truth:
        data["ground_truth"] = [ground_truth]
        metrics = [faithfulness, answer_relevancy, context_precision]
    else:
        # Without ground truth, we can't measure context_precision accurately 
        # but faithfulness and answer_relevancy are still useful.
        metrics = [faithfulness, answer_relevancy]

    dataset = Dataset.from_dict(data)
    
    # Run evaluation
    llm = get_eval_llm()
    embeddings = get_eval_embeddings()
    
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings
    )
    
    return results

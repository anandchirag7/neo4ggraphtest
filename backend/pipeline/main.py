import base64
import json
import requests
import numpy as np
from pathlib import Path
import sys
import os

# Add parent directory to sys.path to allow importing 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import ANSWER_URL, ANSWER_MODEL, EMBEDDING_URL, EMBEDDING_MODEL, VISION_URL, VISION_MODEL

def llm_infer(prompt: str, model: str = None) -> str:
    """Text inference using a local LLM."""
    if model is None:
        model = ANSWER_MODEL
    
    resp = requests.post(
        ANSWER_URL,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"]

def embed_text(texts, model: str = None) -> np.ndarray:
    """Get embeddings for a list of texts."""
    if model is None:
        model = EMBEDDING_MODEL
    
    if isinstance(texts, str):
        texts = [texts]

    vectors = []
    for t in texts:
        resp = requests.post(
            EMBEDDING_URL,
            json={"model": model, "prompt": t},
            timeout=300,
        )
        resp.raise_for_status()
        emb = resp.json()["embedding"]
        vectors.append(emb)

    return np.array(vectors, dtype="float32")

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def vision_infer(image_path: str,
                 prompt: str = "Describe this image.",
                 model: str = None) -> str:
    """Vision inference: send an image + prompt."""
    if model is None:
        model = VISION_MODEL
    
    img_b64 = encode_image_to_base64(image_path)

    # Some Ollama vision models work through /api/generate with a 'images' field
    resp = requests.post(
        VISION_URL,
        json={
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    # For non-streaming, Ollama returns full text in 'response'
    return data.get("response", "")

if __name__ == "__main__":
    # 1) Text inference
    print("=== LLM Inference ===")
    answer = llm_infer("Explain what engine break-in means in 3 bullet points.")
    print(answer)

    # 2) Embeddings
    print("\n=== Embeddings ===")
    docs = [
        "I rebuilt the engine of my Dominar 400.",
        "I want to run a half marathon in 12 weeks.",
    ]
    vecs = embed_text(docs)
    print("Embeddings shape:", vecs.shape)

    # 3) Vision
    img = "uploads\\7mm\\assets\\images\\7mm_p2_img1.png"  # put an actual image file here
    if Path(img).exists():
        print("\n=== Vision Inference ===")
        v_answer = vision_infer(img, "What do you see in this image?")
        print(v_answer)
    else:
        print("\n(no sample.jpg found; vision demo skipped)")

import numpy as np
from typing import Any
import sys
import os

# Add parent directory to sys.path to allow importing 'pipeline'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.main import embed_text as _embed_text

def embed_text(text: str) -> Any:
    """
    Call the embeddings endpoint.
    Returns a numpy array of the embedding.
    Uses the embed_text function from pipeline.main.
    """
    result = _embed_text(text)
    # If result is already a numpy array with single embedding, extract it
    if isinstance(result, np.ndarray) and len(result.shape) == 2 and result.shape[0] == 1:
        return result[0]
    return result

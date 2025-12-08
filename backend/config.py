
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Local/static storage
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "test")
NEO4J_USER = os.getenv("NEO4J_USER", "test")
NEO4J_PASS = os.getenv("NEO4J_PASS", "test")

# Postgres / pgvector
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB   = os.getenv("PG_DB", "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASS", "522771708@Sbi")

# LLM endpoints (Euron)
# LLM endpoints (Euron)
EMBEDDING_URL = os.getenv("EMBEDDING_URL", "https://api.euron.one/api/v1/euri/embeddings")
ANSWER_URL    = os.getenv("ANSWER_URL", "https://api.euron.one/api/v1/euri/chat/completions")
EURON_API_KEY = os.getenv("EURON_API_KEY", "euri-a1d04833d1748505045e19d2ad09a30e2b0b1b8877b4178a3b19187dc7e275b2")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
ANSWER_MODEL    = os.getenv("ANSWER_MODEL", "gpt-4.1-nano")
VISION_URL      = os.getenv("VISION_URL", "http://localhost:11434/api/generate")
VISION_MODEL    = os.getenv("VISION_MODEL", "llama3.1")
VECTOR_DIM      = int(os.getenv("VECTOR_DIM", "1024"))

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))



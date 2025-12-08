# Enterprise KB App

This is a minimal end-to-end example of an enterprise knowledge base app:

- FastAPI backend
- Neo4j graph for documents/pages/figures
- Postgres + pgvector for semantic search
- React frontend (file upload, graph view, chat)

## Backend

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Set environment variables (or use a .env loader if you prefer):

```bash
export NEO4J_URI=test
export NEO4J_USER=test
export NEO4J_PASS=test

export PG_HOST=test
export PG_PORT=5433
export PG_DB=test
export PG_USER=test
export PG_PASS=test

export EMBEDDING_URL=https://api.euron.one/api/v1/euri/embeddings
export ANSWER_URL=https://api.euron.one/api/v1/euri/chat/completions
export EURON_API_KEY=your_api_key_here
export EMBEDDING_MODEL=ai-ultra
export ANSWER_MODEL=ai-ultra-infer
export VECTOR_DIM=1024
```

Run the API:

```bash
uvicorn main:app --reload
```

The API will be on `http://localhost:8000`.

Key endpoints:

- `POST /upload_pdf` – upload a PDF, extract into Neo4j + pgvector.
- `GET /documents` – list known `doc_id`s.
- `GET /graph/{doc_id}` – simple graph JSON for React.
- `POST /ask` – RAG question; returns answer + figures + docs.

Static images (extracted from PDFs) are served under `/static/...`.

## Frontend

A minimal React app is included under `frontend/`.

```bash
cd frontend
npm install
npm start
```

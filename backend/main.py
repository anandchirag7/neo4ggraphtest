
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid

from config import UPLOAD_DIR, STATIC_DIR
from pipeline.pdf_ingest import extract_pdf_to_raw
from pipeline.rag_graph_builder import ingest_raw_into_graph
from pipeline.pgvector_index import index_doc_in_pgvector
from pipeline.query_rag import rag_answer
from models.neo4j_client import list_all_docs, get_graph_for_doc

app = FastAPI(title="Enterprise KB App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (images/tables)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, run the ingestion pipeline:
      - extract text/images/tables -> raw JSON
      - ingest into Neo4j as a document graph
      - index chunks into pgvector
    """
    try:
        doc_id = f"{Path(file.filename).stem}_{uuid.uuid4().hex[:6]}"
        pdf_path = UPLOAD_DIR / f"{doc_id}.pdf"
        with pdf_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        raw_json = extract_pdf_to_raw(str(pdf_path), str(STATIC_DIR / doc_id))
        
        # Save raw JSON to file for inspection
        json_path = UPLOAD_DIR / f"{doc_id}.json"
        import json
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(raw_json, f, indent=2)
            
        ingest_raw_into_graph(raw_json)
        index_doc_in_pgvector(raw_json["doc_id"])

        return {"status": "ok", "doc_id": raw_json["doc_id"], "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def documents():
    """List documents currently in Neo4j."""
    return list_all_docs()


@app.get("/graph/{doc_id}")
async def graph(doc_id: str):
    """Return a lightweight graph {nodes, links} for a given doc."""
    return get_graph_for_doc(doc_id)


@app.post("/ask")
async def ask(payload: dict):
    """
    RAG entrypoint. Expects: { "question": "..." }
    Returns:
      {
        "answer_text": str,
        "figures": [ { doc_id, node_id, page, image_url, caption } ],
        "documents": [doc_id, ...]
      }
    """
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question'")

    result = rag_answer(question)
    return JSONResponse(result)


@app.post("/evaluate")
async def evaluate_rag(payload: dict):
    """
    Evaluate a QA pair using Ragas.
    Expects: { "question": "...", "ground_truth": "..." (optional) }
    Returns: { "answer": "...", "contexts": [...], "metrics": {...} }
    """
    from evaluation.rag_eval import evaluate_response
    
    question = payload.get("question")
    ground_truth = payload.get("ground_truth")
    
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question'")
        
    # 1. Get RAG answer
    rag_result = rag_answer(question)
    answer = rag_result["answer_text"]
    contexts = rag_result.get("contexts", [])
    
    # 2. Run Evaluation
    try:
        eval_results = evaluate_response(question, answer, contexts, ground_truth)
        
        # Convert Ragas EvaluationResult to dict (it doesn't have .items() directly in some versions)
        # using dict() wrapper usually works for the Result object
        # Try multiple ways to extract dict from EvaluationResult
        results_dict = None
        
        # 1. Try casting to dict directly
        try:
            results_dict = dict(eval_results)
        except Exception:
            pass
            
        # 2. Try .scores attribute
        if not isinstance(results_dict, dict):
            try:
                scores = getattr(eval_results, "scores", None)
                if isinstance(scores, dict):
                    results_dict = scores
            except Exception:
                pass
                
        # 3. Try .to_dict()
        if not isinstance(results_dict, dict):
            try:
                if hasattr(eval_results, "to_dict"):
                    results_dict = eval_results.to_dict()
            except Exception:
                pass

        # 4. Final Fallback: String parsing (It looks like "{'k': v}")
        if not isinstance(results_dict, dict):
            try:
                import ast
                results_dict = ast.literal_eval(str(eval_results))
            except Exception:
                pass

        metrics = {}
        import math
        # Ensure results_dict is actually a dict before iterating
        if isinstance(results_dict, dict):
            for k, v in results_dict.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    metrics[k] = None
                else:
                    metrics[k] = v
        else:
            metrics = {"error": f"Could not parse return type: {type(eval_results)}", "raw": str(eval_results)}
    except Exception as e:
        print(f"Evaluation failed: {e}")
        metrics = {"error": str(e)}
        
    return {
        "answer": answer,
        "contexts": contexts,
        "metrics": metrics
    }

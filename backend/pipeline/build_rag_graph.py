#!/usr/bin/env python3
"""
build_rag_graph.py

Pipeline:
1. Load raw JSON (output of extract_raw_pdf.py)
2. Enrich it into:
   - document-level and page-level natural_language_context
   - figures with image paths
   - tables with CSV paths
   - QA triples (for figures and tables)
3. Write enriched JSON to disk
4. Ingest enriched JSON into Neo4j as nodes / edges

Usage:
    python build_rag_graph.py \
        --raw_json raw_7m.json \
        --enriched_json enriched_7m.json \
        --neo4j_uri neo4j+s://e8452459.databases.neo4j.io \
        --neo4j_user neo4j \
        --neo4j_password Z84_fzAbecAayk_Bk3UMjXPsucpsphdM8kg8JqzMqf0 \
        --clear_graph

You can omit --clear_graph if you don’t want to wipe the DB first.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to sys.path to allow importing 'llm'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.answer_llm import answer_llm
from main import vision_infer

from neo4j import GraphDatabase

# Optional: use pandas to peek at tables to build better summaries
try:
    import pandas as pd  # type: ignore
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ============
#  LLM HOOKS
# ============
# Plug your inference API here (Azure/OpenAI/self-hosted, etc.)

def call_vision_for_figure(image_path: str) -> str:
    """
    Use vision model to analyze a figure image and generate a description.
    Returns a text description of what's in the image.
    """
    if not image_path or not Path(image_path).exists():
        return ""
    
    try:
        prompt = """Analyze this technical diagram or figure from a datasheet. 
Describe what you see including:
- Type of diagram (circuit, block diagram, timing diagram, graph, etc.)
- Key components or elements visible
- Labels, values, or measurements shown
- Overall purpose or what it illustrates

Keep the description concise and technical."""
        
        description = vision_infer(image_path, prompt)
        return description.strip()
    except Exception as e:
        print(f"[ERROR] Vision inference failed for {image_path}: {e}")
        return ""


def call_llm_summary(text: str, max_tokens: int = 256) -> str:
    """
    Summarize the given text using the configured LLM.
    """
    text = (text or "").strip()
    if not text:
        return ""

    prompt = f"""
You are a helpful assistant. Please provide a concise summary of the following text.
Keep the summary under {max_tokens} tokens/words roughly.

TEXT:
{text[:4000]}
"""
    try:
        summary = answer_llm(prompt)
        return summary.strip()
    except Exception as e:
        print(f"[ERROR] Summary generation failed: {e}")
        return text[:max_tokens] + "..."


def call_llm_qa_from_figure(fig_context: str) -> List[Dict[str, str]]:
    """
    Generate QA pairs for a figure using the LLM.
    Expects JSON output.
    """
    if not fig_context:
        return []

    prompt = f"""
You are an expert technical assistant.
Given the context about a figure (title, page summary, etc.), generate 3-5 Question-Answer pairs
that would help a user understand this figure.

CONTEXT:
{fig_context[:2000]}

OUTPUT FORMAT:
Strictly a JSON list of objects, each with "question" and "answer" keys.
Example:
[
  {{"question": "What is shown in the X-axis?", "answer": "Time in seconds"}},
  {{"question": "...", "answer": "..."}}
]

Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
"""
    try:
        response = answer_llm(prompt)
        # Clean up potential markdown code blocks
        cleaned_response = re.sub(r"```json|```", "", response).strip()
        qa_list = json.loads(cleaned_response)
        if isinstance(qa_list, list):
            return qa_list
        return []
    except Exception as e:
        print(f"[ERROR] Figure QA generation failed: {e}")
        return []


def call_llm_qa_from_table(table_context: str) -> List[Dict[str, str]]:
    """
    Generate QA pairs for a table using the LLM.
    Expects JSON output.
    """
    if not table_context:
        return []

    prompt = f"""
You are an expert technical assistant.
Given the context about a table (rows, columns, summary), generate 3-5 Question-Answer pairs
that extract key insights from this table.

CONTEXT:
{table_context[:3000]}

OUTPUT FORMAT:
Strictly a JSON list of objects, each with "question" and "answer" keys.
Example:
[
  {{"question": "What is the maximum voltage?", "answer": "5.5V"}},
  {{"question": "...", "answer": "..."}}
]

Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
"""
    try:
        response = answer_llm(prompt)
        # Clean up potential markdown code blocks
        cleaned_response = re.sub(r"```json|```", "", response).strip()
        qa_list = json.loads(cleaned_response)
        if isinstance(qa_list, list):
            return qa_list
        return []
    except Exception as e:
        print(f"[ERROR] Table QA generation failed: {e}")
        return []


def _process_single_image(img: Dict[str, Any], img_idx: int, page_number: int, 
                          page_nlc: str, doc_id: str) -> Dict[str, Any]:
    """
    Process a single image: analyze with vision model and generate QA pairs.
    This function is designed to be called in parallel via ThreadPoolExecutor.
    
    Args:
        img: Image metadata dictionary
        img_idx: Index of the image (1-based)
        page_number: Page number this image belongs to
        page_nlc: Natural language context of the page
        doc_id: Document ID
    
    Returns:
        Dictionary containing the processed figure object with an 'index' key for sorting
    """
    image_id = img["image_id"]
    fig_title = img.get("title") or f"Figure {img_idx} (auto)"
    image_path = img.get("path")
    
    # Get vision-based description of the image
    vision_description = ""
    if image_path:
        print(f"[INFO] Analyzing image {image_id} with vision model...")
        vision_description = call_vision_for_figure(image_path)
    
    # Enhanced context: title + page summary + vision description
    fig_context_parts = [f"{fig_title}. Page {page_number}.", page_nlc]
    if vision_description:
        fig_context_parts.append(f"Image analysis: {vision_description}")
    fig_context = " ".join(fig_context_parts)

    # Generate QA pairs
    qa_pairs = call_llm_qa_from_figure(fig_context)
    qa_triples = [
        {
            "id": f"{image_id}_qa{q_idx}",
            "class": "QA_Triple",
            "question": qa["question"],
            "answer": qa["answer"]
        }
        for q_idx, qa in enumerate(qa_pairs, start=1)
    ]

    return {
        "figure_id": image_id,
        "page": page_number,
        "type": img.get("type", "unknown"),
        "title": fig_title,
        "natural_language_context": fig_context,
        "vision_description": vision_description,
        "image_meta": img,
        "qa_triples": qa_triples,
        "index": img_idx  # For sorting to maintain original order
    }


# ========================
#  ENRICHMENT FROM RAW
# ========================

def _preview_table_csv(path: str, max_rows: int = 5) -> str:
    """
    Build a small text preview of a CSV table for summarization / QA.
    """
    if not HAS_PANDAS:
        return f"Table at path {path} (pandas not installed, preview not available)."

    try:
        df = pd.read_csv(path, nrows=max_rows)
        return df.to_csv(index=False)
    except Exception as e:
        return f"Table at path {path}, preview error: {e}"


def build_enriched_json(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turn raw per-page JSON into a structured RAG-ready JSON.

    Assumes raw_json structure from extract_raw_pdf.py:
    {
      "doc_id": "...",
      "source_file": "...",
      "assets_dir": "...",
      "pages": [
        {
          "page_number": ...,
          "raw_text": "...",
          "images": [...],
          "tables": [...],
          ...
        }
      ]
    }
    """

    doc_id = raw_json.get("doc_id", "unknown_doc")
    source_file = raw_json.get("source_file")
    assets_dir = raw_json.get("assets_dir")

    # Document-level context: concatenate first few pages for summary
    all_text = " ".join(p.get("raw_text", "") for p in raw_json.get("pages", []))
    doc_summary = call_llm_summary(all_text, max_tokens=512)

    enriched = {
        "doc_id": doc_id,
        "source_file": source_file,
        "assets_dir": assets_dir,
        "num_pages": raw_json.get("num_pages"),
        "document_natural_language_context": doc_summary,
        "pages": []
    }

    for page in raw_json["pages"]:
        page_number = page["page_number"]
        raw_text = page.get("raw_text", "")

        page_nlc = call_llm_summary(raw_text, max_tokens=512)

        page_obj = {
            "page_number": page_number,
            "natural_language_context": page_nlc,
            "raw_text": raw_text,
            "text_blocks": [],
            "figures": [],
            "tables": []
        }

        # For now: a single text block per page (you can later split by headings)
        page_obj["text_blocks"].append(
            {
                "id": f"p{page_number}_text_block_1",
                "type": "text_block",
                "title": None,
                "summary": call_llm_summary(raw_text, max_tokens=256)
            }
        )


        # Figures from images[] - Process in parallel for better performance
        images = page.get("images", [])
        if images:
            print(f"[INFO] Processing {len(images)} images in parallel...")
            
            # Use ThreadPoolExecutor to process images concurrently
            # Cap at 4 workers to avoid overwhelming the vision API
            max_workers = min(len(images), 4)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all image processing tasks
                future_to_img = {
                    executor.submit(
                        _process_single_image, 
                        img, 
                        img_idx, 
                        page_number, 
                        page_nlc, 
                        doc_id
                    ): img
                    for img_idx, img in enumerate(images, start=1)
                }
                
                # Collect results as they complete
                figure_results = []
                for future in as_completed(future_to_img):
                    try:
                        fig_obj = future.result()
                        figure_results.append(fig_obj)
                    except Exception as e:
                        img = future_to_img[future]
                        print(f"[ERROR] Failed to process image {img.get('image_id', 'unknown')}: {e}")
                
                # Sort by original index to maintain order
                figure_results.sort(key=lambda x: x.pop("index"))
                page_obj["figures"].extend(figure_results)

        # Tables
        for t_idx, t in enumerate(page.get("tables", []), start=1):
            table_id = t["table_id"]
            table_path = t.get("path")
            table_preview = _preview_table_csv(table_path) if table_path else ""
            table_context_raw = f"Table {t_idx} on page {page_number} from document {doc_id}.\n{table_preview}"
            table_nlc = call_llm_summary(table_context_raw, max_tokens=256)

            qa_pairs = call_llm_qa_from_table(table_context_raw)
            qa_triples = []
            for q_idx, qa in enumerate(qa_pairs, start=1):
                qa_triples.append(
                    {
                        "id": f"{table_id}_qa{q_idx}",
                        "class": "QA_Triple",
                        "question": qa["question"],
                        "answer": qa["answer"]
                    }
                )

            table_obj = {
                "table_id": table_id,
                "page": page_number,
                "path": table_path,
                "rows": t.get("rows"),
                "cols": t.get("cols"),
                "flavor": t.get("flavor"),
                "natural_language_context": table_nlc,
                "qa_triples": qa_triples
            }

            page_obj["tables"].append(table_obj)

        enriched["pages"].append(page_obj)

    return enriched


# ==================
#  NEO4J INGESTION
# ==================

class Neo4jRAGIngestor:
    """
    Neo4j ingestor for:
      - Document
      - Page
      - TextBlock
      - Figure (with image path)
      - Table (with CSV path)
      - QA_Triple

    Graph shape:

      (Document)-[:HAS_PAGE]->(Page)
      (Page)-[:HAS_TEXT_BLOCK]->(TextBlock)
      (Page)-[:HAS_FIGURE]->(Figure)
      (Page)-[:HAS_TABLE]->(Table)
      (Figure)-[:HAS_QA]->(QA_Triple)
      (Table)-[:HAS_QA]->(QA_Triple)
    """

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_graph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def ingest_enriched_json(self, enriched: Dict[str, Any]):
        with self.driver.session() as session:
            doc_id = enriched["doc_id"]
            source_file = enriched.get("source_file")
            num_pages = enriched.get("num_pages")
            assets_dir = enriched.get("assets_dir")
            doc_nlc = enriched.get("document_natural_language_context", "")

            # Document node
            session.run(
                """
                MERGE (d:Document {doc_id: $doc_id})
                SET d.source_file = $source_file,
                    d.num_pages = $num_pages,
                    d.assets_dir = $assets_dir,
                    d.natural_language_context = $doc_nlc
                """,
                doc_id=doc_id,
                source_file=source_file,
                num_pages=num_pages,
                assets_dir=assets_dir,
                doc_nlc=doc_nlc,
            )

            # Pages + content
            for page in enriched.get("pages", []):
                self._create_page(session, doc_id, page)

    def _create_page(self, session, doc_id: str, page: Dict[str, Any]):
        page_number = page["page_number"]
        nlc = page.get("natural_language_context", "")

        # Page node
        session.run(
            """
            MATCH (d:Document {doc_id: $doc_id})
            MERGE (p:Page {doc_id: $doc_id, page_number: $page_number})
            SET p.natural_language_context = $nlc
            MERGE (d)-[:HAS_PAGE]->(p)
            """,
            doc_id=doc_id,
            page_number=page_number,
            nlc=nlc,
        )

        # Text blocks
        for tb in page.get("text_blocks", []):
            self._create_text_block(session, doc_id, page_number, tb)

        # Figures
        for fig in page.get("figures", []):
            self._create_figure(session, doc_id, page_number, fig)

        # Tables
        for tab in page.get("tables", []):
            self._create_table(session, doc_id, page_number, tab)

    def _create_text_block(self, session, doc_id: str, page_number: int, tb: Dict[str, Any]):
        tb_id = tb["id"]
        session.run(
            """
            MATCH (p:Page {doc_id: $doc_id, page_number: $page_number})
            MERGE (t:TextBlock {id: $tb_id})
            SET t.title = $title,
                t.summary = $summary
            MERGE (p)-[:HAS_TEXT_BLOCK]->(t)
            """,
            doc_id=doc_id,
            page_number=page_number,
            tb_id=tb_id,
            title=tb.get("title"),
            summary=tb.get("summary"),
        )

    def _create_figure(self, session, doc_id: str, page_number: int, fig: Dict[str, Any]):
        figure_id = fig["figure_id"]
        title = fig.get("title")
        nlc = fig.get("natural_language_context", "")
        ftype = fig.get("type", "unknown")
        image_meta = fig.get("image_meta", {}) or {}
        path = image_meta.get("path")
        width = image_meta.get("width")
        height = image_meta.get("height")

        session.run(
            """
            MATCH (p:Page {doc_id: $doc_id, page_number: $page_number})
            MERGE (f:Figure {figure_id: $figure_id})
            SET f.title = $title,
                f.natural_language_context = $nlc,
                f.type = $ftype,
                f.path = $path,
                f.width = $width,
                f.height = $height
            MERGE (p)-[:HAS_FIGURE]->(f)
            """,
            doc_id=doc_id,
            page_number=page_number,
            figure_id=figure_id,
            title=title,
            nlc=nlc,
            ftype=ftype,
            path=path,
            width=width,
            height=height,
        )

        for qa in fig.get("qa_triples", []):
            self._create_qa_triple(session, "Figure", figure_id, qa)

    def _create_table(self, session, doc_id: str, page_number: int, tab: Dict[str, Any]):
        table_id = tab["table_id"]
        nlc = tab.get("natural_language_context", "")
        rows = tab.get("rows")
        cols = tab.get("cols")
        flavor = tab.get("flavor")
        path = tab.get("path")

        session.run(
            """
            MATCH (p:Page {doc_id: $doc_id, page_number: $page_number})
            MERGE (t:Table {table_id: $table_id})
            SET t.natural_language_context = $nlc,
                t.rows = $rows,
                t.cols = $cols,
                t.flavor = $flavor,
                t.path = $path
            MERGE (p)-[:HAS_TABLE]->(t)
            """,
            doc_id=doc_id,
            page_number=page_number,
            table_id=table_id,
            nlc=nlc,
            rows=rows,
            cols=cols,
            flavor=flavor,
            path=path,
        )

        for qa in tab.get("qa_triples", []):
            self._create_qa_triple(session, "Table", table_id, qa)

    def _create_qa_triple(self, session, parent_label: str, parent_id: str, qa: Dict[str, Any]):
        qa_id = qa["id"]
        question = qa["question"]
        answer = qa["answer"]

        # Parent match by label and id key
        if parent_label == "Figure":
            match_parent = "MATCH (p:{label} {{figure_id: $parent_id}})".format(label=parent_label)
        else:  # Table
            match_parent = "MATCH (p:{label} {{table_id: $parent_id}})".format(label=parent_label)

        cypher = f"""
        {match_parent}
        MERGE (q:QA_Triple {{id: $qa_id}})
        SET q.question = $question,
            q.answer = $answer
        MERGE (p)-[:HAS_QA]->(q)
        """

        session.run(
            cypher,
            parent_id=parent_id,
            qa_id=qa_id,
            question=question,
            answer=answer,
        )


# ==============
#  MAIN SCRIPT
# ==============

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_json", required=True, help="Path to raw JSON from extract_raw_pdf.py")
    parser.add_argument("--enriched_json", required=True, help="Where to store enriched JSON")

    parser.add_argument("--neo4j_uri", required=True)
    parser.add_argument("--neo4j_user", required=True)
    parser.add_argument("--neo4j_password", required=True)
    parser.add_argument("--clear_graph", action="store_true", help="Delete all existing nodes/edges first")

    args = parser.parse_args()

    # 1. Load raw JSON
    raw_path = Path(args.raw_json)
    with raw_path.open("r", encoding="utf-8") as f:
        raw_json = json.load(f)

    # 2. Build enriched JSON
    enriched = build_enriched_json(raw_json)

    # 3. Save enriched JSON
    enriched_path = Path(args.enriched_json)
    enriched_path.parent.mkdir(parents=True, exist_ok=True)
    with enriched_path.open("w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    print(f"[OK] Enriched JSON written to {enriched_path}")

    # 4. Ingest into Neo4j
    ingestor = Neo4jRAGIngestor(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
    try:
        if args.clear_graph:
            print("[WARN] Clearing entire graph...")
            ingestor.clear_graph()
        print("[OK] Ingesting enriched JSON into Neo4j...")
        ingestor.ingest_enriched_json(enriched)
        print("[OK] Ingestion complete.")
    finally:
        ingestor.close()


if __name__ == "__main__":
    main()

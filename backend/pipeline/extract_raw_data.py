#!/usr/bin/env python3
"""
extract_raw_data.py

Ingests pre-extracted data (Text + embedded HTML Tables) from a directory structure.
Enriches the text with LLM-generated Section/Subsection headers.
Extracts HTML tables with surrounding context.
Generates a JSON output compatible with the RAG pipeline (similar to extract_raw_pdf.py).

Usage:
    python extract_raw_data.py --input_dir datasheets_ingest --output_dir backend/pipeline
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag

# Add backend to path to import config/llm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import EURON_API_KEY, ANSWER_MODEL, MAX_TOKENS, TEMPERATURE, ANSWER_URL
    import requests
except ImportError:
    # Fallback if config not found (e.g. running standalone)
    print("[WARN] Could not import config. LLM features may fail.")
    EURON_API_KEY = os.getenv("EURON_API_KEY", "")
    ANSWER_URL = os.getenv("ANSWER_URL", "")
    ANSWER_MODEL = os.getenv("ANSWER_MODEL", "gpt-4o")

def llm_enrich_text(text: str) -> str:
    """
    Calls LLM to insert Markdown headers (#, ##) into the raw text
    to improve structure. Keeps content otherwise unchanged.
    """
    if not text.strip():
        return text

    system_prompt = (
        "You are a helpful assistant improving document structure. "
        "Read the following raw text from a technical datasheet page. "
        "Insert logical Markdown headers (# Section, ## Subsection) where appropriate "
        "based on the identifying content (e.g. 'Electrical Characteristics', 'Pin Configuration'). "
        "Do NOT change the original text content, only INSERT headers on new lines. "
        "Do NOT output markdown code blocks, just the text."
    )
    
    user_prompt = f"RAW TEXT:\n{text}\n\nSTRUCTURED TEXT:"

    try:
        if not EURON_API_KEY:
            return text
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {EURON_API_KEY}"
        }
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": ANSWER_MODEL,
            "max_tokens": 2000,
            "temperature": 0.0
        }
        resp = requests.post(ANSWER_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[WARN] LLM enrichment failed: {e}")
        return text

def extract_tables_and_text(html_content: str, page_num: int, doc_id: str, assets_dir: Path) -> Dict[str, Any]:
    """
    Parses mixed HTML/Text content.
    - Extracts <table> elements.
    - Captures context (text before/after).
    - Returns cleaned text (with LLM enrichment) and table metadata.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    tables_meta = []
    cleaned_text_parts = []
    
    # Iterate through top-level elements
    # Using recursive=False to handle top-level chunks
    elements = list(soup.body.children) if soup.body else list(soup.children)
    
    current_text_block = []
    
    table_idx = 1
    
    for el in elements:
        if isinstance(el, Tag) and el.name == 'table':
            # It's a table
            # 1. Flush current text
            if current_text_block:
                cleaned_text_parts.append("".join(current_text_block))
                current_text_block = [] # Reset
            
            # 2. Get Context (last few lines of previous text)
            # Simple approach: take the last non-empty text part
            context_before = cleaned_text_parts[-1][-500:] if cleaned_text_parts else ""
            
            # 3. Process Table
            table_id = f"{doc_id}_p{page_num}_table{table_idx}"
            table_filename = f"{table_id}.html" # Save as HTML or converting to CSV? User said store for inference. HTML is fine.
            # User said "store few lines before and after for inference"
            # I will store the context IN the metadata, and save the table content to file.
            
            # Save table to assets
            tables_dir = assets_dir / "tables"
            tables_dir.mkdir(parents=True, exist_ok=True)
            with open(tables_dir / table_filename, "w", encoding="utf-8") as f:
                f.write(str(el))
            
            # We can't get context_after easily until we process the *next* block. 
            # So we'll store a placeholder or handle it in a second pass?
            # Simpler: Just store the table object in a list and stitch later? 
            # Or just grab the next element if it's text.
            
            context_after = ""
            # Peek at next element
            next_el = el.next_sibling
            if next_el and isinstance(next_el, NavigableString):
                context_after = str(next_el)[:500]
            elif next_el and isinstance(next_el, Tag):
                context_after = next_el.get_text()[:500]

            tables_meta.append({
                "table_id": table_id,
                "page_number": page_num,
                "path": str(tables_dir / table_filename),
                "context_before": context_before,
                "context_after": context_after,
                "raw_html": str(el)[:100] + "..." # Snippet
            })
            table_idx += 1
            
        else:
            # It's text (NavigableString or other Tags like <p>, <div>)
            text = el.get_text() if isinstance(el, Tag) else str(el)
            if text.strip():
                current_text_block.append(text)
    
    # Flush remaining text
    if current_text_block:
        cleaned_text_parts.append("".join(current_text_block))

    # Join all text parts and run LLM enrichment
    full_text = "\n".join(cleaned_text_parts)
    print(f"  [INFO] Enriching text for Page {page_num}...")
    enriched_text = llm_enrich_text(full_text)
    
    return {
        "text": enriched_text,
        "tables": tables_meta
    }

def process_product_folder(product_path: Path, output_dir: Path):
    doc_id = product_path.name
    print(f"Processing Document: {doc_id}")
    
    assets_dir = output_dir.parent / f"{doc_id}_assets" # e.g. backend/pipeline/7m_assets
    
    pages_data = []
    
    # Find page_*.txt files
    # User said "text files like page_1.txt"
    files = sorted(list(product_path.glob("page_*.txt")))
    
    # Sort by number (page_1, page_2, page_10)
    def get_page_num(p):
        m = re.search(r"page_(\d+)", p.name)
        return int(m.group(1)) if m else 0
    
    files.sort(key=get_page_num)
    
    for f in files:
        page_num = get_page_num(f)
        try:
            content = f.read_text(encoding="utf-8")
            
            # If content has <table> tags, treat as HTML. 
            # Even if .txt extension, user said "in form of text and html tables"
            extracted = extract_tables_and_text(content, page_num, doc_id, assets_dir)
            
            pages_data.append({
                "page_number": page_num,
                "raw_text": extracted["text"], # Enriched text
                "images": [], # User said no images
                "tables": extracted["tables"],
                "figure_references": [], # Could extract with regex if needed
                "table_references": [],
                "references": []
            })
            
        except Exception as e:
            print(f"[ERR] Failed to process {f.name}: {e}")

    # Result Object
    result = {
        "doc_id": doc_id,
        "source_file": str(product_path),
        "num_pages": len(pages_data),
        "assets_dir": str(assets_dir),
        "pages": pages_data
    }
    
    # Output File
    output_file = output_dir / f"raw_{doc_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[SUCCESS] Wrote {output_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Root folder containing product subfolders (e.g. datasheet_ingest)")
    parser.add_argument("--output_dir", required=True, help="Directory to save output JSONs")
    args = parser.parse_args()
    
    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    
    if not input_root.exists():
        print(f"[ERR] Input directory {input_root} does not exist.")
        return

    # Iterate over subdirectories (documents)
    for child in input_root.iterdir():
        if child.is_dir():
            process_product_folder(child, output_root)

if __name__ == "__main__":
    main()

import os
import glob
import json
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from config import (
    ANSWER_URL, ANSWER_MODEL, EURON_API_KEY, MAX_TOKENS, TEMPERATURE
)

# Configuration
INPUT_ROOT = "datasheets_extracted" # Folder containing product subfolders
OUTPUT_DIR = "pipeline"

SECTIONING_SYSTEM_PROMPT = """
You are a technical document analyzer. Your task is to read the provided datasheet text and insert SECTION HEADERS to structure it.

1.  Identify logical sections such as "Features", "Applications", "Description", "Absolute Maximum Ratings", "Electrical Specifications", "Pin Configuration", "Typical Performance Curves", etc.
2.  Insert a header on its own line in the format: `[SECTION: <Section Name>]`
3.  Do NOT change any of the original text content. Only insert headers.
4.  Do NOT wrap the output in markdown code blocks.
"""

def llm_section_text(text: str) -> str:
    """
    Sends text to LLM to insert section headers.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }
    
    payload = {
        "model": ANSWER_MODEL,
        "messages": [
            {"role": "system", "content": SECTIONING_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the text:\n\n{text}"}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": False
    }

    try:
        resp = requests.post(ANSWER_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Handle different response formats depending on provider (Euron/OpenAI compatible)
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        elif "message" in data: # Ollama sometimes
             return data["message"]["content"].strip()
        else:
            return text
    except Exception as e:
        print(f"Warning: LLM sectioning failed: {e}")
        return text

def extract_tables_with_context(html_content: str, window_lines=3):
    """
    Extracts <table> sections and surrounding context.
    Returns:
        - clean_text: text with tables replaced by placeholders or removed
        - tables: list of table objects
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = []
    
    # Locate all tables
    found_tables = soup.find_all('table')
    
    for i, tbl in enumerate(found_tables):
        # Generate a unique ID
        table_id = f"table_{i}"
        
        # Get Context
        pre_context = []
        curr = tbl.previous_sibling
        count = 0
        while curr and count < window_lines:
            if isinstance(curr, str) and curr.strip():
                pre_context.insert(0, curr.strip())
                count += 1
            elif hasattr(curr, 'get_text') and curr.get_text().strip():
                pre_context.insert(0, curr.get_text().strip())
                count += 1
            curr = curr.previous_sibling
            
        post_context = []
        curr = tbl.next_sibling
        count = 0
        while curr and count < window_lines:
            if isinstance(curr, str) and curr.strip():
                post_context.append(curr.strip())
                count += 1
            elif hasattr(curr, 'get_text') and curr.get_text().strip():
                post_context.append(curr.get_text().strip())
                count += 1
            curr = curr.next_sibling
            
        tables.append({
            "table_id": table_id,
            "content": str(tbl), # Keep raw HTML
            "context_before": "\n".join(pre_context),
            "context_after": "\n".join(post_context)
        })
        
        # Replace table in soup with a marker
        marker = soup.new_tag("div")
        marker.string = f"[TABLE_REF: {table_id}]"
        tbl.replace_with(marker)

    clean_text = soup.get_text(separator="\n")
    # print(clean_text) # Optional debug
    return clean_text, tables

def process_extracted_folder(base_folder):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Iterate over product folders
    for product_folder in glob.glob(os.path.join(base_folder, "*")):
        if not os.path.isdir(product_folder):
            continue
            
        product_name = os.path.basename(product_folder)
        print(f"Processing Product: {product_name}")
        
        txt_files = sorted(glob.glob(os.path.join(product_folder, "*.txt")))
        
        pages_data = []
        
        for file_path in txt_files:
            print(f"  Reading {os.path.basename(file_path)}...")
            try:
                # Extract page number from filename (assuming page_X.txt)
                filename = os.path.basename(file_path)
                page_num_match = re.search(r"page_(\d+)", filename)
                page_num = int(page_num_match.group(1)) if page_num_match else 0
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 1. Extract Tables & Clean Text
                # Note: If the input is pure text but has <table> tags, BS4 works.
                cleaned_text, extracted_tables = extract_tables_with_context(content)
                
                # 2. LLM Sectioning
                # Only apply if there is substantial text
                if len(cleaned_text.strip()) > 50:
                    sectioned_text = llm_section_text(cleaned_text)
                else:
                    sectioned_text = cleaned_text
                
                pages_data.append({
                    "page_number": page_num,
                    "raw_text": sectioned_text, # "raw" but actually processed/sectioned
                    "images": [], # No images in this flow
                    "tables": extracted_tables,
                    "figure_references": [], # Would need more logic to populate
                    "table_references": [t["table_id"] for t in extracted_tables],
                    "references": []
                })
                
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")
        
        # Create Final JSON
        final_json = {
            "doc_id": product_name,
            "source_file": product_folder, # Reference to folder
            "num_pages": len(pages_data),
            "assets_dir": "", # No assets dir for now
            "pages": pages_data
        }
        
        output_path = os.path.join(OUTPUT_DIR, f"raw_{product_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_json, f, indent=2)
            
        print(f"  Saved {output_path}")

if __name__ == "__main__":
    if not os.path.exists(INPUT_ROOT):
        print(f"Input directory '{INPUT_ROOT}' does not exist.")
        # Determine if we should create it or if the user provided a different path
        # For now, just create it so the script runs without error if empty
        os.makedirs(INPUT_ROOT, exist_ok=True)
        print(f"Created '{INPUT_ROOT}'. Put matching product folders inside.")
    
    process_extracted_folder(INPUT_ROOT)

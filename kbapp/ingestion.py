import os
import base64
import requests
import glob
from pdf2image import convert_from_path

# ---------------- CONFIGURATION ---------------- #
INPUT_FOLDER = "datasheets"       # Folder containing your PDF datasheets
OUTPUT_BASE_FOLDER = "extracted_text" # Base folder for TXT outputs

# API Configuration (Your Local Endpoints)
ANSWER_URL = "http://localhost:11434/api/chat"
ANSWER_MODEL = "gpt-oss:120b-cloud"

VISION_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "llava-phi3"


# ----------------- PROMPTS ----------------- #

# Step 1: Vision Prompt (Same as before - Capture everything)
VISION_PROMPT = """
Analyze this datasheet page image comprehensively. 
1. Transcribe all text headers, paragraphs, and list items.
2. Read every table row by row.
3. Describe all diagrams, charts, schematics, and pin configurations in detail. Capture pin numbers, labels, dimensions, and graph axes.
Provide a raw, detailed textual description of the page content.
"""

# Step 2: Formatting Prompt (Text-Specific)
# This prompt instructs the model to create a readable, structured TEXT document.
FORMATTING_SYSTEM_PROMPT = """
You are a technical documentation specialist. Your task is to format raw, unstructured text from a datasheet page into a clean, readable text document.

**FORMATTING RULES:**
1. **Headers:** Use clear markers for sections (e.g., `[SECTION NAME]`).
2. **Tables:** Format tables clearly using pipes `|` or aligned columns so they are readable in a text file.
3. **Lists:** Use hyphens `-` or asterisks `*` for bullet points.
4. **Diagrams:** Create a section called `[DIAGRAM INFERENCE]` and describe the pinouts, dimensions, or graph data clearly.
5. **Key-Value Pairs:** Keep them on separate lines (e.g., `Parameter: Value`).
6. **No Markdown Code Blocks:** Do not wrap the output in ``` or similar tags. Just return the plain text.

**OUTPUT TEMPLATE:**
================================================================================
--- PAGE METADATA ---
Part Number: (Extract if present)
Manufacturer: (Extract if present)
================================================================================

[SECTION TITLE]
(Content...)

[TABLE: TABLE NAME]
(Formatted rows...)

[DIAGRAM INFERENCE]
(Description of visual elements...)
"""

# ----------------- HELPER FUNCTIONS ----------------- #

def encode_image(image_path):
    """Encodes a saved image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_vision_extraction(base64_img):
    """Step 1: Get raw visual description from LLaVA."""
    payload = {
        "model": VISION_MODEL,
        "prompt": VISION_PROMPT,
        "images": [base64_img],
        "stream": False
    }
    
    try:
        response = requests.post(VISION_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"      [Error] Vision Step failed: {e}")
        return ""

def format_to_text(raw_text, page_num):
    """Step 2: Convert raw text to structured Text using GPT-120b."""
    payload = {
        "model": ANSWER_MODEL,
        "messages": [
            {"role": "system", "content": FORMATTING_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the raw content description for Page {page_num}:\n\n{raw_text}"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1 
        }
    }

    try:
        response = requests.post(ANSWER_URL, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"      [Error] Formatting Step failed: {e}")
        return raw_text # Fallback to raw vision output

# ----------------- CORE PROCESSING LOGIC ----------------- #

def process_single_pdf(pdf_path):
    """
    Handles the full extraction pipeline for a single PDF file.
    """
    filename = os.path.basename(pdf_path)
    file_id = os.path.splitext(filename)[0] # e.g., "7m" from "7m.pdf"
    
    # Create a dedicated folder for this document's output
    doc_output_folder = os.path.join(OUTPUT_BASE_FOLDER, file_id)
    if not os.path.exists(doc_output_folder):
        os.makedirs(doc_output_folder)

    print(f"\n[+] Processing Document: {filename}")
    
    # Convert PDF to Images
    try:
        pages = convert_from_path(pdf_path)
    except Exception as e:
        print(f"   [!] Critical Error converting PDF: {e}")
        return

    # Master text accumulator for the whole document
    full_document_text = f"FILENAME: {filename}\nSOURCE DOCUMENT: {pdf_path}\n\n"

    # Iterate Pages
    for i, page_image in enumerate(pages):
        page_num = i + 1
        print(f"   > Page {page_num}/{len(pages)}...")

        # Save temp image
        temp_img_path = os.path.join(doc_output_folder, f"temp_{page_num}.jpg")
        page_image.save(temp_img_path, "JPEG")
        base64_img = encode_image(temp_img_path)

        # STEP 1: Vision
        raw_vision_data = get_vision_extraction(base64_img)
        
        if not raw_vision_data:
            print("      [!] No vision data. Skipping.")
            if os.path.exists(temp_img_path): os.remove(temp_img_path)
            continue

        # STEP 2: Formatting
        formatted_text = format_to_text(raw_vision_data, page_num)

        # Save Page Text File
        output_filename = os.path.join(doc_output_folder, f"page_{page_num}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(formatted_text)
        
        # Accumulate for master file
        full_document_text += f"\n{'='*80}\n--- PAGE {page_num} ---\n{'='*80}\n\n{formatted_text}\n"

        print(f"      [OK] Saved Page Text.")
        
        # Cleanup temp image
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

    # Save Combined Master File
    master_filename = os.path.join(doc_output_folder, f"{file_id}_full_extraction.txt")
    with open(master_filename, "w", encoding="utf-8") as f:
        f.write(full_document_text)
    print(f"   [OK] Saved Master Text File: {master_filename}")

# ----------------- MAIN EXECUTION ----------------- #

def main():
    # 1. Setup Base Output
    if not os.path.exists(OUTPUT_BASE_FOLDER):
        os.makedirs(OUTPUT_BASE_FOLDER)
    
    # 2. Find all PDFs in the input folder
    pdf_files = glob.glob(os.path.join(INPUT_FOLDER, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{INPUT_FOLDER}'.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    # 3. Batch Process
    for pdf_path in pdf_files:
        try:
            process_single_pdf(pdf_path)
        except Exception as e:
            print(f"   [!] Failed to process {pdf_path}: {e}")
            continue

    print("\nBatch Text Extraction Complete.")

if __name__ == "__main__":
    main()
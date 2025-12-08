
from pathlib import Path
import fitz  # PyMuPDF
import re
import json

FIGURE_RE = re.compile(r"(Figure\s+\d+\.?.*)", re.IGNORECASE)
TABLE_RE = re.compile(r"(Table\s+\d+\.?.*)", re.IGNORECASE)

def extract_pdf_to_raw(pdf_path: str, assets_dir: str) -> dict:
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    assets_dir = Path(assets_dir)
    images_dir = assets_dir / "images"
    tables_dir = assets_dir / "tables"
    images_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)  # tables not implemented yet

    result = {
        "doc_id": pdf_path.stem,
        "source_file": str(pdf_path),
        "assets_dir": str(assets_dir),
        "num_pages": doc.page_count,
        "pages": []
    }

    for page_index in range(doc.page_count):
        page_number = page_index + 1
        page = doc.load_page(page_index)
        raw_text = page.get_text("text")

        figure_refs = FIGURE_RE.findall(raw_text)
        table_refs = TABLE_RE.findall(raw_text)

        images = []
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = doc.extract_image(xref)
            image_bytes = pix["image"]
            ext = pix.get("ext", "png")

            image_id = f"{pdf_path.stem}_p{page_number}_img{img_idx + 1}"
            image_filename = f"{image_id}.{ext}"
            image_path = images_dir / image_filename
            with image_path.open("wb") as f:
                f.write(image_bytes)

            images.append(
                {
                    "image_id": image_id,
                    "page_number": page_number,
                    "path": str(image_path.relative_to(assets_dir.parent.parent)),  # relative to backend/
                    "width": pix.get("width"),
                    "height": pix.get("height"),
                    "ext": ext,
                    "type": "unknown",
                    "title": None,
                }
            )

        page_obj = {
            "page_number": page_number,
            "raw_text": raw_text,
            "images": images,
            "tables": [],  # table extraction can be added later
            "figure_references": figure_refs,
            "table_references": table_refs,
            "references": [],
        }
        result["pages"].append(page_obj)

    doc.close()
    return result

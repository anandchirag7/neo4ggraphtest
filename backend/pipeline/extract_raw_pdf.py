#!/usr/bin/env python3
"""
extract_raw_pdf.py

Usage:
    python extract_raw_pdf.py \
        --pdf_path /mnt/data/RT6220_DS-12.pdf \
        --output raw_rt6220.json \
        --assets_dir ./rt6220_assets

What it does:
- Per-page raw text
- Saves images to:   <assets_dir>/images/<doc>_p<page>_img<idx>.<ext>
- Saves tables (if Camelot installed) to:
                    <assets_dir>/tables/<doc>_p<page>_table<idx>.csv
- Records these paths in the JSON.
"""

import argparse
import json
import re
from pathlib import Path

import fitz  # PyMuPDF

# Optional: table extraction
try:
    import camelot  # type: ignore
    HAS_CAMELOT = True
except ImportError:
    HAS_CAMELOT = False


FIGURE_RE = re.compile(r"(Figure\s+\d+\.?.*)", re.IGNORECASE)
TABLE_RE = re.compile(r"(Table\s+\d+\.?.*)", re.IGNORECASE)


def extract_pdf(pdf_path: str, assets_dir: str):
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)

    assets_dir = Path(assets_dir)
    images_dir = assets_dir / "images"
    tables_dir = assets_dir / "tables"
    images_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "doc_id": pdf_path.stem,
        "source_file": str(pdf_path),
        "num_pages": doc.page_count,
        "assets_dir": str(assets_dir),
        "pages": []
    }

    # --- optional table extraction (Camelot) ---
    # We read once for all pages if available.
    camelot_tables_by_page = {}
    if HAS_CAMELOT:
        try:
            # '1-end' = all pages; adjust flavor as needed
            tables = camelot.read_pdf(
                str(pdf_path), pages="1-end", flavor="lattice"
            )
            for idx, t in enumerate(tables):
                pno = t.page
                camelot_tables_by_page.setdefault(pno, []).append((idx, t))
        except Exception as e:
            print(f"[WARN] Camelot failed on {pdf_path}: {e}")
            camelot_tables_by_page = {}
    else:
        print("[INFO] Camelot not installed, tables[] will be empty.")

    # --- page loop ---
    for page_index in range(doc.page_count):
        page_number = page_index + 1
        page = doc.load_page(page_index)

        # Raw text
        raw_text = page.get_text("text")

        # Figure / table reference strings
        figure_refs = FIGURE_RE.findall(raw_text)
        table_refs = TABLE_RE.findall(raw_text)

        # Images -> save to disk
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
                    "path": str(image_path),
                    "width": pix.get("width"),
                    "height": pix.get("height"),
                    "ext": ext,
                    "type": "unknown",   # refined later in enrichment
                    "title": None        # inferred later
                }
            )

        # Tables -> save each as CSV
        tables_meta = []
        if HAS_CAMELOT and page_number in camelot_tables_by_page:
            for local_idx, (global_idx, table) in enumerate(
                camelot_tables_by_page[page_number]
            ):
                table_id = f"{pdf_path.stem}_p{page_number}_table{local_idx + 1}"
                table_filename = f"{table_id}.csv"
                table_path = tables_dir / table_filename

                # Save as CSV
                table.to_csv(str(table_path))

                tables_meta.append(
                    {
                        "table_id": table_id,
                        "page_number": page_number,
                        "path": str(table_path),
                        "rows": table.df.shape[0],
                        "cols": table.df.shape[1],
                        "flavor": table.flavor,
                        "global_index": int(global_idx)
                    }
                )

        page_obj = {
            "page_number": page_number,
            "raw_text": raw_text,
            "images": images,
            "tables": tables_meta,
            "figure_references": figure_refs,
            "table_references": table_refs,
            "references": []
        }

        result["pages"].append(page_obj)

    doc.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_path", required=True, help="Path to PDF file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument(
        "--assets_dir",
        required=True,
        help="Directory where images/ and tables/ will be stored",
    )

    args = parser.parse_args()

    data = extract_pdf(args.pdf_path, args.assets_dir)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Raw PDF extraction written to {out_path}")
    print(f"[OK] Images saved under {Path(args.assets_dir) / 'images'}")
    print(f"[OK] Tables saved under {Path(args.assets_dir) / 'tables'}")


if __name__ == "__main__":
    main()

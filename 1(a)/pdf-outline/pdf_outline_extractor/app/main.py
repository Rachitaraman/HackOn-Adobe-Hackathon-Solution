import os
import sys
import fitz  # PyMuPDF
import json

from pytesseract import image_to_string
from PIL import Image
import re

# Ensure local import works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_extract_kit.core.extractor import extract_outline as process_pdf


from utils import is_scanned_pdf


INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"


def extract_outline_with_pdfkit(pdf_path):
    try:
        result = process_pdf(pdf_path)
        outline = []
        for h in result.get("headings", []):
            outline.append({
                "level": h.get("level", "").upper(),
                "text": h.get("text", "").strip(),
                "page": h.get("page_num", -1)
            })
        title = result.get("title", "Untitled Document")
        return {"title": title, "outline": outline}
    except Exception as e:
        return {"error": f"PDF-Extract-Kit failed: {str(e)}", "outline": []}


def extract_outline_with_ocr(doc):
    print("🔍 Extracting using OCR + heuristic heading patterns...")
    outline = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        try:
            text = image_to_string(img, lang="fra+eng")  # Add other langs if needed
        except Exception as e:
            print(f"⚠️ OCR failed on page {page_num + 1}: {e}")
            continue

        lines = text.split("\n")
        for line in lines:
            clean = line.strip()
            if not clean:
                continue

            # Heading detection heuristics
            if re.match(r"^\d+(\.\d+)*\s+[A-Z].*", clean) or re.match(r"^[A-Z][A-Z\s\-:]{4,}$", clean):
                outline.append({
                    "level": "H2",
                    "text": clean,
                    "page": page_num + 1
                })

    return {
        "title": "OCR-Detected Headings",
        "outline": outline
    }


def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)

    # Use OCR directly if scanned
    if is_scanned_pdf(doc):
        return extract_outline_with_ocr(doc)

    # Try PDF-Extract-Kit first
    result = extract_outline_with_pdfkit(pdf_path)

    # If outline is empty, fallback to OCR
    if not result.get("outline"):
        print("⚠️ No outline found with PDF-Extract-Kit. Falling back to OCR...")
        return extract_outline_with_ocr(doc)

    return result


def main():
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input folder not found: {INPUT_DIR}")
        exit(1)

    if not os.listdir(INPUT_DIR):
        print(f"⚠️ Input folder is empty: {INPUT_DIR}")
        exit(1)

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(INPUT_DIR, filename)
        print(f"📄 Processing: {filename}")

        try:
            result = extract_outline(pdf_path)
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✔ Done → {output_path}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")


if __name__ == "__main__":
    main()

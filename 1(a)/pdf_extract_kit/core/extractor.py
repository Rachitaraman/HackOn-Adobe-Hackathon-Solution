import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import re
import os

def extract_text_blocks(doc):
    blocks = []
    for page_num, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                if line_text:
                    blocks.append({
                        "text": line_text,
                        "page": page_num
                    })
    return blocks

def heuristic_headings(blocks):
    headings = []
    seen = set()
    for block in blocks:
        text = block["text"]
        if len(text.split()) > 15 or len(text) < 4:
            continue
        if re.search(r'\d+\.\d+(\.\d+)*', text) or text.isupper():
            key = (text.lower(), block["page"])
            if key not in seen:
                seen.add(key)
                headings.append({
                    "level": "H2",
                    "text": text,
                    "page": block["page"]
                })
    return headings

def ocr_fallback(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    headings = []
    for i, image in enumerate(pages):
        text = pytesseract.image_to_string(image)
        lines = text.split("\n")
        for line in lines:
            clean = line.strip()
            if 4 < len(clean) < 120 and re.search(r'[A-Za-z]{3,}', clean):
                if clean.isupper() or re.match(r'\d+\.\d+', clean):
                    headings.append({
                        "level": "H1",
                        "text": clean,
                        "page": i + 1
                    })
    return headings

def extract_title_from_doc(doc):
    text = doc[0].get_text("text")
    lines = [line.strip() for line in text.split("\n") if 6 < len(line.strip()) < 120]
    return " ".join(lines[:3]) if lines else "Untitled PDF"

def extract_outline(path):
    try:
        doc = fitz.open(path)
        blocks = extract_text_blocks(doc)
        headings = heuristic_headings(blocks)
        if not headings:
            raise ValueError("No headings detected, use OCR.")
        return {
            "title": extract_title_from_doc(doc),
            "outline": headings
        }
    except Exception:
        ocr_headings = ocr_fallback(path)
        return {
            "title": "OCR-Detected Headings",
            "outline": ocr_headings
        }



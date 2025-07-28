import fitz  # PyMuPDF
import re
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from sklearn.cluster import KMeans


MIN_WORDS = 1
MAX_WORDS = 14


def extract_text_blocks(doc):
    blocks = []
    for page_num, page in enumerate(doc, start=1):
        if not page.get_text("text").strip():
            continue  # skip empty pages (for OCR fallback)
        blocks_raw = page.get_text("dict")["blocks"]
        for block in blocks_raw:
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                main_span = spans[0]
                text = main_span["text"].strip()
                if not text or len(text.split()) > MAX_WORDS:
                    continue
                blocks.append({
                    "text": text,
                    "font_size": main_span["size"],
                    "bold": bool(main_span["flags"] & 2),
                    "page": page_num
                })
    return blocks


def filter_heading_candidates(blocks):
    candidates = []
    for b in blocks:
        text = b["text"]

        if len(text) < 5:
            continue
        if not re.search(r"[A-Za-z]{3,}", text):
            continue
        if text.lower() in {"the", "and", "this", "that"}:
            continue
        if not (b["bold"] or text.isupper() or re.match(r"^\d+(\.\d+)*", text)):
            continue
        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text):
            continue  # exclude dates

        candidates.append(b)
    return candidates


def cluster_headings(blocks):
    if len(blocks) < 2:
        return []
    font_sizes = np.array([[b["font_size"]] for b in blocks])
    k = min(4, len(set(fs[0] for fs in font_sizes)))
    if k < 1:
        return []
    kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
    labels = kmeans.fit_predict(font_sizes)
    cluster_order = sorted(
        [(label, kmeans.cluster_centers_[label][0]) for label in set(labels)],
        key=lambda x: -x[1]
    )
    level_map = {label: f"H{i+1}" for i, (label, _) in enumerate(cluster_order)}

    result = []
    for idx, b in enumerate(blocks):
        level = level_map[labels[idx]]
        result.append({
            "level": level,
            "text": b["text"],
            "page": b["page"]
        })
    return result


def deduplicate(headings):
    seen = set()
    output = []
    for h in headings:
        key = (h["text"].lower(), h["page"])
        if key not in seen:
            seen.add(key)
            output.append(h)
    return output


def extract_title_from_doc(doc):
    lines = []
    for line in doc[0].get_text("text").split("\n"):
        cleaned = line.strip()
        if 6 < len(cleaned) < 100:
            lines.append(cleaned)
        if len(lines) >= 3:
            break
    return " ".join(lines).strip() or "Untitled PDF"


def process_pdf(path):
    doc = fitz.open(path)
    text_blocks = extract_text_blocks(doc)

    if text_blocks:
        candidates = filter_heading_candidates(text_blocks)
        clustered = cluster_headings(candidates)
        cleaned = deduplicate(clustered)
        if cleaned:
            return {
                "title": extract_title_from_doc(doc),
                "outline": cleaned
            }

    # OCR fallback
    print("⚠️ No outline found with PDF-Extract-Kit. Falling back to OCR...")

    images = convert_from_path(path, dpi=300)
    ocr_blocks = []
    for page_num, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img)
        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line.split()) > MAX_WORDS or len(line) < 4:
                continue
            if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", line):
                continue
            if re.match(r"^[A-Z \d:\.\-\(\)]+$", line) or re.match(r"^\d+(\.\d+)*\s", line):
                ocr_blocks.append({
                    "text": line,
                    "page": page_num,
                    "font_size": 12.0,
                    "bold": False
                })

    candidates = filter_heading_candidates(ocr_blocks)
    clustered = cluster_headings(candidates)
    cleaned = deduplicate(clustered)
    return {
        "title": "OCR-Detected Headings",
        "outline": cleaned
    }


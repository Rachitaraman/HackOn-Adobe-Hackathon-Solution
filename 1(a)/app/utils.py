import os
import json
import pytesseract
import re
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from sklearn.cluster import KMeans

def save_json(data, filename, output_dir="/app/output"):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def is_scanned_pdf(doc):
    for page in doc:
        if page.get_text("text").strip():
            return False
    return True

def is_heading_candidate(text):
    # Regex-based heuristic
    return (
        len(text.strip()) > 5 and (
            bool(re.match(r"^\d+(\.\d+)*\s", text)) or  # e.g., 1., 1.1.2 Title
            text.isupper() or
            bool(re.match(r"^[A-Z][A-Za-z\s]{3,}$", text))  # Title Case
        )
    )

def extract_text_blocks_with_ocr(doc):
    """Returns block-wise text + bounding boxes"""
    blocks = []
    for page_num, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        # data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        MULTI_LANG = "eng+hin+deu+fra"  # You can extend this

        data = pytesseract.image_to_data(img, lang=MULTI_LANG, output_type=pytesseract.Output.DICT)


        n = len(data["text"])
        for i in range(n):
            text = data["text"][i].strip()
            if text:
                block = {
                    "text": text,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "page": page_num + 1
                }
                blocks.append(block)
    return blocks

def cluster_headings(blocks):
    """Cluster based on visual size (height + top)"""
    candidates = [b for b in blocks if is_heading_candidate(b["text"])]
    if not candidates:
        return []

    X = np.array([[b["height"]] for b in candidates])
    k = min(3, len(set([b["height"] for b in candidates])))  # Avoid too many clusters
    kmeans = KMeans(n_clusters=k, n_init="auto").fit(X)

    clustered = []
    for i, block in enumerate(candidates):
        level = f"H{1 + (kmeans.labels_[i])}"
        clustered.append({
            "level": level,
            "text": block["text"],
            "page": block["page"]
        })
    return clustered

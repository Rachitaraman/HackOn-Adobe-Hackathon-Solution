# HackOn-Adobe-Hackathon-Solution

# 📚 Adobe Hackathon 2025 – Challenge 1: PDF Outline Extraction + Persona-Based Ranking

This repository contains the complete solution for **Challenge 1** from the Adobe India Hackathon 2025. It includes two main modules:

- ✅ **1(a) PDF Outline Extractor** – Extracts a clean, structured outline (H1–H4) from both text-based and scanned PDFs.
- ✅ **1(b) Persona-Based Heading Ranker** – Ranks the extracted headings based on their relevance to a user-defined persona query.

---

## 🧩 Challenge Breakdown

### 📘 1(a) PDF Outline Extractor

This module extracts structured outlines (like H1–H4 headings) from unstructured PDF documents. It works with both digital (text-based) and scanned (image-based) PDFs using OCR fallback when necessary.

#### 🔧 Features

- 📝 Extracts hierarchical headings (H1–H4) from PDFs
- 🧠 Uses font size, alignment, layout to infer headings
- 🔍 Integrates Tesseract OCR for scanned/image-based PDFs
- 🌐 Multilingual OCR support (English, Hindi, French, German, etc.)
- 📄 Outputs structured `title` and `outline` in JSON format
- 🐳 Fully dockerized for portable usage

#### 🛠️ Tech Stack

- **Python** – Scripting & orchestration
- **PyMuPDF (fitz)** – PDF parsing and layout extraction
- **Tesseract OCR** (`pytesseract`) – Image-based text recognition
- **pdf2image** – Converts PDF pages to images (for OCR)
- **scikit-learn** – Optional: clusters font sizes for level inference

---

### 📗 1(b) Persona-Based Heading Ranking

This module ranks the extracted headings based on their relevance to a natural language **persona query** (e.g. _"topics for beginners"_, _"for researchers"_).

#### 🚀 Problem Statement

Given:

- A persona query (free text)
- The outline (JSON) generated in part 1(a)

👉 The task is to **rank headings** from the outline that are most relevant to the persona.

#### 🧠 Solution Strategy

- Treats the problem as an **information retrieval and ranking** task.
- Uses **TF-IDF vectorization** to compare persona query with heading text.
- Optional features:
  - Presence of numbers (e.g., "Step 1", "1.1")
  - Heading length
  - Heading level (H1/H2/H3)
- Uses a scoring model (TF-IDF similarity + heuristics or ML) to rank.

#### ✅ Output

A ranked list of headings (from each document), sorted by their relevance to the persona.

---

## 📁 Folder Structure
adobe/
├── 1(a)/
│ └── code/
│ ├── main.py # Outline extractor
│ ├── Dockerfile
│ └── requirements.txt
│
├── 1(b)/
│ └── code/
│ ├── main.py # Persona handler
│ ├── persona_classifier.py # TF-IDF ranker
│ ├── features.py # Feature engineering
│ ├── Dockerfile
│ └── requirements.txt
│
├── input/
│ ├── file01.pdf, ...
│ └── collection-1/
│ └── *.pdf
│ └── collection-2/
│ └── collection-3/
│
├── output/
│ ├── extracted/ # From 1(a)
│ └── ranked/ # From 1(b)
│
├── adobe_case.pdf # Official problem statement
└── README.md

---

## ⚙️ Setup & Run Instructions

### ✅ Python (Local Setup)

1. **Install dependencies**

For 1(a):
```bash
cd adobe/1(a)/code
pip install -r requirements.txt

▶️ Run
bash
Copy code
# 1(a) – Extract outlines
docker run --rm \
  -v "$(pwd)/../../input:/app/input" \
  -v "$(pwd)/../../output/extracted:/app/output" \
  adobe-outline

# 1(b) – Rank by persona
docker run --rm \
  -v "$(pwd)/../../output/extracted:/app/input" \
  -v "$(pwd)/../../output/ranked:/app/output" \
  adobe-ranker

# PDF Outline Extractor

This project extracts structured outlines (like H1–H4 headings) from PDF files — including both text-based and scanned/image-only PDFs. It outputs a clean, table-of-contents-style JSON structure.

## Features

- 📝 Extracts headings from both text and scanned PDFs
- 🔍 Fallback OCR using Tesseract for image-based documents
- 🌐 Supports multilingual documents (Tesseract OCR supports English, French, Hindi and German)
- 🎯 Returns structured JSON output with heading levels (H1–H4) and page numbers
- 🐳 Dockerized for easy setup and deployment

## Tech Stack & Libraries

- *Python* – Core scripting and orchestration
- **PyMuPDF (fitz)** – High-quality PDF text extraction
- **Tesseract OCR (pytesseract)** – For scanned image PDFs and multilingual text recognition
- *pdf2image* – Converts PDF pages to images (for OCR)
- *scikit-learn* – Clusters font sizes to determine heading levels (H1–H4)

## OCR Language Support

Tesseract can extract text from PDFs in various languages by changing the OCR language setting (e.g., eng, hin, fra, etc.). Language training data must be available inside the container or host system.

## Usage (Docker)

```bash
# Build the Docker image
docker build -t pdf-outline .

# Run the container to process all PDFs in app/input/
docker run --rm \
  -v "$(pwd)/app/input:/app/input" \
  -v "$(pwd)/app/output:/app/output" \
  pdf-outline

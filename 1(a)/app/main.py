import os
import json
from pdf_extract_kit.core.extractor import extract_outline as process_pdf


INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(".pdf"):
        continue
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename.rsplit(".", 1)[0] + ".json")

    print(f"📄 Processing: {filename}")
    try:
        result = process_pdf(input_path)
        if not result["outline"]:
            print("⚠️ No outline found with PDF-Extract-Kit. Falling back to OCR...")
        else:
            print("✔ Done →", output_path)
    except Exception as e:
        print("❌ Error:", e)
        result = {"title": "Untitled", "outline": []}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
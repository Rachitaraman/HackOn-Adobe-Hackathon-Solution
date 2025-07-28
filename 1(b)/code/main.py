# main.py
import json
import os
from pathlib import Path
from datetime import datetime
from persona_classifier import rank_relevant_headings, get_refined_text_for_section
# If you used PyMuPDF (fitz) for parsing:
# import fitz # Assuming PyMuPDF is installed

# --- Configuration ---
# Your project's top-level folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent # Points to 1(b)
INPUT_PDF_DIR = PROJECT_ROOT / "Collection 1" / "pdf" # Where original PDFs are
INPUT_JSON_DIR = PROJECT_ROOT / "Collection 1" # Where 1A output JSONs are (e.g., doc1.json, doc2.json)
OUTPUT_FILE = PROJECT_ROOT / "Collection 1" / "challenge1b_output.json" # Output as per 1B spec

# Define the persona and task (as per problem statement)
# You would get these from an input file if not hardcoded for testing
PERSONA_DATA = {
    "name": "PhD Researcher in Computational Biology",
    "description": "Expert in computational methods for biological research, focusing on molecular dynamics and bioinformatics."
}

TASK_DATA = {
    "description": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks in Graph Neural Networks for Drug Discovery."
}

# --- PDF Parsing (Placeholder/Example - You need to implement this robustly) ---
# This is crucial. Your current main.py only reads JSONs from 1A.
# To get 'refined_text', you need the actual text content of sections from PDFs.
def extract_full_text_and_sections_from_pdf(pdf_path, headings_from_1a):
    """
    PLACEHOLDER: This function should parse a PDF and return its full text
    and, crucially, the full text content for each identified section.
    
    In a real scenario, you'd iterate through pages, extract text, and
    use the heading page numbers/levels to determine section boundaries.
    
    Args:
        pdf_path (Path): Path to the PDF file.
        headings_from_1a (list): List of headings from 1A output, e.g.,
                                 [{"text": "Intro", "level": "H1", "page": 1}, ...]

    Returns:
        dict: {
            "full_text": "...",
            "sections_content": {
                "Section Title 1": "Full text content of Section 1",
                "Section Title 2": "Full text content of Section 2",
                ...
            }
        }
    """
    # For demonstration, we'll return dummy content.
    # YOU NEED TO IMPLEMENT THIS USING PDF PARSING LIBRARIES (e.g., pdfplumber or PyMuPDF).
    
    # Example using PyMuPDF (fitz):
    # doc_full_text = ""
    # sections_content = {}
    # try:
    #     doc = fitz.open(pdf_path)
    #     for page_num in range(doc.page_count):
    #         page = doc.load_page(page_num)
    #         doc_full_text += page.get_text() + "\n"
    #
    #     # This part is complex: linking 1A headings to actual text blocks.
    #     # You'd typically iterate through text blocks, identify headings,
    #     # and then collect text until the next heading of a similar or higher level.
    #     # For simplicity here, we'll just assume a fixed placeholder for sections_content
    #     # You need to map the 'headings_from_1a' to text blocks in the PDF.
    #     for h in headings_from_1a:
    #         # This is a *very* simplified placeholder.
    #         # In reality, you'd extract text between heading 'h' and the next heading
    #         # or end of document.
    #         sections_content[h["text"]] = f"Dummy content for '{h['text']}' on page {h['page']} from {pdf_path.name}. This text should be extracted directly from the PDF under this heading."
    #
    # except Exception as e:
    #     print(f"Error parsing PDF {pdf_path}: {e}")
    # return {"full_text": doc_full_text, "sections_content": sections_content}
    
    # --- Dummy Implementation for now to allow the rest of the code to run ---
    dummy_sections_content = {}
    for h in headings_from_1a:
        # Placeholder for actual content extraction under each heading
        dummy_sections_content[h["text"]] = f"This is placeholder content for the section titled '{h['text']}' from page {h['page']}." \
                                            f" For the 'Graph Neural Networks' example, this might contain details about GNN architectures, training methodologies, or dataset usage." \
                                            f" For 'Performance metrics', it would elaborate on benchmarks and results."
    
    return {
        "full_text": "This is the full dummy text of the PDF. For a real solution, parse the PDF using a library.",
        "sections_content": dummy_sections_content
    }


def process_documents_for_1b():
    all_extracted_sections = []
    all_sub_section_analysis = []
    input_document_filenames = []

    # Get all JSON files from Round 1A output (assuming they are named like doc_name.json)
    json_files = sorted(INPUT_JSON_DIR.glob("*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {INPUT_JSON_DIR}. Ensure Round 1A outputs are present.")
        return

    # Assuming the PDF names correspond to JSON names (e.g., doc1.json -> doc1.pdf)
    for json_file in json_files:
        doc_id = json_file.stem # e.g., "document_1"
        pdf_filename = f"{doc_id}.pdf"
        pdf_path = INPUT_PDF_DIR / pdf_filename

        if not pdf_path.exists():
            print(f"⚠️ Warning: Corresponding PDF '{pdf_filename}' not found for '{json_file.name}'. Skipping sub-section analysis for this document.")
            # If PDF not found, we can still process headings but cannot do sub-section analysis
            # Continue to next file or handle as appropriate. For now, assume PDF exists.
            continue
            
        input_document_filenames.append(pdf_filename)

        print(f"Processing document: {pdf_filename}")

        # 1. Load headings from 1A's JSON output
        with open(json_file, "r", encoding="utf-8") as f:
            json_1a_data = json.load(f)
        
        # Ensure 'outline' key exists and is a list
        if "outline" not in json_1a_data or not isinstance(json_1a_data["outline"], list):
            print(f"❌ '{json_file.name}' does not contain a valid 'outline' key. Skipping.")
            continue

        headings_from_1a = []
        for item in json_1a_data["outline"]:
            # Ensure required keys exist for a heading
            if all(k in item for k in ["text", "level", "page"]):
                headings_from_1a.append({
                    "text": item["text"],
                    "level": item["level"],
                    "page": item["page"]
                })
            else:
                print(f"⚠️ Malformed heading entry in {json_file.name}: {item}")


        # 2. Extract full text content for sections from the actual PDF
        # This is where your PDF parsing library comes in.
        pdf_content = extract_full_text_and_sections_from_pdf(pdf_path, headings_from_1a)
        sections_full_text = pdf_content["sections_content"]


        # 3. Rank relevant headings
        ranked_sections = rank_relevant_headings(
            headings_from_1a,
            PERSONA_DATA["description"],
            TASK_DATA["description"],
            top_n=20 # Get more than 10 to pick best for sub-section analysis later
        )

        # 4. Populate extracted_sections and sub_section_analysis
        for rank, section in enumerate(ranked_sections):
            # Assign importance_rank based on sorted order (1-based)
            all_extracted_sections.append({
                "document": pdf_filename,
                "page_number": section["page"],
                "section_title": section["text"],
                "importance_rank": rank + 1 # 1-based ranking
            })

            # For sub-section analysis, get refined text only for top N sections (e.g., top 5-10)
            # You can decide how many sections' sub-sections to analyze
            if rank < 10: # Analyze sub-sections for the top 10 relevant main sections
                section_title = section["text"]
                full_section_content = sections_full_text.get(section_title, "") # Get content from our PDF parsing
                
                if full_section_content:
                    refined_text = get_refined_text_for_section(
                        full_section_content,
                        PERSONA_DATA["description"],
                        TASK_DATA["description"]
                    )
                    if refined_text: # Only add if we actually found refined text
                        all_sub_section_analysis.append({
                            "document": pdf_filename,
                            "refined_text": refined_text,
                            "page_number": section["page"] # Use the section's start page number
                        })
                else:
                    print(f"⚠️ Warning: No content found for section '{section_title}' in {pdf_filename}. Skipping sub-section analysis.")

    # Final Output Structure
    final_output = {
        "metadata": {
            "input_documents": input_document_filenames,
            "persona": PERSONA_DATA,
            "job_to_be_done": TASK_DATA,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": all_extracted_sections,
        "sub_section_analysis": all_sub_section_analysis
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        json.dump(final_output, out_f, indent=2, ensure_ascii=False)
    print(f"✅ Output written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_documents_for_1b()
    
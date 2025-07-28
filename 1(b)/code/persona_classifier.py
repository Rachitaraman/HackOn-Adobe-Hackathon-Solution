# persona_classifier.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from features import clean_text

def calculate_relevance_scores(query_text, texts_to_compare):
    """
    Calculates cosine similarity scores between a query and a list of texts.
    """
    if not texts_to_compare:
        return []

    cleaned_texts = [clean_text(t) for t in texts_to_compare]
    # Fit on all texts including the query for a consistent vocabulary
    vectorizer = TfidfVectorizer().fit(cleaned_texts + [clean_text(query_text)])

    query_vec = vectorizer.transform([clean_text(query_text)])
    texts_vecs = vectorizer.transform(cleaned_texts)

    scores = cosine_similarity(query_vec, texts_vecs).flatten()
    return scores.tolist()

def rank_relevant_headings(headings, persona_description, task_description, top_n=10):
    """
    Ranks document headings by relevance to persona and task.
    """
    persona_task_text = f"{persona_description} {task_description}"

    results = []
    heading_texts = [h["text"] for h in headings]
    scores = calculate_relevance_scores(persona_task_text, heading_texts)

    for i, h in enumerate(headings):
        results.append({
            "text": h["text"],
            "page": h["page"],
            "level": h["level"], # Keep level for output
            "score": round(float(scores[i]), 4)
        })

    results.sort(key=lambda x: -x["score"])
    return results[:top_n] # Ensure to return up to top_n

def get_refined_text_for_section(section_full_text, persona_description, task_description, max_sentences=3):
    """
    Identifies the most relevant sentences/paragraphs within a given section's full text.
    """
    if not section_full_text:
        return ""

    persona_task_text = f"{persona_description} {task_description}"

    # Simple sentence tokenization (can be improved with NLTK if allowed and fits size)
    # For now, split by common delimiters.
    # Note: `clean_text` removes punctuation, so this won't work well if you keep it aggressive.
    # If clean_text removes periods, you might need to split by spaces and group words.
    # For a proper solution, consider not removing periods in clean_text
    # or using a proper sentence tokenizer (e.g., from NLTK if feasible).
    
    # A safer approach without relying heavily on punctuation after aggressive clean_text:
    # Just split into chunks (e.g., paragraphs or fixed-size text blocks)
    # Let's assume input 'section_full_text' already has some paragraph breaks or you can chunk it.
    
    # Simple paragraph splitting (can be improved)
    paragraphs = [p.strip() for p in section_full_text.split('\n\n') if p.strip()]
    
    if not paragraphs: # If no paragraphs, try splitting by sentences if clean_text was less aggressive
        # Fallback if paragraphs didn't work (e.g., single long paragraph)
        # This requires `clean_text` to *not* remove periods.
        # If `clean_text` is too aggressive, sentences won't be easily split.
        # For demonstration, let's assume `clean_text` is adjusted or we deal with it.
        sentences = re.split(r'(?<=[.!?])\s+', section_full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        texts_to_analyze = sentences if sentences else [section_full_text]
    else:
        texts_to_analyze = paragraphs


    if not texts_to_analyze:
        return ""

    scores = calculate_relevance_scores(persona_task_text, texts_to_analyze)

    # Combine text with scores and sort
    scored_texts = sorted(zip(texts_to_analyze, scores), key=lambda x: x[1], reverse=True)

    # Take top `max_sentences` (or paragraphs) and join them
    refined_parts = [text for text, score in scored_texts[:max_sentences]]
    return " ".join(refined_parts)
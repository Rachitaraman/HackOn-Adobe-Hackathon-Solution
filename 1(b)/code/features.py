# features.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def extract_features(query, headings):
    """
    Extracts similarity and length-based features for each heading given a query.

    Args:
        query (str): The persona query (e.g., "Find content useful for a beginner").
        headings (list[str]): List of heading strings.

    Returns:
        list[dict]: List of feature dictionaries, one per heading.
    """
    features = []
    
    # Combine query + headings for joint vectorization
    texts = [query] + headings
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Cosine similarity between query (0) and each heading (1 to N)
    query_vec = tfidf_matrix[0:1]
    heading_vecs = tfidf_matrix[1:]
    cosine_scores = cosine_similarity(query_vec, heading_vec).flatten()

    for i, heading in enumerate(headings):
        f = {
            "cosine_similarity": float(cosine_scores[i]),
            "heading_length": len(heading),
            "heading_word_count": len(heading.split()),
            "starts_with_number": heading.strip()[0].isdigit()
        }
        features.append(f)

    return features

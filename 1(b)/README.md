# 📘 Challenge 1(b) – Persona-Based Heading Ranking

This module solves the second part of **Adobe Hackathon 2025 – Challenge 1**, where the goal is to **rank the most relevant headings** in a document outline based on a **persona-specific query**.

---

## 🚀 Problem Statement

Given:
- A set of documents (in JSON format) with structured outlines from Challenge 1(a).
- A **natural language query** representing a user persona (e.g., "content for beginners", "for professionals", etc.).

👉 **Task**: Automatically **rank the headings** from each document based on their **relevance to the given query**.

---

## 🧠 Solution Approach

We treat this as an **information retrieval and ranking** task. For each document:

1. **Input**: 
   - JSON output from Challenge 1(a).
   - Persona query (e.g. `"for advanced readers"`).

2. **Features Extracted**:
   - Cosine similarity between query and heading text (using TF-IDF).
   - Whether the heading contains numbers (like "1.1" or "Step 1").
   - Word count of the heading.
   - Heading level (H1/H2/H3).
   - Optional: presence of keywords.

3. **Ranking**:
   - Each heading is scored using a simple ML model (logistic regression or heuristic scoring).
   - Top relevant headings are returned as a ranked list.

---

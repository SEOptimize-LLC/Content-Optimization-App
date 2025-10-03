# Blog Optimizer App - High-Level Architecture

## Overview
The Blog Optimizer is a Streamlit-based web application designed to optimize blog post outlines and drafts using NLP and ML techniques. It supports two modes: Outline Optimization and Draft Optimization. The app processes user-uploaded inputs, applies intelligent enhancements, and outputs optimized content with export options.

## Key Components

### 1. User Interface (Streamlit)
- **Mode Toggle**: A radio button or selectbox to switch between "Outline Optimization" and "Draft Optimization".
- **File Upload Sections**: 
  - Outline Mode: Upload Query Fan-Out Report (Markdown/Text) and Original Outline (Markdown).
  - Draft Mode: Upload Original Draft (Text/Markdown) and Expanded Keyword List (CSV/Markdown/List).
- **Progress Indicators**: Use `st.progress()` and spinners during processing.
- **Output Display**: Render optimized outline or keyword report in Markdown format using `st.markdown()`.
- **Export Buttons**: Buttons to download as Word (.docx) or integrate with Google Docs API for direct export.

### 2. Backend Modules
The backend is modular, with separate Python modules for each functionality:

- **core/inputs.py**: Handles file parsing and validation.
  - Parse Markdown for outlines and reports.
  - Parse CSV/List for keywords.
  - Extract text from drafts.

- **core/outline_optimizer.py**: Implements outline logic.
  - Build contextual knowledge by combining report sub-queries and outline content.
  - Infer search intent using Hugging Face Transformers (e.g., zero-shot classification for intent).
  - Enhance structure: Parse headings with spaCy/NLTK, apply report insights to add/reorganize H2/H3 (5-10 H2s max, merge if >10 using semantic similarity).
  - Add talking points/links: Generate suggestions based on context, optimize SEO by incorporating keywords into headings.
  - Output: Enhanced Markdown outline.

- **core/draft_optimizer.py**: Implements draft logic.
  - Analyze draft: Extract topic embedding using Sentence Transformers.
  - Rank keywords: Compute cosine similarity between keyword embeddings and draft topic.
  - Select top 10+ keywords (threshold-based).
  - Generate insertions: For each keyword, identify relevant paragraphs (via similarity), use Transformers for natural rephrasing (e.g., T5 model for paraphrasing).
  - Skip if keyword present; provide 3 options per keyword with hints (5-10 words from original) and snippets.
  - Output: Structured Markdown report.

- **core/export.py**: Handles exports.
  - Word: Use python-docx to generate .docx from Markdown.
  - Google Docs: Use Google API to create and insert content (requires OAuth setup).

- **core/utils.py**: Shared utilities.
  - NLP helpers: Tokenization, embedding generation.
  - SEO checks: Keyword density, heading optimization.
  - Edge case handlers: Merging sections, natural flow validation.

### 3. Data Flow
1. User selects mode and uploads files.
2. Inputs validated and parsed in `inputs.py`.
3. Route to appropriate optimizer (`outline_optimizer.py` or `draft_optimizer.py`).
4. Processing: ML models loaded on-demand (e.g., 'all-MiniLM-L6-v2' for embeddings).
5. Output generated and displayed.
6. User exports if desired.

### 4. ML Pipeline
- **Embeddings**: Sentence Transformers for similarity.
- **Intent Detection**: Hugging Face pipeline for zero-shot classification (labels: informational, navigational, etc.).
- **Text Generation**: T5 or GPT-like for rephrasing insertions.
- **Caching**: Use Streamlit's session state for model reuse.

### 5. Deployment
- Run locally: `streamlit run app.py`.
- Cloud: Streamlit Cloud or Heroku; handle secrets for Google API.

### 6. Dependencies
See [requirements.txt](requirements.txt).

This architecture ensures modularity, scalability, and ease of maintenance.
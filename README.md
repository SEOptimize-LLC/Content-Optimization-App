# Blog Optimizer App

A Streamlit-based web application for optimizing blog post outlines and drafts using advanced NLP and ML techniques. It supports two modes: Outline Optimization (enhances structure based on Query Fan-Out reports) and Draft Optimization (suggests natural keyword insertions).

## Repository Structure
The project is organized as follows for modularity and maintainability:

```
blog_optimizer/
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation and setup instructions
├── ARCHITECTURE.md                  # High-level architecture overview
├── INPUT_FORMATS.md                 # Detailed input file format specifications
├── core/                            # Core backend modules
│   ├── __init__.py                  # (Auto-generated or empty)
│   ├── outline_optimizer.py         # Outline optimization logic (parsing, intent inference, structure enhancement)
│   ├── draft_optimizer.py           # Draft optimization logic (keyword ranking, insertion generation)
│   └── export.py                    # Export utilities (Word and Google Docs)
└── tests/                           # Unit and integration tests
    └── test_app.py                  # Basic tests for optimizers
```

- **Root Files**: Entry point, dependencies, and docs.
- **core/**: Separates business logic from UI; easy to test and extend.
- **tests/**: For validation; expand with more comprehensive tests (e.g., pytest fixtures for ML models).

To initialize `__init__.py` files if missing:
```
touch blog_optimizer/core/__init__.py
touch blog_optimizer/tests/__init__.py
```

## Features
- **Outline Mode**: Analyzes Query Fan-Out reports and original outlines to infer search intent, prioritize/merge sections (5-10 H2s), add talking points/links, and optimize for SEO.
- **Draft Mode**: Ranks keywords by relevance to the draft, generates 3 natural insertion options per top keyword with placement hints.
- **UI**: Intuitive Streamlit interface with mode toggle, file uploads, progress bars, and Markdown output display.
- **Exports**: Download as Word (.docx); Google Docs integration (requires API setup).
- **Tech Stack**: Python, Streamlit, spaCy, Hugging Face Transformers, Sentence Transformers, NLTK, python-docx, Google API Client.

## Setup
1. **Clone/Navigate to Project**:
   ```
   cd blog_optimizer
   ```

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Install spaCy Model**:
   ```
   python -m spacy download en_core_web_sm
   ```

4. **Google Docs Export (Optional)**:
   - Enable Google Docs API in [Google Cloud Console](https://console.cloud.google.com/).
   - Download `credentials.json` and place in project root.
   - Run the app once to authorize (opens browser for OAuth).

## Usage
1. **Run the App**:
   ```
   streamlit run app.py
   ```
   Opens at `http://localhost:8501`.

2. **Outline Optimization**:
   - Select "Outline Optimization".
   - Upload Query Fan-Out Report (.md/.txt) and Original Outline (.md).
   - Click "Optimize Outline".
   - View enhanced outline; export as needed.

3. **Draft Optimization**:
   - Select "Draft Optimization".
   - Upload Original Draft (.txt/.md) and Keyword List (.csv/.txt/.md).
   - Click "Optimize Draft".
   - View keyword report with insertion options; export.

### Input Examples
See [INPUT_FORMATS.md](INPUT_FORMATS.md) for details.

**Sample Outline.md**:
```
# Home Gym Guide
## Benefits
- Convenience
- Cost savings
[Source](https://example.com)
```

**Sample Keywords.csv**:
```
keyword,volume
home gym,10000
workout equipment,5000
```

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for high-level design, modules, and data flow.

## Edge Cases Handled
- **Too Many H2s**: Merges low-relevance sections into high ones using semantic similarity.
- **Keyword Already Present**: Skips with enhancement suggestion.
- **Natural Flow**: Uses T5 paraphraser for insertions; limits points to 10 per section.
- **Short Inputs**: Warns if draft <500 words; requires min sub-queries.
- **Links/Fact-Checking**: Adds placeholder reputable links; encourages manual verification.

## Testing
- **Unit Tests**: Run with pytest (not included; add for ML functions like `optimize_outline`).
- **End-to-End**: Test with sample inputs; verify outputs are readable (no disruptions).
- **Validation**: Embeddings/similarities ensure relevance; manual review for flow.

Example Test Command (add tests/ dir):
```
pytest tests/
```

## Deployment
- **Streamlit Cloud**: Connect GitHub repo; add `requirements.txt`.
- **Heroku**: Use `Procfile`: `web: streamlit run app.py --server.port $PORT`.
- **Secrets**: For Google API, use environment variables or Streamlit secrets.toml.

## Limitations & Improvements
- ML Models: Uses lightweight models (e.g., T5-small); upgrade to GPT for better paraphrasing.
- Google Export: Basic text insertion; enhance with full Markdown parsing.
- Performance: Cache models in production; handle large files.
- Suggestions: Integrate real-time SEO tools (e.g., Ahrefs API); add user auth for multi-user.

## License
MIT License.
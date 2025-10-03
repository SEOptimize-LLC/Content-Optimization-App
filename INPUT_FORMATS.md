# Input Formats for Blog Optimizer

This document defines the expected structures for user inputs to ensure proper parsing and processing in the app. All inputs are uploaded via Streamlit file uploaders and parsed using libraries like `markdown`, `pandas`, and `spacy`.

## 1. Query Fan-Out Report (Outline Mode Only)
- **Format**: Markdown (.md) or Plain Text (.txt).
- **Expected Structure**:
  - Header: Title of the report (e.g., "# Query Fan-Out Analysis for [Topic]").
  - Sub-Queries Section: List of exploded sub-queries (e.g., "## Sub-Queries\n- Sub-query 1: ...\n- Sub-query 2: ...").
  - Insights/Suggestions: Bullet points or numbered lists with recommendations (e.g., "## Insights\n- Suggestion 1: Cover aspect X for better coverage.\n- Link to source: [URL]").
  - Search Intent: Optional section inferring user intent (e.g., "## Inferred Intent: Informational").
- **Parsing**: Use `markdown` to convert to HTML, then extract sections with regex or `beautifulsoup4`. Sub-queries and insights stored as lists of strings.
- **Validation**: Must contain at least 3 sub-queries; warn if missing insights.
- **Example**:
  ```
  # Query Fan-Out for Home Gym Equipment
  ## Sub-Queries
  - Best home gym machines for beginners
  - Benefits of home workouts vs gym
  - Budget home gym setup ideas

  ## Insights
  - Ensure coverage of cost comparisons.
  - Add links to reputable sites like Mayo Clinic.
  ```

## 2. Original Outline (Outline Mode Only)
- **Format**: Markdown (.md).
- **Expected Structure**:
  - H1: Main title (e.g., "# Ultimate Guide to Home Gym Equipment").
  - H2 Subheadings: 5-10 main sections (e.g., "## Section 1: Benefits").
  - H3 Subheadings: Under H2s as needed (e.g., "### Subtopic").
  - Talking Points: Bullet lists under headings (e.g., "- Point 1\n- Point 2").
  - Links: Inline Markdown links (e.g., "[Source](https://example.com)").
- **Parsing**: Use `markdown-it-py` or regex to extract hierarchy (H1, H2, H3), bullets, and links. Represent as a tree structure (dict with keys: 'h1', 'h2s' list of dicts with 'title', 'h3s', 'points', 'links')).
- **Validation**: At least 1 H1, 3+ H2s; each H2 has 5-10 points.
- **Example**:
  ```
  # Ultimate Guide to Home Gym Equipment
  ## Benefits of Home Workouts
  - Convenience of anytime access
  - Cost savings over gym memberships
  - [Source: Mayo Clinic](https://mayoclinic.org)
  ### Types of Benefits
  - Physical health improvements
  ```

## 3. Original Draft (Draft Mode Only)
- **Format**: Plain Text (.txt), Markdown (.md), or Word (.docx).
- **Expected Structure**:
  - Free-form paragraphs of written content.
  - Optional headings (##) for sections.
  - No strict structure; full article draft.
- **Parsing**: For .txt/.md: Read as string, split into paragraphs. For .docx: Use `python-docx` to extract text. Tokenize with spaCy for sentences/paragraphs.
- **Validation**: Minimum 500 words; warn if too short.
- **Example** (Markdown):
  ```
  Home gyms are popular for their convenience. Many people prefer working out at home rather than going to a gym.
  ```

## 4. Expanded Keyword List (Draft Mode Only)
- **Format**: CSV (.csv), Markdown (.md list), or Plain Text (.txt list).
- **Expected Structure**:
  - CSV: Columns - "keyword" (required), optional: "search_volume", "competition", "relevance_score".
  - Markdown/Text: Bullet list (e.g., "- keyword1\n- keyword2") or comma-separated.
- **Parsing**: Pandas for CSV (load to DataFrame, extract 'keyword' column). For lists: Split lines or commas into list of strings.
- **Validation**: At least 10 keywords; deduplicate.
- **Example CSV**:
  ```
  keyword,search_volume
  home gym equipment,10000
  best home workout machines,5000
  ```
- **Example Markdown**:
  ```
  - home gym equipment
  - best home workout machines
  ```

## General Notes
- All files must be UTF-8 encoded.
- Errors in parsing trigger user-friendly messages in Streamlit (e.g., "Invalid format: Expected Markdown for outline").
- Inputs stored in Streamlit session_state for processing.
- Future: Support PDF via `PyPDF2` for reports/drafts.
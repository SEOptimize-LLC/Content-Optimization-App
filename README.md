# Semantic SEO Content Optimizer V2

**Complete implementation of Koray Tuğberk GÜBÜR's Semantic SEO Framework**

Transform Query Fan-Out reports into complete semantic SEO strategies with automated topical mapping, content briefs, and distributional semantics optimization.

---

## 🎯 What This Does

This app takes a **Query Fan-Out report** and automatically generates:

✅ **Entity & Attribute Detection** - Auto-identifies central entities and source context
✅ **Topical Maps** - Complete Entity-Attribute-Value structures with core/author sections
✅ **Content Briefs** - With 4 contextual elements (Vector, Hierarchy, Structure, Connections)
✅ **Semantic Content Networks** - Internal linking strategy with PageRank analysis
✅ **Distributional Semantics** - Keyword co-occurrence and "contextual dance" optimization
✅ **Article Methodology** - Definitions, Q&A pairs, modality markers, inquisitive semantics
✅ **URL Structure** - Information tree planning
✅ **Meta Optimization** - Title tags, meta descriptions aligned with macro/micro context

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Upload & Optimize

1. **Upload** Query Fan-Out Report → Auto-detects entities
2. **Confirm** Central Entity & Source Context (5 suggestions shown)
3. **Select** Outline or Draft optimization mode
4. **Generate** Complete semantic SEO strategy
5. **Export** as Markdown or Word

---

## 📊 Framework Overview

### **Koray's Semantic SEO Framework - 10 Core Components**

#### **Foundation Layer**
1. **Central Entity & Source Context** - WHO you are and WHAT you're about
2. **Topical Map** - Entity-Attribute pairs forming Core (monetization) + Author (authority) sections
3. **Query Processing** - Functional/concrete words, question types, intent classification

#### **Content Planning Layer**
4. **Content Brief** - The CORE with 4 contextual elements:
   - **Contextual Vector**: Heading order (search demand + semantic closeness)
   - **Contextual Hierarchy**: H1/H2/H3 structure by importance
   - **Contextual Structure**: Format specs (list/table/paragraph) by question type
   - **Contextual Connections**: Internal linking strategy

5. **Macro vs. Micro Context** - ONE main focus (80%) + related supplementary (20%)

#### **Content Creation Layer**
6. **Article Methodology** - Authorship rules:
   - Start with definitions
   - Extractive + abstractive summaries
   - Modality markers (fact/research/suggestion)
   - Research citations in-context
   - Inquisitive semantics (answer → question flow)

#### **Semantic Optimization Layer**
7. **Distributional Semantics** - Strategic keyword co-occurrence:
   - Page-wide contextual consistency
   - Section-specific "contextual dance"
   - Word sequence modeling
   - Anchor segments for discourse flow

8. **Question Generation** - From keywords → structured questions
   - Boolean, definitional, grouping, comparative
   - Question format as headings
   - Answer format matches question format

#### **Network Layer**
9. **Semantic Content Network** - Internal linking:
   - Root document (reflects macro context)
   - Strategic anchor text placement
   - Contextual relevance + user clickability

10. **URL Structure** - Information tree hierarchy
    - `/central-entity/attribute/sub-attribute`
    - Clear, descriptive, keyword-rich

---

## 📁 Project Structure

```
Content-Optimization-App/
├── app.py                              # Main Streamlit app (4-step workflow) ⭐
├── requirements.txt                    # Python dependencies
├── README.md                           # Complete documentation
├── ARCHITECTURE.md                     # Architecture overview
├── INPUT_FORMATS.md                    # Input specifications
├── Semantic SEO_ Definitive Guide (1).md  # Koray's framework reference
├── Incorporating semantics into keyword research.xlsx  # Framework glossary
├── core/                               # Backend modules
│   ├── entity_context_extractor.py    # Auto-detect entities & context
│   ├── topical_map_builder.py         # Generate topical maps
│   ├── query_processor.py             # Advanced query analysis
│   ├── content_brief_generator.py     # 4 contextual elements ⭐
│   ├── distributional_semantics.py    # Co-occurrence & word sequences
│   ├── content_structure_generator.py # Article methodology
│   ├── network_builder.py             # Semantic content network
│   ├── url_structure_generator.py     # URL planning
│   ├── meta_optimizer.py              # Title & meta optimization
│   ├── outline_optimizer.py           # Complete outline pipeline
│   ├── draft_optimizer.py             # Complete draft pipeline
│   └── google_api_config.py           # Google Cloud API integration
└── tests/                              # Unit tests
    └── test_app.py
```

---

## 🔧 Feature Details

### **Outline Optimization Mode**

**Input:** Query Fan-Out Report + Original Outline

**Output:**
- Complete topical map (Markdown)
- Content briefs for core attributes (top 3)
- Semantic content network with internal linking strategy
- URL structure plan
- Meta tags (title + description) for each page

**What You Get:**
1. **Topical Map** with:
   - Root document
   - Core section (monetization focus)
   - Author section (broader coverage)

2. **Content Briefs** with:
   - Contextual Vector (ordered headings)
   - Contextual Hierarchy (H1/H2/H3 by importance)
   - Contextual Structure (format: list/table/paragraph)
   - Contextual Connections (internal links with anchor text)
   - Article Methodology (authorship rules)

3. **Semantic Network**:
   - PageRank scores
   - Hub nodes
   - Linking strategy (8 links max per page)

4. **URL Structure**:
   - Information tree hierarchy
   - SEO-optimized slugs
   - Image URL strategy

5. **Meta Optimization**:
   - 3 title variations (ranked by SEO score)
   - 3 meta description variations
   - Open Graph tags
   - Schema.org markup

### **Draft Optimization Mode**

**Input:** Draft Text + Keyword List

**Output:**
- Keyword relevance rankings
- Keyword insertion recommendations (3 options per keyword)
- Co-occurrence analysis
- Word sequence recommendations
- Contextual dance plan (section-by-section)
- Anchor segment suggestions

**What You Get:**
1. **Keyword Analysis**:
   - Top 15 keywords by relevance
   - Already present vs. missing
   - Frequency counts

2. **Insertion Recommendations**:
   - Best section for each keyword
   - 3 insertion options (beginning/middle/end)
   - Natural phrasing examples

3. **Distributional Semantics**:
   - Co-occurrence matrix
   - Missing keyword pairs to add together
   - Section-by-section keyword density

4. **Word Sequences**:
   - N-gram analysis (bigrams, trigrams)
   - Preceding/following word patterns
   - Natural phrase suggestions

5. **Contextual Dance**:
   - Macro keywords (should appear in ALL sections)
   - Section-specific micro keywords
   - Coverage % tracking

6. **Anchor Segments**:
   - Sentence flow improvements
   - Connecting words/phrases
   - Discourse integration

---

## 🔌 Google Cloud API Integration (Optional)

### **Setup Instructions**

#### **1. Google Cloud Natural Language API**

**Purpose:** Enhanced entity extraction (more accurate than spaCy)

**Setup:**
1. Enable API in [Google Cloud Console](https://console.cloud.google.com/)
2. Create Service Account → Download JSON credentials
3. Save as `service-account.json` in project root

**Cost:** FREE tier = 5,000 units/month, then $1-2 per 1,000

**Usage:**
```python
from core.google_api_config import setup_google_apis

manager = setup_google_apis(
    language_credentials='path/to/service-account.json'
)

entities = manager.extract_entities_from_text("Your query text here")
```

#### **2. Google Search Console API**

**Purpose:** Import actual ranking queries from your website

**Setup:**
1. Enable API in Google Cloud Console
2. Download OAuth `client_secret.json`
3. First run triggers browser authentication flow

**Cost:** FREE (unlimited)

**Usage:**
```python
manager.setup_search_console()
queries = manager.get_search_console_queries(
    site_url='https://www.example.com/',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

#### **3. Knowledge Graph Search API**

**Purpose:** Map entities to Google's Knowledge Graph

**Setup:**
1. Enable API in Google Cloud Console
2. Get API key from Credentials page
3. Add to `api_config.json`

**Cost:** FREE tier = 100,000 calls/day

**Usage:**
```python
manager = setup_google_apis(kg_api_key='YOUR_API_KEY')
kg_entities = manager.search_knowledge_graph('glasses')
```

### **Configuration File**

Create `api_config.json`:
```json
{
  "knowledge_graph_api_key": "YOUR_API_KEY_HERE",
  "natural_language_credentials_path": "service-account.json",
  "search_console_token_path": "token.pickle"
}
```

---

## 💡 Usage Examples

### **Example 1: Optimize Blog Outline**

```python
# In the app workflow:

# Step 1: Upload query-fanout-glasses.md
# Step 2: Confirm entity = "glasses", context = "luxury eyewear brand"
# Step 3: Upload original-outline.md
# Step 4: Get complete topical map + content briefs + network + URLs + meta
```

**Result:**
- Topical map with 15 attributes (core: "types", "frames", "lenses"; author: "care", "history")
- Content brief for "Types of Glasses for Round Faces"
- Internal linking: Root → 8 core pages → 12 author pages
- URL: `/glasses/types-of-frames-for-round-faces`
- Title: "Types of Glasses for Round Faces | Luxury Eyewear Guide"

### **Example 2: Optimize Draft Article**

```python
# Step 1: Upload query-fanout.md
# Step 2: Confirm entity + context
# Step 3: Upload draft.txt + keywords.csv
# Step 4: Get keyword insertion plan + co-occurrence analysis
```

**Result:**
- Top 15 keywords ranked by relevance
- "blue light glasses" → Add in Section 3, beginning position
- Missing co-occurrence: "blue light" + "eye strain" (add together)
- Contextual dance: "glasses" should appear in 90% of sections (currently 60%)
- 5 anchor segment suggestions for better flow

---

## 🎓 Semantic SEO Concepts Explained

### **What is a Topical Map?**

A topical map is NOT a concept map (copying SERPs). It's an **Entity-Attribute-Value structure**:

- **Central Entity**: "Germany"
- **Attributes**: "visa", "population", "climate", "culture"
- **Values**: Specific details about each attribute

**Core vs. Author Sections:**
- **Core**: Directly tied to monetization (e.g., visa services)
- **Author**: Broader coverage for topical authority (e.g., culture, history)

### **What are the 4 Contextual Elements?**

1. **Contextual Vector**: The ORDER of headings (search demand + semantic closeness)
2. **Contextual Hierarchy**: The WEIGHT (H1 macro, H2 high-priority, H3 sub-topics)
3. **Contextual Structure**: The FORMAT (list for grouping, table for comparison, paragraph for definition)
4. **Contextual Connections**: The LINKS (internal linking strategy with anchor text)

### **What is Distributional Semantics?**

"Words are known by the company they keep" - meaning is derived from co-occurring words.

**Key concepts:**
- **Co-occurrence**: Keywords appearing together in a window (e.g., "water" + "hydration" within 10 words)
- **Contextual Dance**: Strategic keyword placement by section
- **Word Sequences**: Common n-grams (e.g., "benefits of X", "how to Y")
- **Anchor Segments**: Repeated words between sentences for flow

### **What is Macro vs. Micro Context?**

Every page has:
- **Macro Context** (80%): ONE main focus (e.g., "Types of Glasses")
- **Micro Context** (20%): Related supplementary topics (e.g., "Care Tips")

**Title tag** = Macro Context
**Meta description** = Macro + hints of Micro

---

## 🔬 Technical Details

### **NLP Models Used**

All run **locally** (no API costs):

- **spaCy** (`en_core_web_sm`): Entity recognition, dependency parsing, NER
- **Sentence Transformers** (`all-MiniLM-L6-v2`): Semantic similarity, embeddings
- **T5-small**: Paraphrasing, definition generation
- **NLTK**: Stopwords, n-grams, tokenization

### **Memory Usage**

Approx. **800MB RAM** for all models:
- spaCy: 13MB
- Sentence Transformers: 80MB
- T5-small: 242MB
- Other libraries: ~400MB

**Streamlit Cloud FREE tier**: 1GB RAM ✓ (fits!)
**Streamlit Cloud Team**: 4GB RAM (if you need larger models)

### **Performance**

Processing a Query Fan-Out report with 50 queries:
- Entity extraction: ~2 seconds
- Topical map generation: ~5 seconds
- Content brief (3 attributes): ~15 seconds
- Semantic network: ~3 seconds
- **Total**: ~25 seconds

---

## 📚 Resources

### **Learn More About Semantic SEO**

- Koray Tuğberk GÜBÜR's [Holistic SEO](https://www.holisticseo.digital/)
- [Topical Authority Guide](https://www.holisticseo.digital/topical-authority/)
- [Semantic SEO Course](https://www.holisticseo.digital/semantic-seo/)

### **Framework Documentation**

See `INPUT_FORMATS.md` for input file specifications
See `ARCHITECTURE.md` for system design

### **API Documentation**

- [Google Cloud Natural Language API](https://cloud.google.com/natural-language/docs)
- [Google Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original)
- [Knowledge Graph Search API](https://developers.google.com/knowledge-graph)

---

## 🐛 Troubleshooting

### **spaCy Model Not Found**

```bash
python -m spacy download en_core_web_sm
```

### **Streamlit Cloud Deployment Hanging**

- Set Python version to **3.10-3.12** in app settings
- If torch fails: downgrade to `torch==2.0.1`
- If spaCy fails: downgrade to `spacy==3.6.1`

### **Google API Errors**

**403 Forbidden:**
- Check API is enabled in Cloud Console
- Verify credentials file path
- Check quotas/billing

**Import Errors:**
```bash
pip install google-cloud-language
pip install google-api-python-client
```

---

## 🚧 Roadmap

### **Completed ✅**
- ✅ Entity & context extraction
- ✅ Topical map generation
- ✅ Query processing (functional/concrete words, question types)
- ✅ Content brief generator (4 contextual elements)
- ✅ Distributional semantics
- ✅ Article methodology
- ✅ Semantic content network
- ✅ URL structure generation
- ✅ Meta optimization
- ✅ Google Cloud API integration setup

### **Coming Soon 🔜**
- 🔜 GSC integration in app UI
- 🔜 Knowledge Graph entity mapping in workflow
- 🔜 Publication frequency tracker
- 🔜 Multi-language support
- 🔜 Visual topical map (graph visualization)
- 🔜 Batch processing (multiple pages)
- 🔜 API endpoints for programmatic access

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

Built with [Claude Code](https://claude.com/claude-code)

**Want to contribute?**
- Report bugs via GitHub Issues
- Submit feature requests
- Create pull requests

---

## 📞 Support

For questions about:
- **Semantic SEO Framework**: Visit [Holistic SEO](https://www.holisticseo.digital/)
- **This Implementation**: Create a GitHub Issue
- **Deployment**: Check Streamlit [docs](https://docs.streamlit.io/)

---

**⭐ Star this repo if you find it helpful!**

Built with 🤖 by Claude Code
Framework by Koray Tuğberk GÜBÜR

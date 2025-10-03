import re
import traceback

# Diagnostic logging for spaCy import
print("Attempting spaCy import in draft_optimizer...")
try:
    import spacy
    print("SUCCESS: Imported spacy (draft).")
except ImportError as e:
    print(f"IMPORT ERROR in spacy (draft): {e}")
    traceback.print_exc()
except Exception as e:
    print(f"GENERAL ERROR in spacy (draft): {e}")
    traceback.print_exc()

try:
    from transformers import pipeline
    print("SUCCESS: Imported transformers.pipeline (draft).")
except Exception as e:
    print(f"ERROR in transformers (draft): {e}")
    traceback.print_exc()

try:
    from sentence_transformers import SentenceTransformer, util
    print("SUCCESS: Imported sentence_transformers (draft).")
except Exception as e:
    print(f"ERROR in sentence_transformers (draft): {e}")
    traceback.print_exc()

import nltk
from nltk.corpus import stopwords
import pandas as pd
from collections import Counter
import markdown
from bs4 import BeautifulSoup

print("Core imports for draft_optimizer completed.")

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None

# Load ML models
embedder = SentenceTransformer('all-MiniLM-L6-v2')
paraphraser = pipeline("text2text-generation", model="t5-small")

STOP_WORDS = set(stopwords.words('english'))

def parse_draft(draft_text):
    """Parse draft into paragraphs."""
    # Split by double newlines for paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', draft_text) if p.strip()]
    return paragraphs

def parse_keywords(keyword_input):
    """Parse keywords from CSV, MD, or text."""
    keywords = []
    if isinstance(keyword_input, str):
        if keyword_input.endswith('.csv'):
            df = pd.read_csv(keyword_input)
            keywords = df['keyword'].tolist() if 'keyword' in df.columns else df.iloc[:, 0].tolist()
        else:
            # Assume bullet list or comma-separated
            lines = keyword_input.split('\n')
            for line in lines:
                line = line.strip('- ').strip()
                if line:
                    keywords.extend([kw.strip() for kw in line.split(',')])
    else:
        # Assume list or DataFrame
        keywords = keyword_input if isinstance(keyword_input, list) else keyword_input['keyword'].tolist()
    
    # Deduplicate
    return list(set(keywords))

def get_draft_topic_embedding(paragraphs):
    """Get embedding for the overall draft topic."""
    # Combine all paragraphs
    full_text = ' '.join(paragraphs)
    doc = nlp(full_text)
    # Use sentences as representatives
    sentences = [sent.text for sent in doc.sents]
    if sentences:
        topic_emb = embedder.encode(' '.join(sentences[:10]))  # Top 10 sentences
    else:
        topic_emb = embedder.encode(full_text)
    return topic_emb

def rank_keywords(keywords, topic_emb, threshold=0.3):
    """Rank keywords by cosine similarity to draft topic."""
    kw_embeds = embedder.encode(keywords)
    similarities = util.cos_sim(topic_emb, kw_embeds)[0]
    
    ranked = [(kw, sim.item()) for kw, sim in zip(keywords, similarities) if sim.item() > threshold]
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    # Select top 10+ (all above threshold, min 10 if possible)
    top_keywords = [kw for kw, _ in ranked[:15]]  # Up to 15 for more options
    return top_keywords, ranked

def check_keyword_presence(paragraphs, keyword):
    """Check if keyword is already present."""
    keyword_lower = keyword.lower()
    for para in paragraphs:
        if keyword_lower in para.lower():
            return True, para
    return False, None

def generate_insertion_options(paragraphs, keyword, topic_emb):
    """Generate 3 natural insertion options for the keyword."""
    options = []
    
    # Find most relevant paragraphs
    para_embeds = embedder.encode(paragraphs)
    sims = util.cos_sim(topic_emb, para_embeds)[0]
    top_para_idx = sims.argmax().item()
    candidate_para = paragraphs[top_para_idx]
    
    present, existing_para = check_keyword_presence(paragraphs, keyword)
    if present:
        # Suggest enhancement instead
        options.append({
            'hint': ' '.join(candidate_para.split()[:10]),  # First 10 words
            'snippet': f"Enhance existing: {existing_para[:100]}... (already includes '{keyword}')"
        })
        return options  # Only one option for enhancement
    
    # Generate 3 rephrased versions with keyword inserted naturally
    for i in range(3):
        # Use T5 to paraphrase with keyword prompt
        prompt = f"paraphrase: Insert '{keyword}' naturally: {candidate_para}"
        result = paraphraser(prompt, max_length=150, num_return_sequences=1)[0]['generated_text']
        
        hint_words = ' '.join(candidate_para.split()[:10])
        options.append({
            'hint': hint_words,
            'snippet': result
        })
    
    return options

def generate_keyword_report(top_keywords, paragraphs, topic_emb):
    """Generate structured Markdown report for keywords."""
    report = "# Keyword Insertion Report\n\n"
    
    for keyword in top_keywords:
        options = generate_insertion_options(paragraphs, keyword, topic_emb)
        report += f"## Keyword: {keyword}\n\n"
        
        if not options:  # Skip if no options (e.g., already present and no enhancement needed)
            report += "### Skipped: Keyword already sufficiently present\n\n"
            continue
        
        for idx, opt in enumerate(options[:3], 1):
            report += f"### Option #{idx}\n"
            report += f"#### Placement Hint: {opt['hint']}\n\n"
            report += f"#### New Content Snippet: {opt['snippet']}\n\n"
        
        report += "\n---\n\n"
    
    return report

def optimize_draft(draft_text, keyword_input):
    """
    Main function to optimize draft.
    
    Args:
        draft_text (str): Raw text of original draft.
        keyword_input (str or list or pd.DataFrame): Keywords from file or list.
    
    Returns:
        str: Structured report in Markdown.
        dict: Metadata like top_keywords, num_options.
    """
    if nlp is None:
        raise ValueError("spaCy model not loaded.")
    
    paragraphs = parse_draft(draft_text)
    keywords = parse_keywords(keyword_input)
    topic_emb = get_draft_topic_embedding(paragraphs)
    top_keywords, ranked = rank_keywords(keywords, topic_emb)
    
    report_md = generate_keyword_report(top_keywords, paragraphs, topic_emb)
    
    return report_md, {
        'top_keywords': top_keywords,
        'rankings': ranked,
        'num_paragraphs': len(paragraphs)
    }
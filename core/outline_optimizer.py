import re
import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
import markdown
from bs4 import BeautifulSoup

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Load spaCy model (en_core_web_sm for efficiency)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None

# Load ML models
intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

STOP_WORDS = set(stopwords.words('english'))

def parse_query_report(report_text):
    """Parse Query Fan-Out report into sub-queries and insights."""
    soup = BeautifulSoup(markdown.markdown(report_text), 'html.parser')
    sub_queries = []
    insights = []
    current_section = None
    
    for element in soup.find_all(['h2', 'ul', 'li', 'p']):
        if element.name == 'h2':
            current_section = element.get_text().strip().lower()
        elif element.name == 'li' or element.name == 'p':
            text = element.get_text().strip()
            if current_section and 'sub-quer' in current_section:
                sub_queries.append(text)
            elif current_section and 'insight' in current_section:
                insights.append(text)
    
    return sub_queries, insights

def parse_outline(outline_md):
    """Parse original outline into hierarchical structure."""
    soup = BeautifulSoup(markdown.markdown(outline_md), 'html.parser')
    structure = {'h1': '', 'h2s': []}
    
    current_h2 = None
    for element in soup.find_all(['h1', 'h2', 'h3', 'ul', 'li', 'a']):
        if element.name == 'h1':
            structure['h1'] = element.get_text().strip()
        elif element.name == 'h2':
            if current_h2:
                structure['h2s'].append(current_h2)
            current_h2 = {'title': element.get_text().strip(), 'h3s': [], 'points': [], 'links': []}
        elif element.name == 'h3' and current_h2:
            current_h2['h3s'].append(element.get_text().strip())
        elif element.name == 'li' and current_h2:
            current_h2['points'].append(element.get_text().strip())
        elif element.name == 'a' and current_h2:
            link_text = element.get_text().strip()
            link_url = element.get('href', '')
            if link_url:
                current_h2['links'].append(f"[{link_text}]({link_url})")
    
    if current_h2:
        structure['h2s'].append(current_h2)
    
    return structure

def build_contextual_knowledge(sub_queries, outline_structure):
    """Build combined context from sub-queries and outline."""
    context = []
    # Add sub-queries
    context.extend(sub_queries)
    # Add outline titles and points
    for h2 in outline_structure['h2s']:
        context.append(h2['title'])
        context.extend(h2['points'])
        context.extend(h2['h3s'])
    return ' '.join(context)

def infer_search_intent(context):
    """Infer search intent using zero-shot classification."""
    candidate_labels = ["informational", "navigational", "transactional", "commercial investigation"]
    result = intent_classifier(context[:512], candidate_labels)  # Truncate for model limit
    intent = result['labels'][0]
    return intent, result['scores'][0]

def extract_keywords(context):
    """Extract key terms using NLTK for SEO."""
    tokens = nltk.word_tokenize(context.lower())
    words = [w for w in tokens if w.isalpha() and w not in STOP_WORDS]
    # Simple frequency for now; can enhance with TF-IDF
    freq = nltk.FreqDist(words)
    return [word for word, _ in freq.most_common(20)]

def prioritize_h2s(h2s, sub_queries, keywords, max_h2s=10):
    """Prioritize and merge H2s based on similarity to sub-queries and keywords."""
    # Embed H2 titles
    h2_titles = [h2['title'] for h2 in h2s]
    h2_embeddings = embedder.encode(h2_titles)
    
    # Embed sub-queries and keywords
    query_embeds = embedder.encode(sub_queries + keywords)
    
    # Compute similarities
    similarities = []
    for i, emb in enumerate(h2_embeddings):
        sims = util.cos_sim(emb, query_embeds).max().item()
        similarities.append((h2s[i], sims))
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Select top max_h2s or merge if more
    selected = [s[0] for s in similarities[:max_h2s]]
    
    if len(h2s) > max_h2s:
        # Merge lowest similarity ones into closest high ones
        merged = []
        for low_h2 in similarities[max_h2s:]:
            # Find closest high H2
            closest_idx = max(range(len(selected)), key=lambda i: util.cos_sim(embedder.encode(selected[i]['title']), embedder.encode(low_h2[0]['title'])).item())
            # Merge points and links
            selected[closest_idx]['points'].extend(low_h2[0]['points'])
            selected[closest_idx]['links'].extend(low_h2[0]['links'])
            selected[closest_idx]['title'] += f" & {low_h2[0]['title']}"  # Simple merge title
    
    return selected

def enhance_section(h2, insights, keywords, intent):
    """Enhance a single H2 section with insights, keywords, and new points/links."""
    enhanced = h2.copy()
    
    # Optimize title for SEO: Insert relevant keyword if natural
    if keywords:
        top_kw = keywords[0]
        if top_kw.lower() not in enhanced['title'].lower():
            # Simple insertion: prepend if fits
            enhanced['title'] = f"{top_kw.capitalize()} {enhanced['title']}"
    
    # Add insights as new points
    new_points = [insight for insight in insights if any(term in insight.lower() for term in [intent, 'seo', 'coverage'])]
    enhanced['points'].extend(new_points)
    
    # Add H3s based on sub-queries (simplified)
    if len(enhanced['points']) > 10:
        # Group points into H3s
        doc = nlp(' '.join(enhanced['points']))
        # Placeholder: Add generic H3s
        enhanced['h3s'].extend(['Additional Subtopic 1', 'Additional Subtopic 2'])
    
    # Add placeholder links for fact-checking (in real app, search or suggest)
    enhanced['links'].append("[Fact-check Source](https://example.com/reputable-source)")
    
    # Ensure 5-10 points per H2
    enhanced['points'] = enhanced['points'][:10]
    
    return enhanced

def generate_enhanced_outline(structure, sub_queries, insights, keywords, intent):
    """Generate the full enhanced outline."""
    prioritized_h2s = prioritize_h2s(structure['h2s'], sub_queries, keywords)
    
    enhanced_h2s = []
    for h2 in prioritized_h2s:
        enhanced = enhance_section(h2, insights, keywords, intent)
        enhanced_h2s.append(enhanced)
    
    # Build Markdown
    md = f"# {structure['h1']}\n\n"
    for h2 in enhanced_h2s:
        md += f"## {h2['title']}\n\n"
        for h3 in h2['h3s']:
            md += f"### {h3}\n\n"
        for point in h2['points']:
            md += f"- {point}\n"
        for link in h2['links']:
            md += f"{link}\n\n"
    
    return md

def optimize_outline(query_report_text, original_outline_md):
    """
    Main function to optimize outline.
    
    Args:
        query_report_text (str): Raw text of Query Fan-Out report.
        original_outline_md (str): Raw Markdown of original outline.
    
    Returns:
        str: Enhanced outline in Markdown.
    """
    if nlp is None:
        raise ValueError("spaCy model not loaded.")
    
    sub_queries, insights = parse_query_report(query_report_text)
    structure = parse_outline(original_outline_md)
    context = build_contextual_knowledge(sub_queries, structure)
    intent, confidence = infer_search_intent(context)
    keywords = extract_keywords(context)
    
    enhanced_md = generate_enhanced_outline(structure, sub_queries, insights, keywords, intent)
    
    return enhanced_md, {
        'intent': intent,
        'confidence': confidence,
        'keywords': keywords,
        'num_h2s': len(structure['h2s'])
    }
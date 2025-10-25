"""
Semantic Entity & Attribute Extractor V2
Properly implements Koray's Semantic SEO framework with:
- Intent-based analysis
- Aspect extraction (not keyword counting)
- Semantic clustering using embeddings
- Relationship validation (no tautologies)
"""

import spacy
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import DBSCAN

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None

try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except:
    print("Sentence Transformers not available")
    embedder = None


class SemanticExtractorV2:
    """Extract entities and attributes using proper semantic analysis."""

    # Product aspect categories (what users care about when comparing products)
    PRODUCT_ASPECTS = {
        'effectiveness': ['effective', 'work', 'result', 'whitening', 'brighten', 'performance'],
        'ingredients': ['ingredient', 'formula', 'peroxide', 'chemical', 'natural', 'contains'],
        'safety': ['safe', 'sensitivity', 'enamel', 'gentle', 'harm', 'damage', 'side effect'],
        'price': ['price', 'cost', 'expensive', 'cheap', 'budget', 'value', 'affordable'],
        'usage': ['use', 'apply', 'wear', 'time', 'duration', 'frequency', 'easy', 'convenient'],
        'comparison': ['vs', 'versus', 'compare', 'better', 'best', 'top', 'difference'],
        'brands': ['brand', 'crest', 'colgate', 'whitestrips', 'manufacturer'],
        'features': ['dissolving', 'no-rinse', 'fast', 'quick', 'overnight', 'professional'],
        'user_experience': ['taste', 'residue', 'comfortable', 'stay', 'slip', 'texture']
    }

    def __init__(self):
        self.nlp = nlp
        self.embedder = embedder

    def extract_semantic_structure(self, query_text: str) -> Dict:
        """
        Main extraction method using proper semantic analysis.

        Returns proper Entity-Attribute-Value structure.
        """
        if self.nlp is None:
            raise ValueError("spaCy model not loaded")

        # Phase 1: Parse ONLY real queries (strict filtering)
        queries = self._parse_queries_strict(query_text)

        if not queries:
            return {'error': 'No valid queries found', 'queries': []}

        # Phase 2: Detect primary intent
        primary_intent = self._detect_primary_intent(queries)

        # Phase 3: Extract central entity
        central_entity = self._extract_central_entity(queries)

        # Phase 4: Extract aspect-based attributes (NOT keywords!)
        attributes = self._extract_aspects(queries, primary_intent)

        # Phase 5: Cluster related queries semantically
        if self.embedder:
            clustered_queries = self._cluster_queries_semantically(queries)
        else:
            clustered_queries = {}

        # Phase 6: Build Entity-Attribute-Value structure
        eav_structure = self._build_eav_structure(
            central_entity,
            attributes,
            clustered_queries
        )

        return {
            'central_entity': central_entity,
            'primary_intent': primary_intent,
            'attributes': attributes,
            'clustered_queries': clustered_queries,
            'eav_structure': eav_structure,
            'total_valid_queries': len(queries),
            'queries_parsed': queries[:10]  # Sample for debugging
        }

    def _parse_queries_strict(self, query_text: str) -> List[str]:
        """
        STRICT query parsing - only accept actual search queries.

        Filters out:
        - Instructions/descriptions
        - Metadata/headers
        - Full sentences/paragraphs
        - Anything that doesn't look like a real query
        """
        text = re.sub(r'[#*`]', '', query_text)
        lines = text.split('\n')
        queries = []

        # Instruction patterns (strict regex)
        instruction_patterns = [
            r'\bbelow is\b',
            r'\bthis section\b',
            r'\beach section\b',
            r'\boutlines how\b',
            r'\bmethodology\b',
            r'\bcomprehensive analysis\b',
            r'\boptimize and structure\b',
            r'\bvisibility\b.*\bengagement\b',
            r'\bquery fan-out\b',
            r'\btailored for\b',
            r'\busers seeking\b',
            r'\binformational:',
            r'\btransactional:',
            r'\bcommercial:',
        ]

        for line in lines:
            line = line.strip()

            # Length filter: Real queries are 5-75 chars
            if len(line) < 5 or len(line) > 75:
                continue

            # Skip headers/metadata
            if line.endswith(':') or line.startswith(('Category', 'Section', 'Type', 'Note', 'Intent', '###', '##', '#')):
                continue

            # Clean bullets
            cleaned = re.sub(r'^[-•*\d.)\]]+\s*', '', line).strip()
            if not cleaned or len(cleaned) < 5:
                continue

            cleaned_lower = cleaned.lower()

            # Skip instruction text (strict regex matching)
            if any(re.search(pattern, cleaned_lower, re.IGNORECASE) for pattern in instruction_patterns):
                continue

            # Word count filter
            words = cleaned.split()
            word_count = len(words)

            # Skip if >12 words (probably description, not query)
            if word_count > 12:
                continue

            # Skip complete sentences (ends with period + >10 words)
            if cleaned.endswith('.') and word_count > 10:
                continue

            # Must be a real query format:
            # 1. Question (contains ?) OR
            # 2. Short keyword phrase (2-8 words) OR
            # 3. Starts with query words
            is_question = '?' in cleaned
            is_short_phrase = 2 <= word_count <= 8
            query_starters = ['best', 'top', 'how', 'what', 'why', 'when', 'where', 'which',
                            'are', 'is', 'do', 'does', 'can', 'should', 'will']
            starts_with_query_word = any(cleaned_lower.startswith(w + ' ') for w in query_starters)

            # Accept if it matches query patterns
            if is_question or (is_short_phrase and starts_with_query_word) or (word_count <= 5):
                # Final sanity check: not a sentence fragment
                if not cleaned_lower.startswith(('here is', 'this is', 'there are', 'it is')):
                    queries.append(cleaned)

        return list(set(queries))  # Deduplicate

    def _detect_primary_intent(self, queries: List[str]) -> str:
        """
        Detect primary search intent from queries.

        Returns: comparison, review, how-to, informational, transactional
        """
        intent_keywords = {
            'comparison': ['best', 'top', 'vs', 'versus', 'compare', 'better', 'difference'],
            'review': ['review', 'rating', 'opinion', 'recommendation', 'experience'],
            'how-to': ['how to', 'how do', 'steps', 'guide', 'tutorial'],
            'informational': ['what', 'why', 'when', 'where', 'which', 'definition'],
            'transactional': ['buy', 'purchase', 'order', 'shop', 'deal', 'coupon']
        }

        intent_scores = Counter()

        for query in queries:
            query_lower = query.lower()
            for intent, keywords in intent_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    intent_scores[intent] += 1

        if intent_scores:
            return intent_scores.most_common(1)[0][0]
        return 'informational'

    def _extract_central_entity(self, queries: List[str]) -> str:
        """
        Extract central entity using frequency + semantic analysis.

        For "Best Dissolving Whitening Strips":
        - Central Entity: "dissolving whitening strips" (the product category)
        - NOT: "best", "strips", "whitening"
        """
        # Extract noun phrases
        noun_phrases = Counter()

        for query in queries:
            doc = self.nlp(query)
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()

                # Must be 2+ words for products
                if len(chunk_text.split()) >= 2:
                    # Remove leading determiners/adjectives like "best", "top"
                    chunk_text = re.sub(r'^(best|top|good|great|leading)\s+', '', chunk_text)
                    if len(chunk_text.split()) >= 2:
                        noun_phrases[chunk_text] += 1

        if noun_phrases:
            # Return most common multi-word noun phrase
            return noun_phrases.most_common(1)[0][0]

        # Fallback: extract from longest query
        longest = max(queries, key=len, default="")
        doc = self.nlp(longest)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                return chunk.text.lower()

        return "unknown entity"

    def _extract_aspects(self, queries: List[str], intent: str) -> List[Dict]:
        """
        Extract product/topic ASPECTS (not keywords!).

        For product queries, focus on:
        - Effectiveness, Ingredients, Safety, Price, Usage, etc.

        NOT: "strips", "dissolving" (those are parts of the entity!)
        """
        aspect_matches = defaultdict(set)

        for query in queries:
            query_lower = query.lower()

            # Match to predefined aspect categories
            for aspect_category, keywords in self.PRODUCT_ASPECTS.items():
                if any(kw in query_lower for kw in keywords):
                    # Extract the specific phrase mentioning this aspect
                    aspect_matches[aspect_category].add(query)

        # Build attribute list
        attributes = []
        for aspect, related_queries in aspect_matches.items():
            if len(related_queries) >= 2:  # Must appear in 2+ queries
                attributes.append({
                    'attribute': aspect,
                    'type': 'product_aspect',
                    'frequency': len(related_queries),
                    'sample_queries': list(related_queries)[:3]
                })

        # Sort by frequency
        attributes.sort(key=lambda x: x['frequency'], reverse=True)

        return attributes[:10]  # Top 10 aspects

    def _cluster_queries_semantically(self, queries: List[str]) -> Dict:
        """
        Cluster queries using embeddings to find semantic themes.
        """
        if not queries or not self.embedder:
            return {}

        # Embed queries
        embeddings = self.embedder.encode(queries)

        # Cluster using DBSCAN
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine').fit(embeddings)

        # Group queries by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(clustering.labels_):
            if label != -1:  # -1 = noise
                clusters[f"cluster_{label}"].append(queries[idx])

        # Extract theme from each cluster
        themed_clusters = {}
        for cluster_id, cluster_queries in clusters.items():
            # Use most common noun phrase as theme
            theme = self._extract_cluster_theme(cluster_queries)
            themed_clusters[theme] = cluster_queries

        return themed_clusters

    def _extract_cluster_theme(self, queries: List[str]) -> str:
        """Extract theme from a cluster of queries."""
        # Count common noun phrases
        noun_phrases = Counter()
        for query in queries:
            doc = self.nlp(query)
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:
                    noun_phrases[chunk.text.lower()] += 1

        if noun_phrases:
            return noun_phrases.most_common(1)[0][0]
        return "general"

    def _build_eav_structure(self, entity: str, attributes: List[Dict], clusters: Dict) -> Dict:
        """
        Build Entity-Attribute-Value structure (Koray's framework).

        NO tautologies, NO meaningless attributes.
        """
        eav = {
            'entity': entity,
            'attributes': []
        }

        for attr in attributes:
            attribute_name = attr['attribute']

            # Skip if attribute is substring of entity (tautology!)
            if attribute_name in entity or entity in attribute_name:
                continue

            # Build sub-attributes from sample queries
            sub_attributes = []
            for query in attr['sample_queries']:
                # Extract specific values mentioned
                sub_attr = self._extract_value_from_query(query, attribute_name)
                if sub_attr and sub_attr != attribute_name:
                    sub_attributes.append(sub_attr)

            eav['attributes'].append({
                'name': attribute_name,
                'type': attr['type'],
                'sub_attributes': list(set(sub_attributes))[:5],  # Top 5 unique
                'frequency': attr['frequency']
            })

        return eav

    def _extract_value_from_query(self, query: str, aspect: str) -> Optional[str]:
        """
        Extract specific value/detail mentioned in query.

        E.g., from "best strips for sensitive teeth" + aspect "safety"
        → value: "sensitive teeth"
        """
        doc = self.nlp(query.lower())

        # Look for noun phrases that aren't the aspect itself
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            if aspect not in chunk_text and len(chunk_text.split()) >= 2:
                return chunk_text

        return None


def extract_entity_context(query_report_text: str) -> Dict:
    """
    Main entry point - wrapper for backward compatibility.
    """
    extractor = SemanticExtractorV2()
    return extractor.extract_semantic_structure(query_report_text)
